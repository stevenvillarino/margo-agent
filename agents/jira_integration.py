"""
JIRA Integration for Design Review Automation

This module provides JIRA API integration for creating and managing tickets
related to design issues, accessibility concerns, and QA discrepancies.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import requests
from requests.auth import HTTPBasicAuth


@dataclass
class JIRAIssue:
    """JIRA issue representation."""
    key: Optional[str] = None
    summary: str = ""
    description: str = ""
    issue_type: str = "Task"
    priority: str = "Medium"
    assignee: Optional[str] = None
    reporter: Optional[str] = None
    labels: List[str] = None
    components: List[str] = None
    custom_fields: Dict[str, Any] = None
    attachments: List[str] = None


class JIRAIntegration:
    """
    JIRA API integration for design review workflow automation.
    """
    
    def __init__(self, 
                 jira_url: str,
                 username: str,
                 api_token: str,
                 project_key: str = "DESIGN"):
        """
        Initialize JIRA integration.
        
        Args:
            jira_url: JIRA instance URL (e.g., https://yourcompany.atlassian.net)
            username: JIRA username/email
            api_token: JIRA API token
            project_key: Default project key for created issues
        """
        self.jira_url = jira_url.rstrip('/')
        self.username = username
        self.api_token = api_token
        self.project_key = project_key
        
        self.auth = HTTPBasicAuth(username, api_token)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Validate connection
        self._validate_connection()
    
    def _validate_connection(self) -> bool:
        """Validate JIRA connection and permissions."""
        try:
            response = requests.get(
                f"{self.jira_url}/rest/api/3/myself",
                auth=self.auth,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            
            user_info = response.json()
            self.logger.info(f"JIRA connection validated for user: {user_info.get('displayName')}")
            return True
            
        except Exception as e:
            self.logger.error(f"JIRA connection failed: {e}")
            return False
    
    def create_design_issue(self, 
                           title: str,
                           description: str,
                           issue_type: str = "Task",
                           priority: str = "Medium",
                           assignee: Optional[str] = None,
                           labels: Optional[List[str]] = None,
                           design_file_url: Optional[str] = None,
                           workflow_id: Optional[str] = None) -> Optional[str]:
        """
        Create a JIRA issue for design review findings.
        
        Args:
            title: Issue title/summary
            description: Detailed description
            issue_type: JIRA issue type (Task, Bug, Story, etc.)
            priority: Issue priority (Low, Medium, High, Critical)
            assignee: Username of assignee
            labels: List of labels to add
            design_file_url: URL to design file
            workflow_id: Associated workflow ID
            
        Returns:
            JIRA issue key if successful, None otherwise
        """
        
        # Prepare labels
        issue_labels = labels or []
        issue_labels.extend(["design-review", "automated"])
        if workflow_id:
            issue_labels.append(f"workflow-{workflow_id}")
        
        # Enhanced description with design context
        enhanced_description = f"""
{description}

---
*This issue was automatically created by the Design Review Agent.*

"""
        
        if design_file_url:
            enhanced_description += f"""
**Design File:** {design_file_url}
"""
        
        if workflow_id:
            enhanced_description += f"""
**Workflow ID:** {workflow_id}
"""
        
        # Prepare issue data
        issue_data = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": title,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": enhanced_description
                                }
                            ]
                        }
                    ]
                },
                "issuetype": {"name": issue_type},
                "priority": {"name": priority},
                "labels": issue_labels
            }
        }
        
        # Add assignee if provided
        if assignee:
            issue_data["fields"]["assignee"] = {"accountId": assignee}
        
        try:
            response = requests.post(
                f"{self.jira_url}/rest/api/3/issue",
                auth=self.auth,
                headers=self.headers,
                data=json.dumps(issue_data),
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            issue_key = result.get("key")
            
            self.logger.info(f"Created JIRA issue: {issue_key}")
            
            # Add design file as attachment if provided
            if design_file_url and issue_key:
                self._add_attachment_link(issue_key, design_file_url, "Design File")
            
            return issue_key
            
        except Exception as e:
            self.logger.error(f"Failed to create JIRA issue: {e}")
            return None
    
    def create_accessibility_issue(self,
                                 violation_type: str,
                                 wcag_guideline: str,
                                 description: str,
                                 severity: str = "Medium",
                                 element_path: Optional[str] = None,
                                 screenshot_url: Optional[str] = None,
                                 workflow_id: Optional[str] = None) -> Optional[str]:
        """
        Create JIRA issue for accessibility violations.
        
        Args:
            violation_type: Type of accessibility violation
            wcag_guideline: Relevant WCAG guideline
            description: Detailed description of the violation
            severity: Issue severity
            element_path: CSS selector or element path
            screenshot_url: URL to screenshot showing the issue
            workflow_id: Associated workflow ID
            
        Returns:
            JIRA issue key if successful
        """
        
        title = f"Accessibility: {violation_type} - {wcag_guideline}"
        
        detailed_description = f"""
**Accessibility Violation Detected**

**Violation Type:** {violation_type}
**WCAG Guideline:** {wcag_guideline}
**Severity:** {severity}

**Description:**
{description}

"""
        
        if element_path:
            detailed_description += f"""
**Element Path:** `{element_path}`
"""
        
        if screenshot_url:
            detailed_description += f"""
**Screenshot:** {screenshot_url}
"""
        
        detailed_description += """
**Required Actions:**
1. Review WCAG guideline requirements
2. Implement necessary fixes
3. Test with screen readers
4. Validate compliance

**Testing Tools:**
- axe-core browser extension
- NVDA or JAWS screen reader
- Lighthouse accessibility audit
"""
        
        return self.create_design_issue(
            title=title,
            description=detailed_description,
            issue_type="Bug",
            priority=severity,
            labels=["accessibility", "wcag-compliance", "a11y"],
            workflow_id=workflow_id
        )
    
    def create_qa_discrepancy_issue(self,
                                   element_name: str,
                                   expected_behavior: str,
                                   actual_behavior: str,
                                   qa_url: str,
                                   design_spec_url: str,
                                   screenshot_url: Optional[str] = None,
                                   severity: str = "Medium",
                                   workflow_id: Optional[str] = None) -> Optional[str]:
        """
        Create JIRA issue for QA/Design spec discrepancies.
        
        Args:
            element_name: Name of the UI element with discrepancy
            expected_behavior: What was expected based on design spec
            actual_behavior: What was found in QA environment
            qa_url: URL to QA environment
            design_spec_url: URL to design specification
            screenshot_url: URL to screenshot showing discrepancy
            severity: Issue severity
            workflow_id: Associated workflow ID
            
        Returns:
            JIRA issue key if successful
        """
        
        title = f"Design Discrepancy: {element_name}"
        
        description = f"""
**Design Implementation Discrepancy Detected**

**Element:** {element_name}
**Severity:** {severity}

**Expected (Design Spec):**
{expected_behavior}

**Actual (QA Environment):**
{actual_behavior}

**Environment Details:**
- **QA URL:** {qa_url}
- **Design Spec:** {design_spec_url}

"""
        
        if screenshot_url:
            description += f"""
**Screenshot:** {screenshot_url}
"""
        
        description += """
**Action Items:**
1. Review design specification
2. Compare with current implementation
3. Update implementation to match design
4. Re-test in QA environment
5. Update design spec if needed

**Stakeholders:**
- Design Team: Review specification accuracy
- Development Team: Implement corrections
- QA Team: Verify fixes
"""
        
        return self.create_design_issue(
            title=title,
            description=description,
            issue_type="Bug",
            priority=severity,
            labels=["design-discrepancy", "qa-validation", "implementation"],
            design_file_url=design_spec_url,
            workflow_id=workflow_id
        )
    
    def create_research_request_issue(self,
                                    research_type: str,
                                    objectives: List[str],
                                    target_users: str,
                                    timeline: str,
                                    deliverables: List[str],
                                    priority: str = "Medium",
                                    workflow_id: Optional[str] = None) -> Optional[str]:
        """
        Create JIRA issue for research study requests.
        
        Args:
            research_type: Type of research (User Interview, Survey, etc.)
            objectives: Research objectives
            target_users: Target user description
            timeline: Expected timeline
            deliverables: Expected deliverables
            priority: Issue priority
            workflow_id: Associated workflow ID
            
        Returns:
            JIRA issue key if successful
        """
        
        title = f"Research Request: {research_type}"
        
        objectives_text = "\n".join([f"- {obj}" for obj in objectives])
        deliverables_text = "\n".join([f"- {deliv}" for deliv in deliverables])
        
        description = f"""
**Research Study Request**

**Research Type:** {research_type}
**Priority:** {priority}
**Timeline:** {timeline}

**Objectives:**
{objectives_text}

**Target Users:**
{target_users}

**Expected Deliverables:**
{deliverables_text}

**Next Steps:**
1. Review and approve research plan
2. Recruit participants
3. Conduct research sessions
4. Analyze findings
5. Present results and recommendations

*This research request was automatically generated based on design review findings.*
"""
        
        return self.create_design_issue(
            title=title,
            description=description,
            issue_type="Story",
            priority=priority,
            labels=["research-request", "user-research", "automated"],
            workflow_id=workflow_id
        )
    
    def _add_attachment_link(self, 
                           issue_key: str, 
                           url: str, 
                           link_title: str = "Related Link"):
        """Add a web link to a JIRA issue."""
        
        link_data = {
            "object": {
                "url": url,
                "title": link_title
            }
        }
        
        try:
            response = requests.post(
                f"{self.jira_url}/rest/api/3/issue/{issue_key}/remotelink",
                auth=self.auth,
                headers=self.headers,
                data=json.dumps(link_data),
                timeout=30
            )
            response.raise_for_status()
            self.logger.info(f"Added link to issue {issue_key}: {url}")
            
        except Exception as e:
            self.logger.warning(f"Failed to add link to issue {issue_key}: {e}")
    
    def update_issue_with_workflow_result(self,
                                        issue_key: str,
                                        workflow_result: Dict[str, Any]):
        """Update JIRA issue with workflow execution results."""
        
        comment = f"""
**Workflow Update - {datetime.now().strftime('%Y-%m-%d %H:%M')}**

**Status:** {workflow_result.get('status', 'Unknown')}
**Workflow ID:** {workflow_result.get('workflow_id', 'N/A')}

"""
        
        if workflow_result.get('next_steps'):
            next_steps = "\n".join([f"- {step}" for step in workflow_result['next_steps']])
            comment += f"""
**Next Steps:**
{next_steps}
"""
        
        if workflow_result.get('escalations'):
            escalations = "\n".join([f"- {esc}" for esc in workflow_result['escalations']])
            comment += f"""
**Escalations:**
{escalations}
"""
        
        comment_data = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": comment
                            }
                        ]
                    }
                ]
            }
        }
        
        try:
            response = requests.post(
                f"{self.jira_url}/rest/api/3/issue/{issue_key}/comment",
                auth=self.auth,
                headers=self.headers,
                data=json.dumps(comment_data),
                timeout=30
            )
            response.raise_for_status()
            self.logger.info(f"Updated issue {issue_key} with workflow results")
            
        except Exception as e:
            self.logger.error(f"Failed to update issue {issue_key}: {e}")
    
    def get_issue(self, issue_key: str) -> Optional[Dict[str, Any]]:
        """Get JIRA issue details."""
        try:
            response = requests.get(
                f"{self.jira_url}/rest/api/3/issue/{issue_key}",
                auth=self.auth,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            self.logger.error(f"Failed to get issue {issue_key}: {e}")
            return None
    
    def search_design_issues(self, 
                           workflow_id: Optional[str] = None,
                           labels: Optional[List[str]] = None,
                           max_results: int = 50) -> List[Dict[str, Any]]:
        """Search for design-related issues."""
        
        jql_parts = [f"project = {self.project_key}"]
        
        if workflow_id:
            jql_parts.append(f"labels = 'workflow-{workflow_id}'")
        
        if labels:
            label_conditions = " OR ".join([f"labels = '{label}'" for label in labels])
            jql_parts.append(f"({label_conditions})")
        
        jql = " AND ".join(jql_parts)
        
        try:
            response = requests.get(
                f"{self.jira_url}/rest/api/3/search",
                auth=self.auth,
                headers=self.headers,
                params={
                    "jql": jql,
                    "maxResults": max_results,
                    "fields": "summary,status,priority,assignee,created,updated"
                },
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("issues", [])
            
        except Exception as e:
            self.logger.error(f"Failed to search issues: {e}")
            return []


# Factory function for easy integration
def create_jira_integration(
    jira_url: Optional[str] = None,
    username: Optional[str] = None,
    api_token: Optional[str] = None,
    project_key: str = "DESIGN"
) -> Optional[JIRAIntegration]:
    """
    Create JIRA integration instance from environment variables or parameters.
    
    Args:
        jira_url: JIRA URL (or use JIRA_URL env var)
        username: JIRA username (or use JIRA_USERNAME env var)
        api_token: JIRA API token (or use JIRA_API_TOKEN env var)
        project_key: Project key for issues
        
    Returns:
        JIRAIntegration instance or None if configuration missing
    """
    
    jira_url = jira_url or os.getenv('JIRA_URL')
    username = username or os.getenv('JIRA_USERNAME')
    api_token = api_token or os.getenv('JIRA_API_TOKEN')
    
    if not all([jira_url, username, api_token]):
        logging.warning("JIRA configuration incomplete. Set JIRA_URL, JIRA_USERNAME, and JIRA_API_TOKEN environment variables.")
        return None
    
    try:
        return JIRAIntegration(
            jira_url=jira_url,
            username=username,
            api_token=api_token,
            project_key=project_key
        )
    except Exception as e:
        logging.error(f"Failed to create JIRA integration: {e}")
        return None


# Example usage
if __name__ == "__main__":
    import os
    
    # Create JIRA integration
    jira = create_jira_integration()
    
    if jira:
        print("✅ JIRA integration ready")
        
        # Example: Create design issue
        issue_key = jira.create_design_issue(
            title="Button color inconsistency in checkout flow",
            description="Primary button uses different blue shade than design system",
            issue_type="Bug",
            priority="Medium",
            labels=["design-system", "checkout"],
            design_file_url="https://figma.com/file/example"
        )
        
        if issue_key:
            print(f"✅ Created issue: {issue_key}")
    else:
        print("❌ JIRA integration not available")
