"""
VP Preference Management System
Allows VPs to customize evaluation criteria, add new requirements, and track rationale over time.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class DesignRule:
    """Individual design rule with context and rationale."""
    id: str
    title: str
    description: str
    rationale: str
    priority: int  # 1-5, 5 being highest
    category: str  # e.g., "navigation", "visual", "accessibility"
    created_by: str
    created_date: str
    last_modified: str
    examples: List[str]
    exceptions: List[str]
    tags: List[str]
    
@dataclass
class EvaluationMemory:
    """Memory of past evaluations for learning."""
    design_id: str
    evaluation_date: str
    input_type: str  # file, figma, confluence
    context: str
    issues_found: List[Dict[str, Any]]
    grade_assigned: str
    vp_feedback: Optional[str]
    vp_rating: Optional[int]  # 1-5 on accuracy
    follow_up_actions: List[str]
    
@dataclass
class VPProfile:
    """VP's personal preferences and evaluation style."""
    name: str
    role: str
    focus_areas: List[str]
    strict_areas: List[str]  # Areas where VP is particularly strict
    lenient_areas: List[str]  # Areas where VP is more flexible
    communication_style: str  # "detailed", "concise", "visual"
    typical_context_types: List[str]
    preferred_output_format: str

class VPPreferenceManager:
    """
    Manages VP preferences, custom rules, and learning from feedback.
    """
    
    def __init__(self, data_dir: str = "vp_preferences"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.rules_file = self.data_dir / "custom_rules.json"
        self.memory_file = self.data_dir / "evaluation_memory.json"
        self.profile_file = self.data_dir / "vp_profile.json"
        
        self.custom_rules: List[DesignRule] = []
        self.evaluation_memory: List[EvaluationMemory] = []
        self.vp_profile: Optional[VPProfile] = None
        
        self._load_data()
    
    def _load_data(self):
        """Load existing preferences and memory."""
        try:
            if self.rules_file.exists():
                with open(self.rules_file, 'r') as f:
                    rules_data = json.load(f)
                    self.custom_rules = [DesignRule(**rule) for rule in rules_data]
            
            if self.memory_file.exists():
                with open(self.memory_file, 'r') as f:
                    memory_data = json.load(f)
                    self.evaluation_memory = [EvaluationMemory(**mem) for mem in memory_data]
            
            if self.profile_file.exists():
                with open(self.profile_file, 'r') as f:
                    profile_data = json.load(f)
                    self.vp_profile = VPProfile(**profile_data)
                    
        except Exception as e:
            print(f"Error loading VP preferences: {e}")
    
    def _save_data(self):
        """Save preferences and memory to files."""
        try:
            with open(self.rules_file, 'w') as f:
                json.dump([asdict(rule) for rule in self.custom_rules], f, indent=2)
            
            with open(self.memory_file, 'w') as f:
                json.dump([asdict(mem) for mem in self.evaluation_memory], f, indent=2)
            
            if self.vp_profile:
                with open(self.profile_file, 'w') as f:
                    json.dump(asdict(self.vp_profile), f, indent=2)
                    
        except Exception as e:
            print(f"Error saving VP preferences: {e}")
    
    def add_custom_rule(
        self, 
        title: str, 
        description: str, 
        rationale: str,
        priority: int,
        category: str,
        created_by: str,
        examples: List[str] = None,
        exceptions: List[str] = None,
        tags: List[str] = None
    ) -> str:
        """Add a new custom design rule."""
        rule_id = f"custom_{len(self.custom_rules) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        rule = DesignRule(
            id=rule_id,
            title=title,
            description=description,
            rationale=rationale,
            priority=priority,
            category=category,
            created_by=created_by,
            created_date=datetime.now().isoformat(),
            last_modified=datetime.now().isoformat(),
            examples=examples or [],
            exceptions=exceptions or [],
            tags=tags or []
        )
        
        self.custom_rules.append(rule)
        self._save_data()
        return rule_id
    
    def update_rule(self, rule_id: str, **updates) -> bool:
        """Update an existing rule."""
        for rule in self.custom_rules:
            if rule.id == rule_id:
                for key, value in updates.items():
                    if hasattr(rule, key):
                        setattr(rule, key, value)
                rule.last_modified = datetime.now().isoformat()
                self._save_data()
                return True
        return False
    
    def get_rules_by_category(self, category: str) -> List[DesignRule]:
        """Get all rules in a specific category."""
        return [rule for rule in self.custom_rules if rule.category == category]
    
    def get_high_priority_rules(self, min_priority: int = 4) -> List[DesignRule]:
        """Get high-priority rules."""
        return [rule for rule in self.custom_rules if rule.priority >= min_priority]
    
    def record_evaluation_memory(
        self,
        design_id: str,
        input_type: str,
        context: str,
        issues_found: List[Dict[str, Any]],
        grade_assigned: str,
        vp_feedback: str = None,
        vp_rating: int = None
    ):
        """Record memory of an evaluation for learning."""
        memory = EvaluationMemory(
            design_id=design_id,
            evaluation_date=datetime.now().isoformat(),
            input_type=input_type,
            context=context,
            issues_found=issues_found,
            grade_assigned=grade_assigned,
            vp_feedback=vp_feedback,
            vp_rating=vp_rating,
            follow_up_actions=[]
        )
        
        self.evaluation_memory.append(memory)
        self._save_data()
    
    def get_learning_insights(self, context_type: str = None) -> Dict[str, Any]:
        """Analyze evaluation memory to provide learning insights."""
        relevant_memories = self.evaluation_memory
        
        if context_type:
            relevant_memories = [
                mem for mem in self.evaluation_memory 
                if context_type.lower() in mem.context.lower()
            ]
        
        if not relevant_memories:
            return {"message": "No evaluation history found"}
        
        # Analyze patterns
        common_issues = {}
        grade_distribution = {}
        avg_vp_rating = 0
        rated_evaluations = 0
        
        for memory in relevant_memories:
            # Count common issues
            for issue in memory.issues_found:
                issue_type = issue.get('type', 'unknown')
                common_issues[issue_type] = common_issues.get(issue_type, 0) + 1
            
            # Grade distribution
            grade = memory.grade_assigned
            grade_distribution[grade] = grade_distribution.get(grade, 0) + 1
            
            # VP ratings
            if memory.vp_rating:
                avg_vp_rating += memory.vp_rating
                rated_evaluations += 1
        
        avg_vp_rating = avg_vp_rating / rated_evaluations if rated_evaluations > 0 else 0
        
        return {
            "total_evaluations": len(relevant_memories),
            "most_common_issues": sorted(common_issues.items(), key=lambda x: x[1], reverse=True)[:5],
            "grade_distribution": grade_distribution,
            "average_vp_rating": round(avg_vp_rating, 2),
            "recent_feedback": [
                mem.vp_feedback for mem in relevant_memories[-3:] 
                if mem.vp_feedback
            ]
        }
    
    def generate_personalized_prompt_additions(self) -> str:
        """Generate additional prompt content based on VP's preferences and learning."""
        if not self.custom_rules:
            return ""
        
        # Get high-priority custom rules
        high_priority_rules = self.get_high_priority_rules()
        
        # Get learning insights
        insights = self.get_learning_insights()
        
        prompt_addition = "\n\nVP CUSTOM REQUIREMENTS:\n"
        
        # Add custom rules
        if high_priority_rules:
            prompt_addition += "Pay special attention to these VP-specific requirements:\n"
            for rule in high_priority_rules:
                prompt_addition += f"\n- **{rule.title}** (Priority {rule.priority}): {rule.description}"
                if rule.rationale:
                    prompt_addition += f"\n  Rationale: {rule.rationale}"
                if rule.examples:
                    prompt_addition += f"\n  Examples: {', '.join(rule.examples[:2])}"
        
        # Add learning insights
        if insights.get("most_common_issues"):
            prompt_addition += f"\n\nBASED ON PAST EVALUATIONS:"
            prompt_addition += f"\nThis VP frequently identifies these issue types: {', '.join([issue[0] for issue in insights['most_common_issues'][:3]])}"
            
        # Add communication style preferences
        if self.vp_profile:
            prompt_addition += f"\n\nCOMMUNICATION PREFERENCES:"
            prompt_addition += f"\n- Style: {self.vp_profile.communication_style}"
            prompt_addition += f"\n- Focus areas: {', '.join(self.vp_profile.focus_areas)}"
            if self.vp_profile.strict_areas:
                prompt_addition += f"\n- Be particularly strict about: {', '.join(self.vp_profile.strict_areas)}"
        
        return prompt_addition
    
    def update_vp_profile(
        self,
        name: str = None,
        role: str = None,
        focus_areas: List[str] = None,
        strict_areas: List[str] = None,
        lenient_areas: List[str] = None,
        communication_style: str = None
    ):
        """Update or create VP profile."""
        if not self.vp_profile:
            self.vp_profile = VPProfile(
                name=name or "VP",
                role=role or "Design Leadership",
                focus_areas=focus_areas or [],
                strict_areas=strict_areas or [],
                lenient_areas=lenient_areas or [],
                communication_style=communication_style or "detailed",
                typical_context_types=[],
                preferred_output_format="structured"
            )
        else:
            if name: self.vp_profile.name = name
            if role: self.vp_profile.role = role
            if focus_areas: self.vp_profile.focus_areas = focus_areas
            if strict_areas: self.vp_profile.strict_areas = strict_areas
            if lenient_areas: self.vp_profile.lenient_areas = lenient_areas
            if communication_style: self.vp_profile.communication_style = communication_style
        
        self._save_data()

# Global instance
vp_preference_manager = VPPreferenceManager()
