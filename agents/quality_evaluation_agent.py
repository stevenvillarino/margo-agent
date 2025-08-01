"""
Quality Evaluation Agent

This agent performs comprehensive quality evaluation by cross-referencing
feature guides, validating product requirements, checking research alignment,
and ensuring pain points are addressed according to design principles.
"""

import asyncio
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
from dataclasses import dataclass

from agents.orchestrator import ReviewResult
from agents.exa_search import ExaSearchAgent
from agents.confluence_utils import ConfluenceClient


@dataclass
class QualityCheckItem:
    """A quality check item with validation status."""
    check_type: str
    description: str
    status: str  # "pass", "fail", "warning", "not_applicable"
    details: str
    evidence: List[str]
    severity: str  # "critical", "high", "medium", "low"


@dataclass
class FeatureGuideValidation:
    """Feature guide validation result."""
    guide_name: str
    compliance_score: float
    missing_requirements: List[str]
    addressed_requirements: List[str]
    recommendations: List[str]


class QualityEvaluationAgent:
    """
    Quality evaluation agent that performs comprehensive validation against
    feature guides, product requirements, and design principles.
    """
    
    def __init__(self, 
                 openai_api_key: str,
                 confluence_config: Dict[str, str] = None,
                 exa_api_key: Optional[str] = None,
                 quality_standards: Dict[str, Any] = None):
        """
        Initialize the quality evaluation agent.
        
        Args:
            openai_api_key: OpenAI API key
            confluence_config: Confluence configuration for feature guide access
            exa_api_key: Optional Exa API key for research validation
            quality_standards: Custom quality standards and thresholds
        """
        self.llm = ChatOpenAI(
            model="gpt-4-turbo",
            temperature=0.1,  # Very low for consistent evaluation
            max_tokens=2500
        )
        
        # Initialize Confluence client for feature guide access
        self.confluence_client = None
        if confluence_config:
            try:
                self.confluence_client = ConfluenceClient(
                    url=confluence_config.get('url'),
                    username=confluence_config.get('username'),
                    api_key=confluence_config.get('api_key')
                )
            except Exception as e:
                print(f"Warning: Could not initialize Confluence client: {e}")
        
        # Initialize research capability
        self.exa_agent = None
        if exa_api_key:
            try:
                self.exa_agent = ExaSearchAgent(exa_api_key)
            except Exception as e:
                print(f"Warning: Could not initialize research capability: {e}")
        
        # Quality standards and thresholds
        self.quality_standards = quality_standards or {
            "minimum_compliance_score": 0.8,
            "critical_issue_threshold": 0,
            "high_issue_threshold": 2,
            "feature_guide_match_threshold": 0.7,
            "research_validation_threshold": 0.6,
            "pain_point_coverage_threshold": 0.8
        }
        
        # Roku-specific design principles
        self.roku_design_principles = [
            "Simple and intuitive navigation",
            "Fast content discovery",
            "Consistent visual language",
            "Accessibility for all users",
            "Remote control optimization",
            "Performance and responsiveness",
            "Brand consistency",
            "User personalization",
            "Cross-platform coherence"
        ]
        
        # Quality check categories
        self.quality_categories = [
            "Feature Guide Compliance",
            "Product Requirements Validation",
            "Research Alignment",
            "Pain Point Coverage",
            "Design Principles Adherence",
            "User Experience Quality",
            "Technical Feasibility",
            "Business Value Alignment"
        ]
        
        # Memory for quality patterns
        self.memory = ConversationBufferMemory(return_messages=True)
        self.review_history = []
        self.quality_patterns = {}
    
    async def async_review(self, 
                          image_data: str,
                          design_type: str,
                          context: Dict[str, Any],
                          analysis_results: List[ReviewResult]) -> List[ReviewResult]:
        """
        Conduct comprehensive quality evaluation.
        
        Args:
            image_data: Base64 encoded image data
            design_type: Type of design being reviewed
            context: Additional context including feature requirements
            analysis_results: Results from other agents
            
        Returns:
            Quality evaluation results
        """
        print(f"🔍 Starting quality evaluation for {design_type}")
        
        # Step 1: Retrieve and validate feature guides
        feature_validations = await self._validate_feature_guides(design_type, context)
        
        # Step 2: Cross-reference with product requirements
        product_validation = await self._validate_product_requirements(context, analysis_results)
        
        # Step 3: Validate research alignment
        research_validation = await self._validate_research_alignment(design_type, context)
        
        # Step 4: Check pain point coverage
        pain_point_coverage = await self._validate_pain_point_coverage(context, analysis_results)
        
        # Step 5: Evaluate design principles adherence
        principles_validation = await self._validate_design_principles(image_data, design_type)
        
        # Step 6: Perform comprehensive quality analysis
        quality_analysis = await self._perform_quality_analysis(
            image_data, design_type, feature_validations, product_validation,
            research_validation, pain_point_coverage, principles_validation
        )
        
        # Compile final quality evaluation
        review_result = self._compile_quality_review(
            quality_analysis, feature_validations, design_type, context
        )
        
        # Store for learning
        self.review_history.append(review_result)
        
        return [review_result]
    
    def review(self, 
               image_data: str,
               design_type: str,
               context: Dict[str, Any],
               analysis_results: List[ReviewResult]) -> List[ReviewResult]:
        """Synchronous version of review method."""
        return asyncio.run(self.async_review(image_data, design_type, context, analysis_results))
    
    async def _validate_feature_guides(self, design_type: str, context: Dict[str, Any]) -> List[FeatureGuideValidation]:
        """Validate design against relevant feature guides."""
        validations = []
        
        if not self.confluence_client:
            print("⚠️ Confluence not configured - skipping feature guide validation")
            return validations
        
        try:
            # Search for relevant feature guides
            search_terms = [
                f"{design_type} feature guide",
                f"Roku {design_type} requirements",
                f"{design_type} design spec",
                "UI guidelines",
                "design system"
            ]
            
            relevant_guides = []
            for term in search_terms:
                try:
                    results = self.confluence_client.search_content(term, limit=3)
                    relevant_guides.extend(results)
                except Exception as e:
                    print(f"Search failed for '{term}': {e}")
            
            # Validate against each guide
            for guide in relevant_guides[:5]:  # Limit to top 5 guides
                try:
                    guide_content = self.confluence_client.get_page_content(guide['id'])
                    validation = await self._validate_against_guide(guide, guide_content, context)
                    validations.append(validation)
                except Exception as e:
                    print(f"Guide validation failed: {e}")
            
        except Exception as e:
            print(f"Feature guide validation error: {e}")
        
        return validations
    
    async def _validate_against_guide(self, guide: Dict, guide_content: str, context: Dict[str, Any]) -> FeatureGuideValidation:
        """Validate design against a specific feature guide."""
        
        # Extract requirements from guide content
        requirements_prompt = f"""
        Extract specific requirements from this feature guide:
        
        Guide Title: {guide.get('title', 'Unknown')}
        Content: {guide_content[:2000]}...
        
        Extract:
        1. Must-have requirements
        2. Should-have requirements
        3. Design constraints
        4. User experience requirements
        
        Format as a structured list.
        """
        
        try:
            messages = [SystemMessage(content=requirements_prompt)]
            response = await self.llm.ainvoke(messages)
            extracted_requirements = response.content
            
            # Validate current design context against requirements
            validation_prompt = f"""
            Validate this design context against the extracted requirements:
            
            Design Context: {json.dumps(context, indent=2)}
            
            Requirements: {extracted_requirements}
            
            Provide:
            1. Compliance score (0-1)
            2. Missing requirements
            3. Addressed requirements
            4. Specific recommendations
            """
            
            validation_messages = [SystemMessage(content=validation_prompt)]
            validation_response = await self.llm.ainvoke(validation_messages)
            
            # Parse validation response (simplified)
            compliance_score = self._extract_compliance_score(validation_response.content)
            missing_reqs = self._extract_missing_requirements(validation_response.content)
            addressed_reqs = self._extract_addressed_requirements(validation_response.content)
            recommendations = self._extract_recommendations(validation_response.content)
            
            return FeatureGuideValidation(
                guide_name=guide.get('title', 'Unknown Guide'),
                compliance_score=compliance_score,
                missing_requirements=missing_reqs,
                addressed_requirements=addressed_reqs,
                recommendations=recommendations
            )
            
        except Exception as e:
            print(f"Guide validation error: {e}")
            return FeatureGuideValidation(
                guide_name=guide.get('title', 'Unknown Guide'),
                compliance_score=0.5,
                missing_requirements=["Validation failed"],
                addressed_requirements=[],
                recommendations=["Review guide manually"]
            )
    
    async def _validate_product_requirements(self, context: Dict[str, Any], analysis_results: List[ReviewResult]) -> Dict[str, Any]:
        """Validate against product requirements from context and other agent results."""
        
        # Extract product requirements from context
        product_reqs = context.get('product_requirements', [])
        business_goals = context.get('business_goals', [])
        user_needs = context.get('user_needs', [])
        
        # Extract insights from other agents
        agent_insights = []
        for result in analysis_results:
            if result.agent_type in ['vp_review', 'peer_review']:
                agent_insights.append({
                    'agent': result.agent_name,
                    'feedback': result.feedback[:500],  # Truncate for prompt
                    'score': result.score,
                    'issues': result.specific_issues[:3]
                })
        
        validation_prompt = f"""
        Validate design against product requirements:
        
        Product Requirements: {json.dumps(product_reqs, indent=2)}
        Business Goals: {json.dumps(business_goals, indent=2)}
        User Needs: {json.dumps(user_needs, indent=2)}
        
        Agent Insights: {json.dumps(agent_insights, indent=2)}
        
        Assess:
        1. Requirements coverage (0-1 score)
        2. Business goal alignment
        3. User need satisfaction
        4. Gap analysis
        5. Risk assessment
        
        Provide structured validation results.
        """
        
        try:
            messages = [SystemMessage(content=validation_prompt)]
            response = await self.llm.ainvoke(messages)
            
            return {
                'coverage_score': self._extract_score_from_response(response.content, 'coverage'),
                'alignment_score': self._extract_score_from_response(response.content, 'alignment'),
                'satisfaction_score': self._extract_score_from_response(response.content, 'satisfaction'),
                'gaps': self._extract_gaps_from_response(response.content),
                'risks': self._extract_risks_from_response(response.content),
                'validation_details': response.content
            }
            
        except Exception as e:
            print(f"Product requirements validation error: {e}")
            return {
                'coverage_score': 0.5,
                'alignment_score': 0.5,
                'satisfaction_score': 0.5,
                'gaps': ['Validation failed'],
                'risks': ['Unable to assess'],
                'validation_details': f"Error: {e}"
            }
    
    async def _validate_research_alignment(self, design_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate alignment with research findings and best practices."""
        
        if not self.exa_agent:
            return {'research_score': 0.5, 'details': 'Research validation not available'}
        
        try:
            # Get research context
            research_results = self.exa_agent.comprehensive_design_research(f"{design_type} best practices")
            
            # Extract research insights
            research_insights = []
            for category, documents in research_results.items():
                for doc in documents[:2]:  # Top 2 per category
                    if hasattr(doc, 'page_content') and doc.page_content:
                        research_insights.append({
                            'category': category,
                            'title': doc.metadata.get('title', 'Unknown'),
                            'content': doc.page_content[:300]
                        })
            
            # Validate against research
            validation_prompt = f"""
            Validate design against current research and best practices:
            
            Design Context: {json.dumps(context, indent=2)}
            
            Research Insights: {json.dumps(research_insights, indent=2)}
            
            Assess:
            1. Research alignment score (0-1)
            2. Best practice adherence
            3. Industry standard compliance
            4. Innovation vs. convention balance
            
            Provide detailed analysis.
            """
            
            messages = [SystemMessage(content=validation_prompt)]
            response = await self.llm.ainvoke(messages)
            
            return {
                'research_score': self._extract_score_from_response(response.content, 'research'),
                'best_practice_score': self._extract_score_from_response(response.content, 'practice'),
                'innovation_score': self._extract_score_from_response(response.content, 'innovation'),
                'research_insights': research_insights,
                'validation_details': response.content
            }
            
        except Exception as e:
            print(f"Research validation error: {e}")
            return {
                'research_score': 0.5,
                'details': f"Research validation failed: {e}"
            }
    
    async def _validate_pain_point_coverage(self, context: Dict[str, Any], analysis_results: List[ReviewResult]) -> Dict[str, Any]:
        """Validate that design addresses identified pain points."""
        
        # Extract pain points from context
        pain_points = context.get('pain_points', [])
        user_problems = context.get('user_problems', [])
        current_issues = context.get('current_issues', [])
        
        # Extract pain points mentioned by other agents
        agent_pain_points = []
        for result in analysis_results:
            for issue in result.specific_issues:
                if any(keyword in issue.lower() for keyword in ['pain', 'problem', 'issue', 'difficulty', 'frustration']):
                    agent_pain_points.append(issue)
        
        all_pain_points = pain_points + user_problems + current_issues + agent_pain_points
        
        if not all_pain_points:
            return {'coverage_score': 1.0, 'details': 'No pain points specified'}
        
        validation_prompt = f"""
        Assess how well this design addresses identified pain points:
        
        Identified Pain Points: {json.dumps(all_pain_points, indent=2)}
        
        Design Context: {json.dumps(context.get('design_features', {}), indent=2)}
        
        Agent Feedback Summary: {json.dumps([{
            'agent': r.agent_name,
            'recommendations': r.recommendations[:3]
        } for r in analysis_results], indent=2)}
        
        Evaluate:
        1. Pain point coverage score (0-1)
        2. Which pain points are addressed
        3. Which pain points are not addressed
        4. How effectively they are addressed
        5. Additional pain points that might be created
        
        Provide detailed analysis.
        """
        
        try:
            messages = [SystemMessage(content=validation_prompt)]
            response = await self.llm.ainvoke(messages)
            
            return {
                'coverage_score': self._extract_score_from_response(response.content, 'coverage'),
                'addressed_points': self._extract_addressed_points(response.content),
                'missed_points': self._extract_missed_points(response.content),
                'effectiveness_score': self._extract_score_from_response(response.content, 'effectiveness'),
                'new_pain_points': self._extract_new_pain_points(response.content),
                'validation_details': response.content
            }
            
        except Exception as e:
            print(f"Pain point validation error: {e}")
            return {
                'coverage_score': 0.5,
                'details': f"Pain point validation failed: {e}"
            }
    
    async def _validate_design_principles(self, image_data: str, design_type: str) -> Dict[str, Any]:
        """Validate adherence to Roku design principles."""
        
        principles_prompt = f"""
        Evaluate this {design_type} design against Roku design principles:
        
        Roku Design Principles:
        {chr(10).join([f"• {principle}" for principle in self.roku_design_principles])}
        
        For each principle, assess:
        1. Adherence level (0-1 score)
        2. Evidence of implementation
        3. Areas for improvement
        4. Specific recommendations
        
        Provide detailed principle-by-principle analysis.
        """
        
        try:
            messages = [
                SystemMessage(content=principles_prompt),
                HumanMessage(content=[
                    {"type": "text", "text": "Evaluate this design against Roku design principles."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                ])
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # Parse principle scores
            principle_scores = {}
            for principle in self.roku_design_principles:
                score = self._extract_principle_score(response.content, principle)
                principle_scores[principle] = score
            
            overall_score = sum(principle_scores.values()) / len(principle_scores)
            
            return {
                'overall_principles_score': overall_score,
                'principle_scores': principle_scores,
                'principles_analysis': response.content,
                'recommendations': self._extract_principle_recommendations(response.content)
            }
            
        except Exception as e:
            print(f"Design principles validation error: {e}")
            return {
                'overall_principles_score': 0.5,
                'details': f"Principles validation failed: {e}"
            }
    
    async def _perform_quality_analysis(self, 
                                      image_data: str,
                                      design_type: str,
                                      feature_validations: List[FeatureGuideValidation],
                                      product_validation: Dict[str, Any],
                                      research_validation: Dict[str, Any],
                                      pain_point_coverage: Dict[str, Any],
                                      principles_validation: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive quality analysis integrating all validations."""
        
        # Compile validation summary
        validation_summary = {
            'feature_guides': {
                'count': len(feature_validations),
                'avg_compliance': sum(v.compliance_score for v in feature_validations) / len(feature_validations) if feature_validations else 0,
                'guides': [v.guide_name for v in feature_validations]
            },
            'product_requirements': {
                'coverage_score': product_validation.get('coverage_score', 0),
                'alignment_score': product_validation.get('alignment_score', 0),
                'gaps': len(product_validation.get('gaps', []))
            },
            'research_alignment': {
                'research_score': research_validation.get('research_score', 0),
                'best_practice_score': research_validation.get('best_practice_score', 0)
            },
            'pain_point_coverage': {
                'coverage_score': pain_point_coverage.get('coverage_score', 0),
                'addressed_count': len(pain_point_coverage.get('addressed_points', [])),
                'missed_count': len(pain_point_coverage.get('missed_points', []))
            },
            'design_principles': {
                'overall_score': principles_validation.get('overall_principles_score', 0),
                'principle_count': len(principles_validation.get('principle_scores', {}))
            }
        }
        
        # Comprehensive quality assessment
        quality_prompt = f"""
        Perform comprehensive quality assessment based on all validations:
        
        Validation Summary: {json.dumps(validation_summary, indent=2)}
        
        Quality Standards:
        - Minimum compliance score: {self.quality_standards['minimum_compliance_score']}
        - Critical issue threshold: {self.quality_standards['critical_issue_threshold']}
        - Feature guide match threshold: {self.quality_standards['feature_guide_match_threshold']}
        
        Provide:
        1. Overall quality score (0-10)
        2. Quality grade (A, B, C, D, F)
        3. Critical quality issues
        4. Quality improvement recommendations
        5. Risk assessment for proceeding
        6. Compliance status for each category
        
        Be thorough and specific in your quality assessment.
        """
        
        try:
            messages = [
                SystemMessage(content=quality_prompt),
                HumanMessage(content=[
                    {"type": "text", "text": "Provide comprehensive quality assessment of this design."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                ])
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # Extract quality metrics
            quality_score = self._extract_quality_score(response.content)
            quality_grade = self._extract_quality_grade(response.content)
            critical_issues = self._extract_critical_issues(response.content)
            
            return {
                'overall_quality_score': quality_score,
                'quality_grade': quality_grade,
                'critical_issues': critical_issues,
                'validation_summary': validation_summary,
                'quality_analysis': response.content,
                'compliance_status': self._assess_compliance_status(validation_summary),
                'risk_level': self._assess_risk_level(quality_score, critical_issues)
            }
            
        except Exception as e:
            print(f"Quality analysis error: {e}")
            return {
                'overall_quality_score': 5.0,
                'quality_grade': 'C',
                'critical_issues': [f"Quality analysis failed: {e}"],
                'validation_summary': validation_summary,
                'risk_level': 'Medium'
            }
    
    def _compile_quality_review(self, 
                              quality_analysis: Dict[str, Any],
                              feature_validations: List[FeatureGuideValidation],
                              design_type: str,
                              context: Dict[str, Any]) -> ReviewResult:
        """Compile final quality evaluation review result."""
        
        # Create comprehensive feedback
        feedback_parts = [
            f"## Quality Evaluation Summary",
            f"Overall Quality Score: {quality_analysis['overall_quality_score']:.1f}/10",
            f"Quality Grade: {quality_analysis['quality_grade']}",
            f"Risk Level: {quality_analysis['risk_level']}",
            "",
            "## Validation Results"
        ]
        
        # Add feature guide validation
        if feature_validations:
            feedback_parts.append("### Feature Guide Compliance")
            for validation in feature_validations:
                feedback_parts.append(f"- {validation.guide_name}: {validation.compliance_score:.1%}")
                if validation.missing_requirements:
                    feedback_parts.append(f"  Missing: {', '.join(validation.missing_requirements[:3])}")
        
        # Add compliance status
        compliance_status = quality_analysis.get('compliance_status', {})
        feedback_parts.append("\n### Compliance Status")
        for category, status in compliance_status.items():
            feedback_parts.append(f"- {category}: {status}")
        
        # Add critical issues
        critical_issues = quality_analysis.get('critical_issues', [])
        if critical_issues:
            feedback_parts.append("\n### Critical Issues")
            for issue in critical_issues[:5]:
                feedback_parts.append(f"- {issue}")
        
        feedback = "\n".join(feedback_parts)
        
        # Extract specific issues and recommendations
        all_issues = critical_issues.copy()
        all_recommendations = []
        
        for validation in feature_validations:
            all_issues.extend(validation.missing_requirements)
            all_recommendations.extend(validation.recommendations)
        
        # Calculate confidence based on validation completeness
        confidence = self._calculate_quality_confidence(quality_analysis, feature_validations)
        
        return ReviewResult(
            agent_type="quality_evaluation",
            agent_name="Quality Evaluation Agent",
            score=quality_analysis['overall_quality_score'],
            feedback=feedback,
            specific_issues=all_issues[:8],  # Limit to prevent overflow
            recommendations=all_recommendations[:8],
            confidence=confidence,
            review_time=datetime.now(),
            metadata={
                'quality_grade': quality_analysis['quality_grade'],
                'risk_level': quality_analysis['risk_level'],
                'feature_guides_validated': len(feature_validations),
                'compliance_status': compliance_status,
                'validation_summary': quality_analysis.get('validation_summary', {}),
                'design_type': design_type,
                'confluence_enabled': bool(self.confluence_client),
                'research_enabled': bool(self.exa_agent)
            }
        )
    
    # Helper methods for parsing responses
    def _extract_compliance_score(self, response: str) -> float:
        """Extract compliance score from response."""
        patterns = [
            r'compliance.*?(\d+(?:\.\d+)?)',
            r'score.*?(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)%'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response.lower())
            if match:
                try:
                    score = float(match.group(1))
                    return score / 100 if score > 1 else score
                except:
                    continue
        
        return 0.5  # Default
    
    def _extract_missing_requirements(self, response: str) -> List[str]:
        """Extract missing requirements from response."""
        missing = []
        lines = response.split('\n')
        
        for line in lines:
            if 'missing' in line.lower() and ('requirement' in line.lower() or ':' in line):
                # Extract after colon or dash
                if ':' in line:
                    missing_text = line.split(':', 1)[1].strip()
                elif '-' in line:
                    missing_text = line.split('-', 1)[1].strip()
                else:
                    missing_text = line.strip()
                
                if missing_text and len(missing_text) > 5:
                    missing.append(missing_text)
        
        return missing[:5]  # Limit to prevent overflow
    
    def _extract_addressed_requirements(self, response: str) -> List[str]:
        """Extract addressed requirements from response."""
        addressed = []
        lines = response.split('\n')
        
        for line in lines:
            if ('addressed' in line.lower() or 'met' in line.lower()) and ('requirement' in line.lower() or ':' in line):
                if ':' in line:
                    addressed_text = line.split(':', 1)[1].strip()
                elif '-' in line:
                    addressed_text = line.split('-', 1)[1].strip()
                else:
                    addressed_text = line.strip()
                
                if addressed_text and len(addressed_text) > 5:
                    addressed.append(addressed_text)
        
        return addressed[:5]
    
    def _extract_recommendations(self, response: str) -> List[str]:
        """Extract recommendations from response."""
        recommendations = []
        lines = response.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['recommend', 'suggest', 'should', 'consider']):
                clean_line = re.sub(r'^[-•*]\s*|\d+\.\s*', '', line).strip()
                if clean_line and len(clean_line) > 10:
                    recommendations.append(clean_line)
        
        return recommendations[:5]
    
    def _extract_score_from_response(self, response: str, score_type: str) -> float:
        """Extract specific score type from response."""
        pattern = rf'{score_type}.*?(\d+(?:\.\d+)?)'
        match = re.search(pattern, response.lower())
        
        if match:
            try:
                score = float(match.group(1))
                return score / 10 if score > 1 else score
            except:
                pass
        
        return 0.5  # Default
    
    def _extract_quality_score(self, response: str) -> float:
        """Extract overall quality score from response."""
        patterns = [
            r'quality.*?(\d+(?:\.\d+)?)/10',
            r'overall.*?(\d+(?:\.\d+)?)/10',
            r'score.*?(\d+(?:\.\d+)?)/10'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response.lower())
            if match:
                try:
                    return float(match.group(1))
                except:
                    continue
        
        return 7.0  # Default
    
    def _extract_quality_grade(self, response: str) -> str:
        """Extract quality grade from response."""
        pattern = r'grade[:\s]*([A-F][+\-]?)'
        match = re.search(pattern, response, re.IGNORECASE)
        
        if match:
            return match.group(1).upper()
        
        return 'B'  # Default
    
    def _extract_critical_issues(self, response: str) -> List[str]:
        """Extract critical issues from response."""
        issues = []
        lines = response.split('\n')
        
        for line in lines:
            if 'critical' in line.lower() and ('issue' in line.lower() or 'problem' in line.lower()):
                clean_line = re.sub(r'^[-•*]\s*|\d+\.\s*', '', line).strip()
                if clean_line and len(clean_line) > 10:
                    issues.append(clean_line)
        
        return issues[:5]
    
    def _assess_compliance_status(self, validation_summary: Dict[str, Any]) -> Dict[str, str]:
        """Assess compliance status for each category."""
        status = {}
        
        # Feature guide compliance
        fg_score = validation_summary.get('feature_guides', {}).get('avg_compliance', 0)
        status['Feature Guides'] = 'Pass' if fg_score >= self.quality_standards['feature_guide_match_threshold'] else 'Fail'
        
        # Product requirements
        pr_score = validation_summary.get('product_requirements', {}).get('coverage_score', 0)
        status['Product Requirements'] = 'Pass' if pr_score >= 0.7 else 'Fail'
        
        # Research alignment
        ra_score = validation_summary.get('research_alignment', {}).get('research_score', 0)
        status['Research Alignment'] = 'Pass' if ra_score >= self.quality_standards['research_validation_threshold'] else 'Fail'
        
        # Pain point coverage
        pp_score = validation_summary.get('pain_point_coverage', {}).get('coverage_score', 0)
        status['Pain Point Coverage'] = 'Pass' if pp_score >= self.quality_standards['pain_point_coverage_threshold'] else 'Fail'
        
        # Design principles
        dp_score = validation_summary.get('design_principles', {}).get('overall_score', 0)
        status['Design Principles'] = 'Pass' if dp_score >= 0.7 else 'Fail'
        
        return status
    
    def _assess_risk_level(self, quality_score: float, critical_issues: List[str]) -> str:
        """Assess overall risk level."""
        if len(critical_issues) > 2 or quality_score < 5:
            return 'High'
        elif len(critical_issues) > 0 or quality_score < 7:
            return 'Medium'
        else:
            return 'Low'
    
    def _calculate_quality_confidence(self, quality_analysis: Dict[str, Any], feature_validations: List[FeatureGuideValidation]) -> float:
        """Calculate confidence in quality evaluation."""
        confidence_factors = []
        
        # Confluence integration factor
        if self.confluence_client:
            confidence_factors.append(0.9)
        else:
            confidence_factors.append(0.6)
        
        # Research integration factor
        if self.exa_agent:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.7)
        
        # Feature guide coverage factor
        if feature_validations:
            fg_factor = min(0.9, len(feature_validations) / 3)  # Normalize to 3 guides
            confidence_factors.append(fg_factor)
        else:
            confidence_factors.append(0.5)
        
        # Quality score factor
        quality_score = quality_analysis.get('overall_quality_score', 7)
        score_factor = min(0.9, quality_score / 10)
        confidence_factors.append(score_factor)
        
        return sum(confidence_factors) / len(confidence_factors)
    
    def _extract_gaps_from_response(self, response: str) -> List[str]:
        """Extract gaps from response."""
        return self._extract_list_items(response, ['gap', 'missing', 'lacking'])
    
    def _extract_risks_from_response(self, response: str) -> List[str]:
        """Extract risks from response."""
        return self._extract_list_items(response, ['risk', 'danger', 'concern'])
    
    def _extract_list_items(self, response: str, keywords: List[str]) -> List[str]:
        """Extract list items containing keywords."""
        items = []
        lines = response.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in keywords):
                clean_line = re.sub(r'^[-•*]\s*|\d+\.\s*', '', line).strip()
                if clean_line and len(clean_line) > 10:
                    items.append(clean_line)
        
        return items[:5]
    
    def _extract_principle_score(self, response: str, principle: str) -> float:
        """Extract score for specific principle."""
        # Look for principle name followed by score
        principle_lower = principle.lower()
        lines = response.split('\n')
        
        for line in lines:
            if principle_lower in line.lower():
                # Look for score pattern
                score_match = re.search(r'(\d+(?:\.\d+)?)', line)
                if score_match:
                    try:
                        score = float(score_match.group(1))
                        return score / 10 if score > 1 else score
                    except:
                        continue
        
        return 0.7  # Default score
    
    def _extract_principle_recommendations(self, response: str) -> List[str]:
        """Extract recommendations for principles."""
        return self._extract_recommendations(response)


# Example usage
if __name__ == "__main__":
    import os
    
    openai_key = os.getenv('OPENAI_API_KEY')
    exa_key = os.getenv('EXA_API_KEY')
    
    # Confluence configuration
    confluence_config = {
        'url': os.getenv('CONFLUENCE_URL'),
        'username': os.getenv('CONFLUENCE_USERNAME'),
        'api_key': os.getenv('CONFLUENCE_API_KEY')
    }
    
    if openai_key:
        quality_agent = QualityEvaluationAgent(
            openai_api_key=openai_key,
            confluence_config=confluence_config if all(confluence_config.values()) else None,
            exa_api_key=exa_key
        )
        
        print("✅ Quality Evaluation Agent created successfully")
        print(f"📚 Confluence integration: {'enabled' if quality_agent.confluence_client else 'disabled'}")
        print(f"🔍 Research capability: {'enabled' if quality_agent.exa_agent else 'disabled'}")
        print(f"📋 Quality categories: {len(quality_agent.quality_categories)}")
        print(f"🎯 Design principles: {len(quality_agent.roku_design_principles)}")
    else:
        print("❌ OPENAI_API_KEY required")
