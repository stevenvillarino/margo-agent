# System Architecture

## Mermaid Architecture Diagram

```mermaid
graph TB
    subgraph "User Interface Layer"
        UI[Streamlit Web Interface]
        UI --> TAB1[File Upload Tab]
        UI --> TAB2[Figma Tab]
        UI --> TAB3[Confluence Tab]
        UI --> TAB4[VP Preferences Tab]
    end

    subgraph "Core Agent System"
        AGENT[Design Review Agent]
        AGENT --> MEMORY[Conversation Memory]
        AGENT --> LLMGPT[GPT-4 Vision Model]
    end

    subgraph "Evaluation Modes"
        STDEVAL[Standard Design Review]
        ROKUEVAL[Roku TV Design Review]
        ROKUEVAL --> ROKUPROMPTS[Roku Specific Prompts]
        ROKUEVAL --> VPPREF[VP Preferences Integration]
    end

    subgraph "Document Loaders"
        DOCLOADER[Document Loader Manager]
        DOCLOADER --> CONFLOADER[Confluence Loader]
        DOCLOADER --> FIGLOADER[Figma Loader]
        DOCLOADER --> FILELOADER[File Processor]
    end

    subgraph "VP Preference System"
        VPMGR[VP Preference Manager]
        VPMGR --> CUSTOMRULES[Custom Design Rules]
        VPMGR --> EVALMEM[Evaluation Memory]
        VPMGR --> VPPROFILE[VP Profile]
        VPMGR --> LEARNING[Learning Engine]
    end

    subgraph "Data Storage"
        RULEFILE[(custom_rules.json)]
        MEMFILE[(evaluation_memory.json)]
        PROFFILE[(vp_profile.json)]
    end

    subgraph "External APIs"
        OPENAI[OpenAI GPT-4 API]
        CONFLUENCEAPI[Confluence API]
        FIGMAAPI[Figma API]
    end

    subgraph "Configuration"
        ENV[Environment Variables]
        SETTINGS[Settings Manager]
    end

    %% User Flow
    TAB1 --> AGENT
    TAB2 --> DOCLOADER
    TAB3 --> DOCLOADER
    TAB4 --> VPMGR

    %% Agent Processing
    AGENT --> STDEVAL
    AGENT --> ROKUEVAL
    DOCLOADER --> AGENT

    %% VP Preference Integration
    VPPREF --> CUSTOMRULES
    VPPREF --> LEARNING
    ROKUEVAL --> VPMGR

    %% Data Persistence
    VPMGR --> RULEFILE
    VPMGR --> MEMFILE
    VPMGR --> PROFFILE

    %% External Connections
    LLMGPT --> OPENAI
    CONFLOADER --> CONFLUENCEAPI
    FIGLOADER --> FIGMAAPI

    %% Configuration
    SETTINGS --> ENV

    %% Learning Loop
    LEARNING --> ROKUEVAL
    EVALMEM --> LEARNING

    %% Styling
    classDef userInterface fill:#e1f5fe
    classDef coreSystem fill:#f3e5f5
    classDef dataLayer fill:#e8f5e8
    classDef externalAPI fill:#fff3e0
    classDef vpSystem fill:#fce4ec

    class UI,TAB1,TAB2,TAB3,TAB4 userInterface
    class AGENT,MEMORY,LLMGPT,STDEVAL,ROKUEVAL coreSystem
    class RULEFILE,MEMFILE,PROFFILE dataLayer
    class OPENAI,CONFLUENCEAPI,FIGMAAPI externalAPI
    class VPMGR,CUSTOMRULES,EVALMEM,VPPROFILE,LEARNING vpSystem
```

## Data Flow Architecture

```mermaid
sequenceDiagram
    participant VP as VP User
    participant UI as Streamlit UI
    participant AGENT as Design Agent
    participant VPMGR as VP Preference Manager
    participant LLM as GPT-4 Model
    participant STORAGE as Data Storage

    %% Initial Setup
    VP->>UI: Configure VP Profile
    UI->>VPMGR: Update profile settings
    VPMGR->>STORAGE: Save profile data

    VP->>UI: Add custom design rule
    UI->>VPMGR: Create custom rule
    VPMGR->>STORAGE: Save custom rules

    %% Design Evaluation Process
    VP->>UI: Upload design / Enter Figma URL / Select Confluence
    UI->>AGENT: Request Roku evaluation
    AGENT->>VPMGR: Get personalized prompt additions
    VPMGR->>VPMGR: Combine custom rules + learning insights
    VPMGR-->>AGENT: Enhanced evaluation prompt

    AGENT->>LLM: Send enhanced prompt + design content
    LLM-->>AGENT: Evaluation results
    AGENT->>VPMGR: Record evaluation memory
    VPMGR->>STORAGE: Save evaluation data
    AGENT-->>UI: Return structured results
    UI-->>VP: Display evaluation with grade & issues

    %% Feedback Loop
    VP->>UI: Provide feedback on evaluation
    UI->>VPMGR: Record VP feedback & rating
    VPMGR->>VPMGR: Update learning insights
    VPMGR->>STORAGE: Save updated memory

    %% Learning Application
    Note over VPMGR: Analyze patterns in feedback
    Note over VPMGR: Identify common issues
    Note over VPMGR: Adjust future prompts
```

## Component Details

### 1. **Streamlit UI Layer**
- **File Upload Tab**: Handles local image/PDF uploads
- **Figma Tab**: Processes Figma URLs and file keys
- **Confluence Tab**: Manages Confluence space/page analysis
- **VP Preferences Tab**: Custom rules, profile, feedback, and learning insights

### 2. **Core Agent System**
- **Design Review Agent**: Main orchestrator for all evaluations
- **Conversation Memory**: Maintains chat context and history
- **Evaluation Modes**: Standard review vs. Roku-specific evaluation

### 3. **VP Preference System**
- **Custom Rules Engine**: User-defined design requirements with rationale
- **Evaluation Memory**: Historical record of all evaluations and feedback
- **Learning Engine**: Analyzes patterns to improve future evaluations
- **VP Profile**: Personal preferences and evaluation style

### 4. **Document Processing**
- **Multi-source Support**: Files, Figma, Confluence
- **Content Extraction**: Text, images, design specifications
- **Format Normalization**: Consistent input for evaluation

### 5. **Learning & Adaptation**
- **Feedback Collection**: VP ratings and comments on evaluations
- **Pattern Recognition**: Common issues, grade distributions, preferences
- **Prompt Enhancement**: Dynamic addition of learned preferences
- **Continuous Improvement**: System gets better with each evaluation

## Key Features

### 🧠 **Adaptive Learning**
- Records every evaluation and VP feedback
- Identifies patterns in VP's preferences
- Automatically adjusts future evaluations
- Tracks accuracy improvements over time

### 🎯 **Personalization**
- Custom design rules with priority levels
- VP-specific communication style preferences
- Focus area customization
- Strict vs. lenient evaluation areas

### 📊 **Analytics & Insights**
- Evaluation history and trends
- Most common issue types
- Grade distribution analysis
- Learning effectiveness metrics

### 🔄 **Continuous Improvement**
- Feedback loop between evaluations and learning
- Custom rule refinement based on usage
- Prompt optimization through VP feedback
- Performance tracking and adjustment
