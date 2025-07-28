import base64
import io
from datetime import datetime
from typing import Dict, List, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
from PIL import Image
from prompts.review_prompts import DesignReviewPrompts
from prompts.roku_prompts import RokuDesignPrompts
from agents.utils import encode_image, extract_text_from_pdf
from agents.document_loaders import document_loader_manager
from agents.vp_preferences import vp_preference_manager

class DesignReviewAgent:
    """
    AI agent for reviewing design files and providing feedback.
    """
    
    def __init__(self, model_name: str = "gpt-4-vision-preview"):
        """
        Initialize the design review agent.
        
        Args:
            model_name: The OpenAI model to use for analysis
        """
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.3,
            max_tokens=1500
        )
        self.memory = ConversationBufferMemory(return_messages=True)
        self.prompts = DesignReviewPrompts()
        self.roku_prompts = RokuDesignPrompts()
        
    def review_design(
        self, 
        file, 
        review_type: str = "General Design",
        detail_level: int = 3,
        include_suggestions: bool = True
    ) -> Dict[str, Any]:
        """
        Review a design file and provide feedback.
        
        Args:
            file: Uploaded file object
            review_type: Type of review to perform
            detail_level: Level of detail (1-5)
            include_suggestions: Whether to include improvement suggestions
            
        Returns:
            Dictionary containing review results
        """
        try:
            # Process the file based on type
            if file.type.startswith('image'):
                content = self._analyze_image(file, review_type, detail_level, include_suggestions)
            elif file.type == 'application/pdf':
                content = self._analyze_pdf(file, review_type, detail_level, include_suggestions)
            else:
                raise ValueError(f"Unsupported file type: {file.type}")
            
            return content
            
        except Exception as e:
            return {"error": f"Failed to analyze design: {str(e)}"}
    
    def _analyze_image(
        self, 
        image_file, 
        review_type: str, 
        detail_level: int, 
        include_suggestions: bool
    ) -> Dict[str, Any]:
        """Analyze an image file."""
        # Encode image for API
        image_data = encode_image(image_file)
        
        # Get appropriate prompt
        system_prompt = self.prompts.get_review_prompt(
            review_type, detail_level, include_suggestions
        )
        
        # Create messages
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=[
                {
                    "type": "text",
                    "text": f"Please analyze this {review_type.lower()} design and provide feedback."
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_data}"
                    }
                }
            ])
        ]
        
        # Get response from LLM
        response = self.llm.invoke(messages)
        
        # Parse response
        return self._parse_review_response(response.content, include_suggestions)
    
    def _analyze_pdf(
        self, 
        pdf_file, 
        review_type: str, 
        detail_level: int, 
        include_suggestions: bool
    ) -> Dict[str, Any]:
        """Analyze a PDF file."""
        # Extract text from PDF
        pdf_content = extract_text_from_pdf(pdf_file)
        
        # Get appropriate prompt
        system_prompt = self.prompts.get_review_prompt(
            review_type, detail_level, include_suggestions
        )
        
        # Create messages
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"""
            Please analyze this {review_type.lower()} document and provide feedback.
            
            Document content:
            {pdf_content}
            """)
        ]
        
        # Get response from LLM
        response = self.llm.invoke(messages)
        
        # Parse response
        return self._parse_review_response(response.content, include_suggestions)
    
    def _parse_review_response(self, response: str, include_suggestions: bool) -> Dict[str, Any]:
        """Parse the LLM response into structured format."""
        result = {"review": response}
        
        # Try to extract score if mentioned
        lines = response.split('\n')
        for line in lines:
            if 'score:' in line.lower() or 'rating:' in line.lower():
                try:
                    # Extract number from line
                    import re
                    numbers = re.findall(r'\d+', line)
                    if numbers:
                        result["score"] = int(numbers[0])
                        break
                except:
                    pass
        
        # Extract suggestions if requested
        if include_suggestions and ('suggestions' in response.lower() or 'recommendations' in response.lower()):
            suggestions = []
            in_suggestions = False
            
            for line in lines:
                if 'suggestions' in line.lower() or 'recommendations' in line.lower():
                    in_suggestions = True
                    continue
                
                if in_suggestions and line.strip():
                    if line.startswith(('- ', '• ', '1.', '2.', '3.', '4.', '5.')):
                        suggestions.append(line.strip().lstrip('- •').strip())
                    elif line and not line.startswith(' '):
                        break
            
            if suggestions:
                result["suggestions"] = suggestions[:5]  # Limit to 5 suggestions
        
        return result
    
    def chat(self, message: str) -> str:
        """
        Handle chat messages with the design agent.
        
        Args:
            message: User message
            
        Returns:
            Agent response
        """
        try:
            # Get chat memory
            memory_messages = self.memory.chat_memory.messages
            
            # Create conversation context
            messages = [
                SystemMessage(content=self.prompts.get_chat_prompt())
            ] + memory_messages + [
                HumanMessage(content=message)
            ]
            
            # Get response
            response = self.llm.invoke(messages)
            
            # Save to memory
            self.memory.chat_memory.add_user_message(message)
            self.memory.chat_memory.add_ai_message(response.content)
            
            return response.content
            
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"
    
    def review_figma_file(
        self, 
        file_key: str, 
        review_type: str = "General Design",
        detail_level: int = 3,
        include_suggestions: bool = True,
        node_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Review a Figma design file.
        
        Args:
            file_key: Figma file key
            review_type: Type of review to perform
            detail_level: Level of detail (1-5)
            include_suggestions: Whether to include improvement suggestions
            node_ids: Optional specific node IDs to review
            
        Returns:
            Dictionary containing review results
        """
        try:
            # Load Figma file
            documents = document_loader_manager.load_figma_file(file_key, node_ids)
            
            if not documents:
                return {"error": "No content found in Figma file"}
            
            # Combine document content
            content = "\n\n".join([doc.page_content for doc in documents])
            
            # Get appropriate prompt
            system_prompt = self.prompts.get_review_prompt(
                review_type, detail_level, include_suggestions
            )
            
            # Create messages
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"""
                Please analyze this Figma {review_type.lower()} design and provide feedback.
                
                Figma File Content:
                {content}
                """)
            ]
            
            # Get response from LLM
            response = self.llm.invoke(messages)
            
            # Parse response
            result = self._parse_review_response(response.content, include_suggestions)
            result["source"] = "figma"
            result["file_key"] = file_key
            
            return result
            
        except Exception as e:
            return {"error": f"Failed to analyze Figma file: {str(e)}"}
    
    def review_confluence_pages(
        self, 
        space_key: str, 
        page_ids: Optional[List[str]] = None,
        review_type: str = "General Design",
        detail_level: int = 3,
        include_suggestions: bool = True
    ) -> Dict[str, Any]:
        """
        Review design documentation from Confluence pages.
        
        Args:
            space_key: Confluence space key
            page_ids: Optional specific page IDs to review
            review_type: Type of review to perform
            detail_level: Level of detail (1-5)
            include_suggestions: Whether to include improvement suggestions
            
        Returns:
            Dictionary containing review results
        """
        try:
            # Load Confluence documents
            documents = document_loader_manager.load_confluence_documents(
                space_key, page_ids
            )
            
            if not documents:
                return {"error": "No content found in Confluence pages"}
            
            # Combine document content
            content = "\n\n".join([
                f"Page: {doc.metadata.get('title', 'Unknown')}\n{doc.page_content}" 
                for doc in documents
            ])
            
            # Get appropriate prompt
            system_prompt = self.prompts.get_review_prompt(
                review_type, detail_level, include_suggestions
            )
            
            # Create messages
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"""
                Please analyze these Confluence design documents and provide feedback.
                
                Document Content:
                {content}
                """)
            ]
            
            # Get response from LLM
            response = self.llm.invoke(messages)
            
            # Parse response
            result = self._parse_review_response(response.content, include_suggestions)
            result["source"] = "confluence"
            result["space_key"] = space_key
            result["pages_reviewed"] = len(documents)
            
            return result
            
        except Exception as e:
            return {"error": f"Failed to analyze Confluence pages: {str(e)}"}
    
    def review_roku_design(
        self, 
        design_input,
        input_type: str = "file",  # "file", "figma", "confluence"
        design_context: str = "",
        focus_areas: list = None,
        include_grading: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform Roku-specific design evaluation using the VP's criteria.
        
        Args:
            design_input: File, Figma URL/key, or Confluence space info
            input_type: Type of input ("file", "figma", "confluence")
            design_context: Additional context about the design
            focus_areas: Specific areas to focus evaluation on
            include_grading: Whether to include letter grading
            **kwargs: Additional arguments for specific input types
            
        Returns:
            Dictionary containing Roku-specific review results
        """
        try:
            # Get the design content based on input type
            if input_type == "file":
                content = self._get_file_content_for_roku(design_input)
            elif input_type == "figma":
                content = self._get_figma_content_for_roku(design_input, **kwargs)
            elif input_type == "confluence":
                content = self._get_confluence_content_for_roku(design_input, **kwargs)
            else:
                raise ValueError(f"Unsupported input type: {input_type}")
            
            if not content:
                return {"error": f"No content could be extracted from {input_type} input"}
            
            # Get Roku evaluation prompt
            roku_prompt = self.roku_prompts.get_roku_evaluation_prompt(
                design_context=design_context,
                focus_areas=focus_areas,
                include_grading=include_grading
            )
            
            # Add VP's personalized preferences and learning
            vp_additions = vp_preference_manager.generate_personalized_prompt_additions()
            if vp_additions:
                roku_prompt += vp_additions
            
            # Create messages for evaluation
            messages = [
                SystemMessage(content=roku_prompt),
                HumanMessage(content=f"""
DESIGN PAGE = {design_context if design_context else "TV Interface Design"}

Please evaluate this design according to Roku's standards:

{content}
                """)
            ]
            
            # Get response from LLM
            response = self.llm.invoke(messages)
            
            # Parse the structured response
            result = self._parse_roku_response(response.content)
            result["evaluation_type"] = "roku_tv_design"
            result["input_type"] = input_type
            result["focus_areas"] = focus_areas
            
            # Record this evaluation in memory for learning
            design_id = f"{input_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            vp_preference_manager.record_evaluation_memory(
                design_id=design_id,
                input_type=input_type,
                context=design_context or "No context provided",
                issues_found=result.get("priority_issues", []),
                grade_assigned=result.get("grade", "Not graded")
            )
            
            return result
            
        except Exception as e:
            return {"error": f"Failed to perform Roku design evaluation: {str(e)}"}
    
    def _get_file_content_for_roku(self, file) -> str:
        """Extract content from uploaded file for Roku evaluation."""
        if file.type.startswith('image'):
            # For images, we'll use the vision model to describe the design
            image_data = encode_image(file)
            
            describe_prompt = """Describe this TV interface design in detail, including:
- Layout and screen organization
- Content tiles and their arrangement
- Navigation elements and focus indicators  
- Text elements, sizes, and hierarchy
- Color scheme and visual styling
- Any buttons, menus, or interactive elements
- Content entitlement indicators ($ symbols, subscription badges)
- Overall visual flow and information architecture

Be specific about elements that would be relevant for TV remote control navigation."""
            
            messages = [
                SystemMessage(content=describe_prompt),
                HumanMessage(content=[
                    {"type": "text", "text": "Please describe this TV interface design:"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                ])
            ]
            
            response = self.llm.invoke(messages)
            return response.content
            
        elif file.type == 'application/pdf':
            return extract_text_from_pdf(file)
        else:
            return "Unsupported file type for Roku evaluation"
    
    def _get_figma_content_for_roku(self, file_key: str, **kwargs) -> str:
        """Extract Figma content for Roku evaluation."""
        try:
            # Load Figma file
            documents = document_loader_manager.load_figma_file(
                file_key, 
                kwargs.get('node_ids')
            )
            
            if not documents:
                return "No content found in Figma file"
            
            # Get Figma analysis prompt
            figma_prompt = self.roku_prompts.get_figma_analysis_prompt()
            
            # Combine document content with analysis
            content = "\n\n".join([doc.page_content for doc in documents])
            
            return f"""FIGMA DESIGN ANALYSIS:
{figma_prompt}

FIGMA CONTENT:
{content}"""
            
        except Exception as e:
            return f"Error loading Figma content: {str(e)}"
    
    def _get_confluence_content_for_roku(self, space_key: str, **kwargs) -> str:
        """Extract Confluence content for Roku evaluation."""
        try:
            # Load Confluence documents
            documents = document_loader_manager.load_confluence_documents(
                space_key, 
                kwargs.get('page_ids')
            )
            
            if not documents:
                return "No content found in Confluence pages"
            
            # Get extraction prompt
            extraction_prompt = self.roku_prompts.get_confluence_extraction_prompt()
            
            # Process each document to extract design information
            extracted_content = []
            
            for doc in documents:
                # Use LLM to extract design-relevant information
                messages = [
                    SystemMessage(content=extraction_prompt),
                    HumanMessage(content=f"""
Page Title: {doc.metadata.get('title', 'Unknown')}
Page Content:
{doc.page_content}
                    """)
                ]
                
                response = self.llm.invoke(messages)
                extracted_content.append(f"""
PAGE: {doc.metadata.get('title', 'Unknown')}
EXTRACTED DESIGN INFORMATION:
{response.content}
""")
            
            return "\n\n" + "="*50 + "\n\n".join(extracted_content)
            
        except Exception as e:
            return f"Error loading Confluence content: {str(e)}"
    
    def _parse_roku_response(self, response: str) -> Dict[str, Any]:
        """Parse the structured Roku evaluation response."""
        result = {"full_evaluation": response}
        
        # Try to extract specific sections
        sections = {
            "known_issues": [],
            "priority_issues": [],
            "questions": [],
            "journey_impact": {},
            "grade": "",
            "suggestions": []
        }
        
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            # Identify sections
            if "known issues" in line.lower():
                current_section = "known_issues"
            elif "priority issues" in line.lower() or "issues table" in line.lower():
                current_section = "priority_issues"
            elif "questions" in line.lower() and "purpose" in line.lower():
                current_section = "questions"
            elif "journey impact" in line.lower() or "user journey" in line.lower():
                current_section = "journey_impact"
            elif "grade" in line.lower() and any(grade in line for grade in ['A', 'B', 'C', 'D', 'F']):
                # Extract grade
                import re
                grade_match = re.search(r'([A-F][+-]?)', line)
                if grade_match:
                    sections["grade"] = grade_match.group(1)
            elif "suggestions" in line.lower() or "improvements" in line.lower():
                current_section = "suggestions"
            
            # Add content to current section
            if current_section and line and not line.startswith('#'):
                if line.startswith('-') or line.startswith('•') or line[0].isdigit():
                    sections[current_section].append(line)
        
        result.update(sections)
        return result
    
    def provide_evaluation_feedback(
        self, 
        design_id: str, 
        vp_feedback: str, 
        vp_rating: int
    ) -> bool:
        """
        Allow VP to provide feedback on evaluation quality.
        
        Args:
            design_id: ID of the evaluation to provide feedback on
            vp_feedback: Text feedback from VP
            vp_rating: Rating 1-5 on evaluation accuracy
            
        Returns:
            True if feedback was recorded successfully
        """
        try:
            # Find and update the evaluation memory
            for memory in vp_preference_manager.evaluation_memory:
                if memory.design_id == design_id:
                    memory.vp_feedback = vp_feedback
                    memory.vp_rating = vp_rating
                    vp_preference_manager._save_data()
                    return True
            return False
        except Exception as e:
            print(f"Error providing feedback: {e}")
            return False
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """Get a summary of what the agent has learned from VP feedback."""
        return vp_preference_manager.get_learning_insights()
    
    def add_custom_requirement(
        self,
        title: str,
        description: str,
        rationale: str,
        priority: int,
        category: str,
        examples: List[str] = None,
        exceptions: List[str] = None
    ) -> str:
        """
        Add a new custom design requirement from VP.
        
        Args:
            title: Short title for the requirement
            description: Detailed description
            rationale: Why this requirement is important
            priority: 1-5 priority level
            category: Category (navigation, visual, accessibility, etc.)
            examples: Examples of good/bad implementations
            exceptions: When this rule might not apply
            
        Returns:
            ID of the created rule
        """
        return vp_preference_manager.add_custom_rule(
            title=title,
            description=description,
            rationale=rationale,
            priority=priority,
            category=category,
            created_by="VP",
            examples=examples or [],
            exceptions=exceptions or []
        )
