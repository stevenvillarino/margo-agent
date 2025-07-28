<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Design Review Agent - Copilot Instructions

This is a LangChain-based Python project for building an AI-powered design review agent.

## Project Context
- **Framework**: LangChain for building the AI agent
- **UI**: Streamlit for the web interface
- **Purpose**: Analyze design files and provide automated feedback
- **AI Model**: OpenAI GPT models via LangChain

## Code Style Guidelines
- Follow PEP 8 Python style guidelines
- Use type hints for function parameters and return types
- Write docstrings for all classes and functions
- Use meaningful variable and function names
- Keep functions focused and modular

## LangChain Patterns
- Use LangChain prompt templates for consistent AI interactions
- Implement proper error handling for API calls
- Use LangChain's built-in memory for conversation history
- Structure agents using LangChain's agent framework

## Design Review Features
- Support for image analysis (PNG, JPG, PDF)
- Design critique based on UI/UX principles
- Accessibility review capabilities
- Brand consistency checking
- Layout and typography analysis
