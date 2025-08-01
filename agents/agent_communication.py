"""
Inter-Agent Communication System

This module provides advanced communication capabilities between all agents
in the design review system, enabling knowledge sharing, escalation, and
collaborative decision making.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from collections import defaultdict


class MessageType(Enum):
    """Types of inter-agent messages."""
    KNOWLEDGE_REQUEST = "knowledge_request"
    KNOWLEDGE_RESPONSE = "knowledge_response"
    ESCALATION = "escalation"
    CONSULTATION = "consultation"
    COLLABORATION = "collaboration"
    NOTIFICATION = "notification"
    STATUS_UPDATE = "status_update"
    RESEARCH_REQUEST = "research_request"
    RESEARCH_RESULTS = "research_results"


class Priority(Enum):
    """Message priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


@dataclass
class AgentMessage:
    """Message between agents."""
    message_id: str
    sender: str
    recipient: str
    message_type: MessageType
    priority: Priority
    subject: str
    content: Dict[str, Any]
    timestamp: datetime
    requires_response: bool = False
    parent_message_id: Optional[str] = None
    workflow_id: Optional[str] = None
    expires_at: Optional[datetime] = None


@dataclass
class AgentCapability:
    """Agent capability description."""
    agent_id: str
    agent_name: str
    agent_type: str
    expertise_areas: List[str]
    available_methods: List[str]
    current_load: int  # 0-100 percentage
    response_time_avg: float  # average response time in seconds
    reliability_score: float  # 0-1 reliability rating


@dataclass
class ConversationThread:
    """Thread of messages between agents."""
    thread_id: str
    participants: List[str]
    subject: str
    messages: List[AgentMessage]
    status: str  # "active", "resolved", "escalated"
    created_at: datetime
    updated_at: datetime
    workflow_id: Optional[str] = None


class AgentCommunicationHub:
    """
    Central hub for inter-agent communication and coordination.
    """
    
    def __init__(self):
        """Initialize the communication hub."""
        
        # Message routing and storage
        self.messages: Dict[str, AgentMessage] = {}
        self.threads: Dict[str, ConversationThread] = {}
        self.agent_capabilities: Dict[str, AgentCapability] = {}
        
        # Message queues for each agent
        self.message_queues: Dict[str, List[AgentMessage]] = defaultdict(list)
        
        # Message handlers
        self.message_handlers: Dict[str, Dict[MessageType, Callable]] = defaultdict(dict)
        
        # Agent status tracking
        self.agent_status: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # Knowledge base for sharing insights
        self.shared_knowledge: Dict[str, Any] = defaultdict(dict)
        
        # Escalation rules
        self.escalation_rules: Dict[str, Dict[str, Any]] = {}
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize built-in handlers
        self._setup_default_handlers()
    
    def register_agent(self, 
                      agent_id: str,
                      capability: AgentCapability,
                      message_handlers: Dict[MessageType, Callable] = None):
        """
        Register an agent with the communication hub.
        
        Args:
            agent_id: Unique agent identifier
            capability: Agent capability description
            message_handlers: Message type handlers for this agent
        """
        
        self.agent_capabilities[agent_id] = capability
        self.agent_status[agent_id] = {
            "status": "online",
            "last_seen": datetime.now(),
            "current_tasks": [],
            "message_count": 0
        }
        
        if message_handlers:
            self.message_handlers[agent_id] = message_handlers
        
        self.logger.info(f"Registered agent: {agent_id} ({capability.agent_name})")
    
    async def send_message(self, 
                          sender: str,
                          recipient: str,
                          message_type: MessageType,
                          subject: str,
                          content: Dict[str, Any],
                          priority: Priority = Priority.MEDIUM,
                          requires_response: bool = False,
                          workflow_id: Optional[str] = None,
                          expires_in_hours: Optional[int] = None) -> str:
        """
        Send a message from one agent to another.
        
        Args:
            sender: Sender agent ID
            recipient: Recipient agent ID  
            message_type: Type of message
            subject: Message subject
            content: Message content
            priority: Message priority
            requires_response: Whether response is required
            workflow_id: Associated workflow ID
            expires_in_hours: Message expiration time
            
        Returns:
            Message ID
        """
        
        message_id = f"msg_{uuid.uuid4().hex[:8]}"
        expires_at = None
        if expires_in_hours:
            expires_at = datetime.now() + timedelta(hours=expires_in_hours)
        
        message = AgentMessage(
            message_id=message_id,
            sender=sender,
            recipient=recipient,
            message_type=message_type,
            priority=priority,
            subject=subject,
            content=content,
            timestamp=datetime.now(),
            requires_response=requires_response,
            workflow_id=workflow_id,
            expires_at=expires_at
        )
        
        # Store message
        self.messages[message_id] = message
        
        # Add to recipient's queue
        self.message_queues[recipient].append(message)
        
        # Sort queue by priority
        self.message_queues[recipient].sort(key=lambda m: m.priority.value, reverse=True)
        
        # Handle message delivery
        await self._deliver_message(message)
        
        # Update sender stats
        self.agent_status[sender]["message_count"] += 1
        
        self.logger.info(f"Message sent: {sender} -> {recipient} ({message_type.value})")
        
        return message_id
    
    async def _deliver_message(self, message: AgentMessage):
        """Deliver message to recipient agent."""
        
        recipient = message.recipient
        
        # Check if agent has specific handler for this message type
        if recipient in self.message_handlers:
            handler = self.message_handlers[recipient].get(message.message_type)
            if handler:
                try:
                    await handler(message)
                except Exception as e:
                    self.logger.error(f"Message handler failed: {e}")
        
        # Update thread if applicable
        await self._update_conversation_thread(message)
    
    async def _update_conversation_thread(self, message: AgentMessage):
        """Update or create conversation thread."""
        
        # Find existing thread or create new one
        thread_id = None
        
        if message.parent_message_id:
            # Find thread containing parent message
            for tid, thread in self.threads.items():
                if any(m.message_id == message.parent_message_id for m in thread.messages):
                    thread_id = tid
                    break
        
        if not thread_id:
            # Create new thread
            thread_id = f"thread_{uuid.uuid4().hex[:8]}"
            self.threads[thread_id] = ConversationThread(
                thread_id=thread_id,
                participants=[message.sender, message.recipient],
                subject=message.subject,
                messages=[],
                status="active",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                workflow_id=message.workflow_id
            )
        
        # Add message to thread
        thread = self.threads[thread_id]
        thread.messages.append(message)
        thread.updated_at = datetime.now()
        
        # Update participants
        if message.sender not in thread.participants:
            thread.participants.append(message.sender)
        if message.recipient not in thread.participants:
            thread.participants.append(message.recipient)
    
    async def request_knowledge(self,
                              requester: str,
                              topic: str,
                              specific_question: str,
                              context: Dict[str, Any] = None,
                              urgency: Priority = Priority.MEDIUM) -> str:
        """
        Request knowledge from appropriate expert agents.
        
        Args:
            requester: Agent requesting knowledge
            topic: Knowledge topic
            specific_question: Specific question
            context: Additional context
            urgency: Request urgency
            
        Returns:
            Request message ID
        """
        
        # Find expert agents for this topic
        expert_agents = self._find_topic_experts(topic)
        
        if not expert_agents:
            self.logger.warning(f"No experts found for topic: {topic}")
            return None
        
        # Select best expert based on availability and expertise
        best_expert = self._select_best_expert(expert_agents, topic)
        
        content = {
            "topic": topic,
            "question": specific_question,
            "context": context or {},
            "requester_capability": self.agent_capabilities.get(requester, {})
        }
        
        message_id = await self.send_message(
            sender=requester,
            recipient=best_expert,
            message_type=MessageType.KNOWLEDGE_REQUEST,
            subject=f"Knowledge request: {topic}",
            content=content,
            priority=urgency,
            requires_response=True,
            expires_in_hours=24
        )
        
        self.logger.info(f"Knowledge request sent: {requester} -> {best_expert} ({topic})")
        
        return message_id
    
    async def provide_knowledge_response(self,
                                       responder: str,
                                       original_message_id: str,
                                       knowledge: Dict[str, Any],
                                       confidence: float,
                                       sources: List[str] = None,
                                       follow_up_suggestions: List[str] = None) -> str:
        """
        Provide knowledge response to a previous request.
        
        Args:
            responder: Agent providing the response
            original_message_id: ID of original knowledge request
            knowledge: Knowledge content
            confidence: Confidence level (0-1)
            sources: Knowledge sources
            follow_up_suggestions: Suggested follow-up actions
            
        Returns:
            Response message ID
        """
        
        original_message = self.messages.get(original_message_id)
        if not original_message:
            self.logger.error(f"Original message not found: {original_message_id}")
            return None
        
        content = {
            "knowledge": knowledge,
            "confidence": confidence,
            "sources": sources or [],
            "follow_up_suggestions": follow_up_suggestions or [],
            "responder_expertise": self.agent_capabilities.get(responder, {})
        }
        
        response_id = await self.send_message(
            sender=responder,
            recipient=original_message.sender,
            message_type=MessageType.KNOWLEDGE_RESPONSE,
            subject=f"Re: {original_message.subject}",
            content=content,
            priority=original_message.priority,
            parent_message_id=original_message_id,
            workflow_id=original_message.workflow_id
        )
        
        # Store knowledge in shared knowledge base
        topic = original_message.content.get("topic", "general")
        self._store_shared_knowledge(topic, knowledge, responder, confidence)
        
        return response_id
    
    async def escalate_issue(self,
                           escalator: str,
                           issue: Dict[str, Any],
                           escalation_reason: str,
                           suggested_actions: List[str] = None,
                           workflow_id: Optional[str] = None) -> str:
        """
        Escalate an issue to appropriate authority.
        
        Args:
            escalator: Agent escalating the issue
            issue: Issue details
            escalation_reason: Reason for escalation
            suggested_actions: Suggested actions
            workflow_id: Associated workflow ID
            
        Returns:
            Escalation message ID
        """
        
        # Determine escalation target based on issue type
        escalation_target = self._determine_escalation_target(issue, escalator)
        
        content = {
            "issue": issue,
            "escalation_reason": escalation_reason,
            "suggested_actions": suggested_actions or [],
            "escalator_assessment": self._get_agent_assessment(escalator, issue),
            "urgency_level": self._assess_escalation_urgency(issue)
        }
        
        escalation_id = await self.send_message(
            sender=escalator,
            recipient=escalation_target,
            message_type=MessageType.ESCALATION,
            subject=f"Escalation: {issue.get('title', 'Issue requiring attention')}",
            content=content,
            priority=Priority.HIGH,
            requires_response=True,
            workflow_id=workflow_id,
            expires_in_hours=4  # Escalations should be handled quickly
        )
        
        self.logger.warning(f"Issue escalated: {escalator} -> {escalation_target}")
        
        return escalation_id
    
    async def request_collaboration(self,
                                  initiator: str,
                                  collaborators: List[str],
                                  task: Dict[str, Any],
                                  coordination_mode: str = "parallel",
                                  workflow_id: Optional[str] = None) -> str:
        """
        Request collaboration from multiple agents.
        
        Args:
            initiator: Agent initiating collaboration
            collaborators: List of collaborating agents
            task: Task details requiring collaboration
            coordination_mode: "parallel" or "sequential"
            workflow_id: Associated workflow ID
            
        Returns:
            Collaboration thread ID
        """
        
        thread_id = f"collab_{uuid.uuid4().hex[:8]}"
        
        content = {
            "task": task,
            "coordination_mode": coordination_mode,
            "collaboration_id": thread_id,
            "expected_deliverables": task.get("deliverables", []),
            "timeline": task.get("timeline", {})
        }
        
        # Send collaboration request to all participants
        for collaborator in collaborators:
            await self.send_message(
                sender=initiator,
                recipient=collaborator,
                message_type=MessageType.COLLABORATION,
                subject=f"Collaboration Request: {task.get('title', 'Joint Task')}",
                content=content,
                priority=Priority.MEDIUM,
                requires_response=True,
                workflow_id=workflow_id
            )
        
        self.logger.info(f"Collaboration requested: {initiator} -> {collaborators}")
        
        return thread_id
    
    async def request_research(self,
                             requester: str,
                             research_query: str,
                             research_type: str = "web_search",
                             context: Dict[str, Any] = None,
                             urgency: Priority = Priority.MEDIUM,
                             workflow_id: Optional[str] = None) -> str:
        """
        Request research from research-capable agents.
        
        Args:
            requester: Agent requesting research
            research_query: Research query or topic
            research_type: Type of research needed
            context: Research context
            urgency: Request urgency
            workflow_id: Associated workflow ID
            
        Returns:
            Research request message ID
        """
        
        # Find agents capable of research
        research_agents = self._find_research_agents(research_type)
        
        if not research_agents:
            self.logger.warning(f"No research agents available for type: {research_type}")
            return None
        
        # Select best research agent
        best_researcher = self._select_best_researcher(research_agents)
        
        content = {
            "research_query": research_query,
            "research_type": research_type,
            "context": context or {},
            "expected_depth": "comprehensive" if urgency == Priority.HIGH else "standard",
            "format_requirements": {
                "summary": True,
                "sources": True,
                "key_insights": True,
                "actionable_recommendations": True
            }
        }
        
        request_id = await self.send_message(
            sender=requester,
            recipient=best_researcher,
            message_type=MessageType.RESEARCH_REQUEST,
            subject=f"Research Request: {research_query[:50]}...",
            content=content,
            priority=urgency,
            requires_response=True,
            workflow_id=workflow_id,
            expires_in_hours=12
        )
        
        return request_id
    
    def get_agent_messages(self, agent_id: str, limit: int = 50) -> List[AgentMessage]:
        """Get messages for an agent."""
        messages = self.message_queues.get(agent_id, [])
        return messages[-limit:] if limit else messages
    
    def get_conversation_thread(self, thread_id: str) -> Optional[ConversationThread]:
        """Get conversation thread by ID."""
        return self.threads.get(thread_id)
    
    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Get agent status information."""
        return self.agent_status.get(agent_id, {})
    
    def get_shared_knowledge(self, topic: str) -> Dict[str, Any]:
        """Get shared knowledge for a topic."""
        return self.shared_knowledge.get(topic, {})
    
    def _find_topic_experts(self, topic: str) -> List[str]:
        """Find agents with expertise in a topic."""
        experts = []
        
        for agent_id, capability in self.agent_capabilities.items():
            if topic.lower() in [area.lower() for area in capability.expertise_areas]:
                experts.append(agent_id)
        
        return experts
    
    def _select_best_expert(self, expert_agents: List[str], topic: str) -> str:
        """Select the best expert based on availability and reliability."""
        if not expert_agents:
            return None
        
        best_expert = None
        best_score = -1
        
        for agent_id in expert_agents:
            capability = self.agent_capabilities[agent_id]
            status = self.agent_status[agent_id]
            
            # Calculate selection score
            availability_score = 1.0 - (capability.current_load / 100.0)
            reliability_score = capability.reliability_score
            response_score = 1.0 / (1.0 + capability.response_time_avg / 60.0)  # Prefer faster agents
            
            total_score = (availability_score * 0.4 + 
                          reliability_score * 0.4 + 
                          response_score * 0.2)
            
            if total_score > best_score:
                best_score = total_score
                best_expert = agent_id
        
        return best_expert
    
    def _find_research_agents(self, research_type: str) -> List[str]:
        """Find agents capable of research."""
        researchers = []
        
        for agent_id, capability in self.agent_capabilities.items():
            if "research" in capability.expertise_areas or "web_search" in capability.available_methods:
                researchers.append(agent_id)
        
        return researchers
    
    def _select_best_researcher(self, research_agents: List[str]) -> str:
        """Select best research agent."""
        # For now, select first available. Could be more sophisticated.
        return research_agents[0] if research_agents else None
    
    def _determine_escalation_target(self, issue: Dict[str, Any], escalator: str) -> str:
        """Determine appropriate escalation target."""
        
        issue_type = issue.get("type", "general")
        severity = issue.get("severity", "medium")
        
        # Define escalation hierarchy
        escalation_map = {
            "accessibility": "accessibility_lead",
            "design_system": "design_lead", 
            "strategy": "vp_product",
            "technical": "engineering_lead",
            "user_research": "research_lead",
            "general": "margo_agent"
        }
        
        target = escalation_map.get(issue_type, "margo_agent")
        
        # For critical issues, escalate to VP level
        if severity == "critical":
            target = "vp_product"
        
        return target
    
    def _get_agent_assessment(self, agent_id: str, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Get agent's assessment of the issue."""
        capability = self.agent_capabilities.get(agent_id, {})
        
        return {
            "agent_expertise": capability.expertise_areas if hasattr(capability, 'expertise_areas') else [],
            "confidence_in_assessment": 0.8,  # Would be calculated
            "recommended_priority": issue.get("severity", "medium")
        }
    
    def _assess_escalation_urgency(self, issue: Dict[str, Any]) -> str:
        """Assess urgency of escalation."""
        severity = issue.get("severity", "medium")
        impact = issue.get("impact", "medium")
        
        if severity == "critical" or impact == "critical":
            return "immediate"
        elif severity == "high" or impact == "high":
            return "urgent"
        else:
            return "standard"
    
    def _store_shared_knowledge(self,
                              topic: str,
                              knowledge: Dict[str, Any],
                              contributor: str,
                              confidence: float):
        """Store knowledge in shared knowledge base."""
        
        if topic not in self.shared_knowledge:
            self.shared_knowledge[topic] = {
                "contributions": [],
                "consensus": {},
                "last_updated": datetime.now()
            }
        
        contribution = {
            "contributor": contributor,
            "knowledge": knowledge,
            "confidence": confidence,
            "timestamp": datetime.now()
        }
        
        self.shared_knowledge[topic]["contributions"].append(contribution)
        self.shared_knowledge[topic]["last_updated"] = datetime.now()
        
        # Update consensus if multiple contributions exist
        self._update_knowledge_consensus(topic)
    
    def _update_knowledge_consensus(self, topic: str):
        """Update consensus knowledge for a topic."""
        topic_data = self.shared_knowledge[topic]
        contributions = topic_data["contributions"]
        
        if len(contributions) < 2:
            return
        
        # Simple consensus mechanism - weighted by confidence
        consensus = {}
        total_weight = 0
        
        for contrib in contributions:
            weight = contrib["confidence"]
            total_weight += weight
            
            for key, value in contrib["knowledge"].items():
                if key not in consensus:
                    consensus[key] = {"value": value, "weight": weight}
                else:
                    # Weighted average for numeric values, most confident for others
                    if isinstance(value, (int, float)) and isinstance(consensus[key]["value"], (int, float)):
                        total_val_weight = consensus[key]["weight"] + weight
                        consensus[key]["value"] = (
                            (consensus[key]["value"] * consensus[key]["weight"] + value * weight) / 
                            total_val_weight
                        )
                        consensus[key]["weight"] = total_val_weight
                    elif weight > consensus[key]["weight"]:
                        consensus[key] = {"value": value, "weight": weight}
        
        topic_data["consensus"] = {k: v["value"] for k, v in consensus.items()}
    
    def _setup_default_handlers(self):
        """Setup default message handlers."""
        
        async def default_knowledge_request_handler(message: AgentMessage):
            """Default handler for knowledge requests."""
            self.logger.info(f"Knowledge request received: {message.subject}")
        
        async def default_escalation_handler(message: AgentMessage):
            """Default handler for escalations."""
            self.logger.warning(f"Escalation received: {message.subject}")
        
        # Register default handlers
        self.default_handlers = {
            MessageType.KNOWLEDGE_REQUEST: default_knowledge_request_handler,
            MessageType.ESCALATION: default_escalation_handler
        }


# Factory function for easy integration
def create_communication_hub() -> AgentCommunicationHub:
    """Create an inter-agent communication hub."""
    return AgentCommunicationHub()


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        hub = create_communication_hub()
        
        # Register some example agents
        hub.register_agent("ui_specialist", AgentCapability(
            agent_id="ui_specialist",
            agent_name="UI Design Specialist",
            agent_type="design_reviewer",
            expertise_areas=["ui_design", "visual_design", "design_systems"],
            available_methods=["review", "critique", "recommend"],
            current_load=30,
            response_time_avg=120.0,
            reliability_score=0.9
        ))
        
        hub.register_agent("accessibility_expert", AgentCapability(
            agent_id="accessibility_expert",
            agent_name="Accessibility Expert",
            agent_type="accessibility_reviewer",
            expertise_areas=["accessibility", "wcag", "inclusive_design"],
            available_methods=["audit", "validate", "recommend"],
            current_load=50,
            response_time_avg=180.0,
            reliability_score=0.95
        ))
        
        print("✅ Communication hub ready")
        print(f"📱 Registered agents: {len(hub.agent_capabilities)}")
        
        # Example knowledge request
        request_id = await hub.request_knowledge(
            requester="ui_specialist",
            topic="accessibility",
            specific_question="What are the WCAG requirements for button contrast?",
            urgency=Priority.MEDIUM
        )
        
        print(f"📩 Knowledge request sent: {request_id}")
    
    asyncio.run(main())
