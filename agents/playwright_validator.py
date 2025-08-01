"""
Playwright QA Validation Integration

This module provides Playwright automation for validating QA implementations
against design specifications, checking visual consistency, and detecting
design discrepancies automatically.
"""

import asyncio
import json
import logging
import os
import base64
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from urllib.parse import urljoin, urlparse
import aiofiles
import aiohttp

try:
    from playwright.async_api import async_playwright, Page, Browser, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️ Playwright not installed. Run: pip install playwright && playwright install")


@dataclass
class VisualDiscrepancy:
    """Visual discrepancy found during validation."""
    element_selector: str
    element_name: str
    expected_property: str
    expected_value: str
    actual_value: str
    discrepancy_type: str  # "color", "size", "spacing", "typography", etc.
    severity: str  # "low", "medium", "high", "critical"
    screenshot_path: Optional[str] = None
    coordinates: Optional[Dict[str, int]] = None


@dataclass
class AccessibilityIssue:
    """Accessibility issue found during validation."""
    rule_id: str
    rule_description: str
    element_selector: str
    severity: str  # "minor", "moderate", "serious", "critical"
    wcag_level: str  # "A", "AA", "AAA"
    wcag_guideline: str
    fix_suggestion: str


@dataclass
class ValidationResult:
    """Complete validation result."""
    validation_id: str
    qa_url: str
    design_spec_url: str
    timestamp: datetime
    visual_discrepancies: List[VisualDiscrepancy]
    accessibility_issues: List[AccessibilityIssue]
    overall_score: float
    status: str  # "passed", "failed", "warning"
    screenshots: Dict[str, str]  # viewport -> screenshot_path
    recommendations: List[str]


class PlaywrightQAValidator:
    """
    Playwright-based QA validation against design specifications.
    """
    
    def __init__(self, 
                 headless: bool = True,
                 viewport: Dict[str, int] = None,
                 screenshots_dir: str = "screenshots",
                 browser_type: str = "chromium"):
        """
        Initialize Playwright QA validator.
        
        Args:
            headless: Run browser in headless mode
            viewport: Browser viewport size
            screenshots_dir: Directory for screenshots
            browser_type: Browser type (chromium, firefox, webkit)
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright is not installed. Run: pip install playwright && playwright install")
        
        self.headless = headless
        self.viewport = viewport or {"width": 1920, "height": 1080}
        self.screenshots_dir = screenshots_dir
        self.browser_type = browser_type
        
        # Ensure screenshots directory exists
        os.makedirs(screenshots_dir, exist_ok=True)
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Design system tokens (would be loaded from actual design system)
        self.design_tokens = self._load_design_tokens()
    
    def _load_design_tokens(self) -> Dict[str, Any]:
        """Load design system tokens for validation."""
        # In practice, this would load from your design system
        return {
            "colors": {
                "primary": "#007AFF",
                "secondary": "#5856D6", 
                "success": "#34C759",
                "warning": "#FF9500",
                "error": "#FF3B30",
                "text_primary": "#000000",
                "text_secondary": "#6D6D70",
                "background": "#FFFFFF"
            },
            "typography": {
                "h1": {"font_size": "32px", "font_weight": "700", "line_height": "1.25"},
                "h2": {"font_size": "24px", "font_weight": "600", "line_height": "1.3"},
                "body": {"font_size": "16px", "font_weight": "400", "line_height": "1.5"},
                "caption": {"font_size": "12px", "font_weight": "400", "line_height": "1.4"}
            },
            "spacing": {
                "xs": "4px",
                "sm": "8px", 
                "md": "16px",
                "lg": "24px",
                "xl": "32px"
            },
            "components": {
                "button_primary": {
                    "height": "44px",
                    "border_radius": "8px",
                    "background_color": "#007AFF",
                    "color": "#FFFFFF",
                    "font_weight": "600"
                },
                "input": {
                    "height": "44px",
                    "border": "1px solid #E5E5EA",
                    "border_radius": "8px",
                    "padding": "12px 16px"
                }
            }
        }
    
    async def validate_qa_against_design(self,
                                       qa_url: str,
                                       design_spec: Dict[str, Any],
                                       validation_config: Dict[str, Any] = None) -> ValidationResult:
        """
        Validate QA implementation against design specification.
        
        Args:
            qa_url: URL of QA environment to validate
            design_spec: Design specification with expected elements and properties
            validation_config: Validation configuration options
            
        Returns:
            ValidationResult with all findings
        """
        
        validation_id = f"qa_val_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        config = validation_config or {}
        
        self.logger.info(f"Starting QA validation: {validation_id}")
        self.logger.info(f"QA URL: {qa_url}")
        
        async with async_playwright() as p:
            browser = await self._launch_browser(p)
            context = await browser.new_context(viewport=self.viewport)
            page = await context.new_page()
            
            try:
                # Navigate to QA page
                await page.goto(qa_url, wait_until="networkidle")
                await page.wait_for_timeout(2000)  # Allow for dynamic content
                
                # Take initial screenshot
                screenshot_path = await self._take_screenshot(page, validation_id, "initial")
                screenshots = {"desktop": screenshot_path}
                
                # Validate visual elements
                visual_discrepancies = await self._validate_visual_elements(
                    page, design_spec.get("elements", [])
                )
                
                # Check accessibility
                accessibility_issues = await self._check_accessibility(page)
                
                # Mobile validation if configured
                if config.get("include_mobile", False):
                    mobile_screenshot = await self._validate_mobile_view(page, validation_id)
                    screenshots["mobile"] = mobile_screenshot
                
                # Calculate overall score
                overall_score = self._calculate_validation_score(
                    visual_discrepancies, accessibility_issues
                )
                
                # Generate recommendations
                recommendations = self._generate_recommendations(
                    visual_discrepancies, accessibility_issues
                )
                
                # Determine status
                status = self._determine_validation_status(overall_score, visual_discrepancies)
                
                validation_result = ValidationResult(
                    validation_id=validation_id,
                    qa_url=qa_url,
                    design_spec_url=design_spec.get("spec_url", ""),
                    timestamp=datetime.now(),
                    visual_discrepancies=visual_discrepancies,
                    accessibility_issues=accessibility_issues,
                    overall_score=overall_score,
                    status=status,
                    screenshots=screenshots,
                    recommendations=recommendations
                )
                
                self.logger.info(f"Validation completed: {validation_id}")
                self.logger.info(f"Score: {overall_score:.1f}/10, Status: {status}")
                self.logger.info(f"Issues: {len(visual_discrepancies)} visual, {len(accessibility_issues)} a11y")
                
                return validation_result
                
            finally:
                await browser.close()
    
    async def _launch_browser(self, playwright) -> Browser:
        """Launch browser with appropriate configuration."""
        if self.browser_type == "chromium":
            return await playwright.chromium.launch(headless=self.headless)
        elif self.browser_type == "firefox":
            return await playwright.firefox.launch(headless=self.headless)
        elif self.browser_type == "webkit":
            return await playwright.webkit.launch(headless=self.headless)
        else:
            raise ValueError(f"Unsupported browser type: {self.browser_type}")
    
    async def _take_screenshot(self, page: Page, validation_id: str, suffix: str) -> str:
        """Take screenshot and return file path."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{validation_id}_{suffix}_{timestamp}.png"
        filepath = os.path.join(self.screenshots_dir, filename)
        
        await page.screenshot(path=filepath, full_page=True)
        self.logger.info(f"Screenshot saved: {filepath}")
        
        return filepath
    
    async def _validate_visual_elements(self,
                                      page: Page,
                                      expected_elements: List[Dict[str, Any]]) -> List[VisualDiscrepancy]:
        """Validate visual elements against design specification."""
        
        discrepancies = []
        
        for element_spec in expected_elements:
            selector = element_spec.get("selector")
            element_name = element_spec.get("name", selector)
            expected_props = element_spec.get("properties", {})
            
            if not selector:
                continue
            
            try:
                # Check if element exists
                element = page.locator(selector)
                if not await element.count():
                    discrepancies.append(VisualDiscrepancy(
                        element_selector=selector,
                        element_name=element_name,
                        expected_property="existence",
                        expected_value="present",
                        actual_value="missing",
                        discrepancy_type="missing_element",
                        severity="high"
                    ))
                    continue
                
                # Validate CSS properties
                for property_name, expected_value in expected_props.items():
                    actual_value = await self._get_computed_style(page, selector, property_name)
                    
                    if not self._values_match(expected_value, actual_value, property_name):
                        severity = self._assess_discrepancy_severity(property_name, expected_value, actual_value)
                        
                        discrepancies.append(VisualDiscrepancy(
                            element_selector=selector,
                            element_name=element_name,
                            expected_property=property_name,
                            expected_value=str(expected_value),
                            actual_value=str(actual_value),
                            discrepancy_type=self._classify_discrepancy_type(property_name),
                            severity=severity
                        ))
                
            except Exception as e:
                self.logger.warning(f"Error validating element {selector}: {e}")
        
        return discrepancies
    
    async def _get_computed_style(self, page: Page, selector: str, property_name: str) -> str:
        """Get computed CSS property value."""
        try:
            result = await page.evaluate(f"""
                () => {{
                    const element = document.querySelector('{selector}');
                    if (!element) return null;
                    return window.getComputedStyle(element).getPropertyValue('{property_name}');
                }}
            """)
            return result
        except:
            return ""
    
    def _values_match(self, expected: str, actual: str, property_name: str) -> bool:
        """Check if CSS values match, accounting for different formats."""
        
        if not expected or not actual:
            return False
        
        # Normalize values
        expected = str(expected).strip().lower()
        actual = str(actual).strip().lower()
        
        if expected == actual:
            return True
        
        # Handle color comparisons
        if property_name in ["color", "background-color", "border-color"]:
            return self._colors_match(expected, actual)
        
        # Handle size comparisons
        if property_name in ["width", "height", "font-size", "padding", "margin"]:
            return self._sizes_match(expected, actual)
        
        return False
    
    def _colors_match(self, expected: str, actual: str) -> bool:
        """Compare colors in different formats (hex, rgb, rgba)."""
        # Simple color matching - would be more sophisticated in practice
        # Convert both to hex for comparison
        try:
            expected_hex = self._to_hex_color(expected)
            actual_hex = self._to_hex_color(actual)
            return expected_hex == actual_hex
        except:
            return expected == actual
    
    def _sizes_match(self, expected: str, actual: str, tolerance: float = 2.0) -> bool:
        """Compare sizes with tolerance for rounding differences."""
        try:
            expected_px = self._to_pixels(expected)
            actual_px = self._to_pixels(actual)
            return abs(expected_px - actual_px) <= tolerance
        except:
            return expected == actual
    
    def _to_hex_color(self, color: str) -> str:
        """Convert color to hex format."""
        # Simplified conversion - would use proper color library
        if color.startswith('#'):
            return color
        # Would implement rgb/rgba to hex conversion
        return color
    
    def _to_pixels(self, size: str) -> float:
        """Convert size to pixels."""
        if size.endswith('px'):
            return float(size[:-2])
        elif size.endswith('rem'):
            return float(size[:-3]) * 16  # Assuming 16px = 1rem
        elif size.endswith('em'):
            return float(size[:-2]) * 16  # Simplified
        return 0.0
    
    def _assess_discrepancy_severity(self, property_name: str, expected: str, actual: str) -> str:
        """Assess severity of visual discrepancy."""
        
        critical_properties = ["visibility", "display", "position"]
        high_properties = ["color", "background-color", "font-size", "width", "height"]
        medium_properties = ["padding", "margin", "border", "font-weight"]
        
        if property_name in critical_properties:
            return "critical"
        elif property_name in high_properties:
            return "high"
        elif property_name in medium_properties:
            return "medium"
        else:
            return "low"
    
    def _classify_discrepancy_type(self, property_name: str) -> str:
        """Classify type of discrepancy."""
        
        type_mapping = {
            "color": "color",
            "background-color": "color", 
            "font-size": "typography",
            "font-weight": "typography",
            "font-family": "typography",
            "width": "size",
            "height": "size",
            "padding": "spacing",
            "margin": "spacing",
            "border": "border"
        }
        
        return type_mapping.get(property_name, "other")
    
    async def _check_accessibility(self, page: Page) -> List[AccessibilityIssue]:
        """Check accessibility using axe-core."""
        
        issues = []
        
        try:
            # Inject axe-core
            await page.add_script_tag(url="https://cdn.jsdelivr.net/npm/axe-core@4.7.2/axe.min.js")
            
            # Run axe audit
            results = await page.evaluate("""
                async () => {
                    try {
                        const results = await axe.run();
                        return results;
                    } catch (error) {
                        return { violations: [] };
                    }
                }
            """)
            
            # Process violations
            for violation in results.get("violations", []):
                for node in violation.get("nodes", []):
                    issue = AccessibilityIssue(
                        rule_id=violation.get("id", "unknown"),
                        rule_description=violation.get("description", ""),
                        element_selector=node.get("target", ["unknown"])[0],
                        severity=violation.get("impact", "moderate"),
                        wcag_level=self._extract_wcag_level(violation.get("tags", [])),
                        wcag_guideline=self._extract_wcag_guideline(violation.get("tags", [])),
                        fix_suggestion=node.get("failureSummary", "")
                    )
                    issues.append(issue)
        
        except Exception as e:
            self.logger.warning(f"Accessibility check failed: {e}")
        
        return issues
    
    def _extract_wcag_level(self, tags: List[str]) -> str:
        """Extract WCAG level from axe tags."""
        for tag in tags:
            if tag.startswith("wcag"):
                if "aaa" in tag:
                    return "AAA"
                elif "aa" in tag:
                    return "AA"
                elif "a" in tag:
                    return "A"
        return "AA"  # Default
    
    def _extract_wcag_guideline(self, tags: List[str]) -> str:
        """Extract WCAG guideline from axe tags."""
        for tag in tags:
            if tag.startswith("wcag") and any(char.isdigit() for char in tag):
                return tag
        return "unknown"
    
    async def _validate_mobile_view(self, page: Page, validation_id: str) -> str:
        """Validate mobile viewport."""
        
        # Switch to mobile viewport
        await page.set_viewport_size({"width": 375, "height": 667})
        await page.wait_for_timeout(1000)
        
        # Take mobile screenshot
        screenshot_path = await self._take_screenshot(page, validation_id, "mobile")
        
        # Switch back to desktop
        await page.set_viewport_size(self.viewport)
        
        return screenshot_path
    
    def _calculate_validation_score(self,
                                  visual_discrepancies: List[VisualDiscrepancy],
                                  accessibility_issues: List[AccessibilityIssue]) -> float:
        """Calculate overall validation score."""
        
        base_score = 10.0
        
        # Deduct points for visual discrepancies
        for discrepancy in visual_discrepancies:
            severity_penalties = {
                "critical": 3.0,
                "high": 2.0,
                "medium": 1.0,
                "low": 0.5
            }
            base_score -= severity_penalties.get(discrepancy.severity, 0.5)
        
        # Deduct points for accessibility issues
        for issue in accessibility_issues:
            severity_penalties = {
                "critical": 2.5,
                "serious": 2.0,
                "moderate": 1.0,
                "minor": 0.5
            }
            base_score -= severity_penalties.get(issue.severity, 0.5)
        
        return max(0.0, min(10.0, base_score))
    
    def _determine_validation_status(self,
                                   score: float,
                                   visual_discrepancies: List[VisualDiscrepancy]) -> str:
        """Determine validation status based on score and issues."""
        
        critical_issues = [d for d in visual_discrepancies if d.severity == "critical"]
        
        if critical_issues or score < 5.0:
            return "failed"
        elif score < 7.0:
            return "warning"
        else:
            return "passed"
    
    def _generate_recommendations(self,
                                visual_discrepancies: List[VisualDiscrepancy],
                                accessibility_issues: List[AccessibilityIssue]) -> List[str]:
        """Generate recommendations based on findings."""
        
        recommendations = []
        
        # Visual discrepancy recommendations
        color_issues = [d for d in visual_discrepancies if d.discrepancy_type == "color"]
        if color_issues:
            recommendations.append("Update color values to match design system tokens")
        
        typography_issues = [d for d in visual_discrepancies if d.discrepancy_type == "typography"]
        if typography_issues:
            recommendations.append("Correct typography sizes and weights according to design spec")
        
        spacing_issues = [d for d in visual_discrepancies if d.discrepancy_type == "spacing"]
        if spacing_issues:
            recommendations.append("Adjust spacing values to match design specifications")
        
        # Accessibility recommendations
        if accessibility_issues:
            recommendations.append("Address accessibility violations to meet WCAG compliance")
            
            critical_a11y = [i for i in accessibility_issues if i.severity in ["critical", "serious"]]
            if critical_a11y:
                recommendations.append("Prioritize critical accessibility issues for immediate resolution")
        
        # General recommendations
        if not recommendations:
            recommendations.append("Implementation matches design specification - ready for production")
        
        return recommendations


# Factory function for easy integration
def create_playwright_validator(
    headless: bool = True,
    viewport: Dict[str, int] = None,
    screenshots_dir: str = "screenshots",
    browser_type: str = "chromium"
) -> Optional[PlaywrightQAValidator]:
    """
    Create Playwright QA validator instance.
    
    Args:
        headless: Run browser in headless mode
        viewport: Browser viewport size
        screenshots_dir: Directory for screenshots  
        browser_type: Browser type
        
    Returns:
        PlaywrightQAValidator instance or None if Playwright not available
    """
    
    if not PLAYWRIGHT_AVAILABLE:
        return None
    
    try:
        return PlaywrightQAValidator(
            headless=headless,
            viewport=viewport,
            screenshots_dir=screenshots_dir,
            browser_type=browser_type
        )
    except Exception as e:
        logging.error(f"Failed to create Playwright validator: {e}")
        return None


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        validator = create_playwright_validator()
        
        if validator:
            print("✅ Playwright QA Validator ready")
            
            # Example validation
            design_spec = {
                "spec_url": "https://figma.com/file/example",
                "elements": [
                    {
                        "name": "Primary Button",
                        "selector": ".btn-primary",
                        "properties": {
                            "background-color": "#007AFF",
                            "height": "44px",
                            "border-radius": "8px"
                        }
                    },
                    {
                        "name": "Page Title",
                        "selector": "h1",
                        "properties": {
                            "font-size": "32px",
                            "font-weight": "700"
                        }
                    }
                ]
            }
            
            # result = await validator.validate_qa_against_design(
            #     qa_url="https://qa.yourapp.com/checkout",
            #     design_spec=design_spec
            # )
            
            # print(f"Validation score: {result.overall_score:.1f}/10")
            # print(f"Status: {result.status}")
        else:
            print("❌ Playwright not available")
    
    if PLAYWRIGHT_AVAILABLE:
        asyncio.run(main())
