# JIRA Task Workflow

Direct Python API integration for JIRA workflows with Claude Code development assistance.

## Overview

This workflow provides seamless integration between JIRA issues and development work, using Claude Code's capabilities to assist with implementation, testing, and code review.

## Workflow State Diagram

```mermaid
graph TD
    A[🎫 JIRA Issue Created] --> B{🔐 User Has Permissions?}
    B -->|No| Z1[❌ Access Denied]
    B -->|Yes| C[📋 Issue Retrieval & Validation]
    
    C --> D[🌿 Git Branch Creation]
    D --> E[💬 JIRA Comment: Development Started]
    E --> F[📊 Analytics Session Started]
    F --> G[🔔 Team Notifications Sent]
    
    G --> H{📈 Workflow Phase?}
    
    %% Phase 1: Basic Workflow
    H -->|Phase 1| I1[🤖 Claude Code Launch]
    I1 --> J1[📝 Development Plan Creation]
    J1 --> K1[🔄 Interactive Development Loop]
    K1 --> L1[✅ Manual Completion]
    
    %% Phase 2: Enhanced Workflow
    H -->|Phase 2| I2[✨ Enhanced Claude Code]
    I2 --> J2[📝 Context-Aware Planning]
    J2 --> K2[🔄 Enhanced Interactive Loop]
    K2 --> M2[🔍 Quality Checks]
    M2 --> N2[🔗 Automated PR Creation]
    N2 --> L2[✅ Enhanced Completion]
    
    %% Phase 3: Advanced Workflow
    H -->|Phase 3| I3[🚀 Advanced Workflow Init]
    I3 --> P3[🎯 Project Type Detection]
    P3 --> Q3[📋 Template Application]
    Q3 --> K3[🔄 Advanced Interactive Loop]
    K3 --> R3[🔧 CI/CD Status Check]
    R3 --> S3[🚀 Deployment Trigger]
    S3 --> T3[📊 Analytics Recording]
    T3 --> L3[✅ Advanced Completion]
    
    %% Phase 4: Enterprise Workflow
    H -->|Phase 4| I4[🏢 Enterprise Workflow Init]
    I4 --> U4[👥 Team Context Loading]
    U4 --> V4[🔐 Permission Validation]
    V4 --> K4[🔄 Enterprise Interactive Loop]
    
    %% Interactive Development Loops
    K1 --> CMD1{💻 User Command}
    K2 --> CMD2{💻 Enhanced Command}
    K3 --> CMD3{💻 Advanced Command}
    K4 --> CMD4{💻 Enterprise Command}
    
    %% Phase 1 Commands
    CMD1 -->|analyze| W1[🔍 Basic Codebase Analysis]
    CMD1 -->|implement| X1[🛠️ Basic Implementation Help]
    CMD1 -->|test| Y1[🧪 Basic Testing]
    CMD1 -->|review| Z1[👀 Basic Review]
    CMD1 -->|done| L1
    
    %% Phase 2 Commands
    CMD2 -->|analyze| W2[🔍 Context-Aware Analysis]
    CMD2 -->|implement| X2[🛠️ Enhanced Implementation]
    CMD2 -->|test| Y2[🧪 Comprehensive Testing]
    CMD2 -->|review| Z2[👀 Quality-Focused Review]
    CMD2 -->|done| N2
    
    %% Phase 3 Commands
    CMD3 -->|analyze| W3[🔍 Project-Specific Analysis]
    CMD3 -->|implement| X3[🛠️ Template-Guided Implementation]
    CMD3 -->|test| Y3[🧪 CI/CD Integrated Testing]
    CMD3 -->|review| Z3[👀 Professional Review]
    CMD3 -->|project| P3A[🎯 Project Configuration]
    CMD3 -->|ci| R3A[🔧 CI/CD Status]
    CMD3 -->|deploy| S3A[🚀 Deployment Management]
    CMD3 -->|done| S3
    
    %% Phase 4 Commands
    CMD4 -->|analyze| W4[🔍 AI-Powered Analysis]
    CMD4 -->|implement| X4[🛠️ Enterprise Implementation]
    CMD4 -->|test| Y4[🧪 Enterprise Testing]
    CMD4 -->|review| Z4[🤖 AI Code Review & Security Scan]
    CMD4 -->|approve| A4[🔐 Approval Workflow Management]
    CMD4 -->|dashboard| D4[🏢 Team Dashboard]
    CMD4 -->|ci| R4[🔧 Advanced CI/CD Monitoring]
    CMD4 -->|deploy| S4[🚀 Enterprise Deployment]
    CMD4 -->|done| COMP4[🏁 Enterprise Completion]
    
    %% Command Loops
    W1 --> CMD1
    X1 --> CMD1
    Y1 --> CMD1
    Z1 --> CMD1
    
    W2 --> CMD2
    X2 --> CMD2
    Y2 --> CMD2
    Z2 --> CMD2
    
    W3 --> CMD3
    X3 --> CMD3
    Y3 --> CMD3
    Z3 --> CMD3
    P3A --> CMD3
    R3A --> CMD3
    S3A --> CMD3
    
    W4 --> CMD4
    X4 --> CMD4
    Y4 --> CMD4
    Z4 --> REV4{🔍 Critical Issues Found?}
    A4 --> CMD4
    D4 --> CMD4
    R4 --> CMD4
    S4 --> APP4{🔐 Approval Required?}
    
    %% Enterprise Review Flow
    REV4 -->|Yes| APP_REQ[🔐 Request Security Approval]
    REV4 -->|No| CMD4
    APP_REQ --> NOTIFY[🔔 Notify Approvers]
    NOTIFY --> WAIT[⏳ Wait for Approval]
    WAIT --> APP_DEC{✅ Approved?}
    APP_DEC -->|Yes| CMD4
    APP_DEC -->|No| REJ[❌ Deployment Rejected]
    APP_DEC -->|Timeout| EXP[⏰ Approval Expired]
    
    %% Enterprise Deployment Flow
    APP4 -->|Yes| WAIT_DEP[⏳ Wait for Deployment Approval]
    APP4 -->|No| COMP4
    WAIT_DEP --> COMP4
    
    %% Completion Flows
    L1 --> FINAL[🎉 Workflow Complete]
    L2 --> FINAL
    L3 --> FINAL
    COMP4 --> ENT_FINAL[🏢 Enterprise Completion]
    
    ENT_FINAL --> NOTIF_FINAL[🔔 Final Notifications]
    NOTIF_FINAL --> ANALYTICS_END[📊 Analytics Session End]
    ANALYTICS_END --> AUDIT[📋 Audit Log Entry]
    AUDIT --> FINAL
    
    %% Webhook Integration (Phase 4)
    WH[🌐 Webhook Events] -.-> AUTO_START[🤖 Auto-Start Workflow]
    AUTO_START -.-> C
    
    WH -.-> PR_EVENT[🔗 PR Events]
    PR_EVENT -.-> JIRA_UPDATE[💬 JIRA Comment Update]
    
    WH -.-> STATUS_CHANGE[📊 Status Change Events]
    STATUS_CHANGE -.-> AUTO_ACTION[🤖 Automated Actions]
    
    %% External Integrations
    FINAL --> EXT_INT[🌐 External Integrations]
    EXT_INT --> SLACK[💬 Slack Notifications]
    EXT_INT --> TEAMS[👥 Teams Notifications]
    EXT_INT --> EMAIL[📧 Email Reports]
    EXT_INT --> CALENDAR[📅 Calendar Updates]
    
    %% Error Handling
    REJ --> ERROR_HANDLE[⚠️ Error Handling]
    EXP --> ERROR_HANDLE
    Z1 --> ERROR_HANDLE
    ERROR_HANDLE --> FINAL
    
    %% Styling
    classDef phase1 fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef phase2 fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef phase3 fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef phase4 fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef webhook fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef external fill:#f1f8e9,stroke:#33691e,stroke-width:2px
    classDef error fill:#ffebee,stroke:#b71c1c,stroke-width:2px
    
    class I1,J1,K1,L1,W1,X1,Y1,Z1 phase1
    class I2,J2,K2,M2,N2,L2,W2,X2,Y2,Z2 phase2
    class I3,P3,Q3,K3,R3,S3,T3,L3,W3,X3,Y3,Z3,P3A,R3A,S3A phase3
    class I4,U4,V4,K4,COMP4,W4,X4,Y4,Z4,A4,D4,R4,S4,REV4,APP_REQ,NOTIFY,WAIT,APP_DEC,APP4,WAIT_DEP,ENT_FINAL,NOTIF_FINAL,ANALYTICS_END,AUDIT phase4
    class WH,AUTO_START,PR_EVENT,JIRA_UPDATE,STATUS_CHANGE,AUTO_ACTION webhook
    class EXT_INT,SLACK,TEAMS,EMAIL,CALENDAR external
    class REJ,EXP,Z1,ERROR_HANDLE error
```

### Detailed Workflow Diagrams

#### 1. Workflow Initialization Flow
```mermaid
graph TD
    A[🎫 JIRA Issue Key Provided] --> B[🔐 Load User Credentials]
    B --> C{👤 User Authentication Valid?}
    C -->|No| D[❌ Authentication Failed]
    C -->|Yes| E[📋 Fetch JIRA Issue Details]
    
    E --> F{📝 Issue Exists & Accessible?}
    F -->|No| G[❌ Issue Not Found/No Access]
    F -->|Yes| H[🌿 Generate Branch Name]
    
    H --> I[🔍 Check Git Repository]
    I --> J{📁 Valid Git Repo?}
    J -->|No| K[❌ Not a Git Repository]
    J -->|Yes| L[🌱 Create Feature Branch]
    
    L --> M[💬 Add JIRA Comment: Started]
    M --> N[📊 Initialize Analytics Session]
    N --> O[🔔 Send Team Notifications]
    O --> P[✅ Initialization Complete]
    
    classDef success fill:#e8f5e8,stroke:#2e7d32
    classDef error fill:#ffebee,stroke:#d32f2f
    classDef process fill:#e3f2fd,stroke:#1976d2
    
    class P success
    class D,G,K error
    class B,E,H,I,L,M,N,O process
```

#### 2. Interactive Development Command Flow
```mermaid
graph TD
    A[🔄 Interactive Development Loop] --> B{💻 User Command Input}
    
    B -->|analyze| C[🔍 Codebase Analysis]
    B -->|implement| D[🛠️ Implementation Assistance]
    B -->|test| E[🧪 Testing Support]
    B -->|review| F[👀 Code Review]
    B -->|done| G[🏁 Complete Workflow]
    B -->|quit| H[👋 Exit Without Completion]
    B -->|help| I[📚 Show Command Help]
    
    %% Analyze Flow
    C --> C1[📂 Scan Project Structure]
    C1 --> C2[🔍 Search Relevant Files]
    C2 --> C3[📝 Generate Analysis Report]
    C3 --> A
    
    %% Implement Flow
    D --> D1[📖 Read Current Code]
    D1 --> D2[🤖 Generate Implementation Plan]
    D2 --> D3[✏️ Apply Code Changes]
    D3 --> D4[📝 Document Changes]
    D4 --> A
    
    %% Test Flow
    E --> E1[🔍 Identify Test Files]
    E1 --> E2[🧪 Create/Update Tests]
    E2 --> E3[▶️ Run Test Suite]
    E3 --> E4{✅ Tests Pass?}
    E4 -->|Yes| A
    E4 -->|No| E5[🔧 Fix Test Failures]
    E5 --> E3
    
    %% Review Flow
    F --> F1[📊 Git Status Check]
    F1 --> F2[🔍 Code Quality Analysis]
    F2 --> F3[📋 Generate Review Report]
    F3 --> A
    
    %% Complete Flow
    G --> G1[🔍 Final Review]
    G1 --> G2[💾 Git Commit]
    G2 --> G3[📤 Push to Remote]
    G3 --> G4[🔗 Create Pull Request]
    G4 --> END[🎉 Workflow Complete]
    
    I --> A
    H --> END
    
    classDef command fill:#fff3e0,stroke:#f57c00
    classDef process fill:#e8f5e8,stroke:#388e3c
    classDef decision fill:#f3e5f5,stroke:#7b1fa2
    classDef terminal fill:#e1f5fe,stroke:#0277bd
    
    class B command
    class C1,C2,C3,D1,D2,D3,D4,E1,E2,E3,E5,F1,F2,F3,G1,G2,G3,G4 process
    class E4 decision
    class END,H terminal
```

#### 3. Phase 4 Enterprise Security & Approval Flow
```mermaid
graph TD
    A[🔍 Enterprise Code Review] --> B[🤖 AI Security Scan]
    B --> C[📊 Quality Analysis]
    C --> D[🔢 Calculate Security Score]
    
    D --> E{🚨 Critical Issues Found?}
    E -->|No| F[✅ Review Passed]
    E -->|Yes| G[🔐 Security Approval Required]
    
    G --> H[📋 Create Approval Request]
    H --> I[👥 Identify Required Approvers]
    I --> J[🔔 Notify Approvers via Slack/Email]
    
    J --> K{⏳ Approval Response}
    K -->|✅ Approved| L[🚀 Proceed with Deployment]
    K -->|❌ Rejected| M[🛑 Block Deployment]
    K -->|⏰ Timeout| N[⏰ Auto-Reject (Expired)]
    
    L --> O[🌐 Trigger CI/CD Pipeline]
    O --> P[📊 Update Analytics]
    P --> Q[🔔 Send Success Notifications]
    
    M --> R[💬 Add Rejection Comment to JIRA]
    N --> R
    R --> S[📊 Log Security Incident]
    
    F --> T{🚀 Deployment Requested?}
    T -->|Yes| U[🔐 Check Deployment Permissions]
    T -->|No| V[✅ Review Complete]
    
    U --> W{👤 User Has Deploy Permission?}
    W -->|Yes| O
    W -->|No| X[🔐 Request Deployment Approval]
    X --> I
    
    classDef security fill:#ffebee,stroke:#c62828
    classDef approval fill:#fff3e0,stroke:#ef6c00
    classDef success fill:#e8f5e8,stroke:#2e7d32
    classDef process fill:#e3f2fd,stroke:#1565c0
    
    class B,D,G,H security
    class I,J,K,L,U,W,X approval
    class F,Q,V success
    class C,O,P,R,S process
```

#### 4. Webhook Integration & Automation Flow
```mermaid
graph TD
    A[🌐 External Webhook Received] --> B{🔍 Webhook Source}
    
    B -->|JIRA| C[📋 JIRA Event Processing]
    B -->|GitHub| D[🔗 GitHub Event Processing]
    B -->|GitLab| E[🦊 GitLab Event Processing]
    
    %% JIRA Events
    C --> C1{📝 Event Type}
    C1 -->|Issue Created| C2[🚀 Auto-Start Workflow]
    C1 -->|Issue Updated| C3[📊 Update Status]
    C1 -->|Status Changed| C4[🔄 Trigger State Change]
    
    %% GitHub Events
    D --> D1{🔗 Event Type}
    D1 -->|PR Opened| D2[💬 Add JIRA Comment]
    D1 -->|PR Merged| D3[✅ Mark Issue Complete]
    D1 -->|Push Event| D4[🔧 Trigger CI/CD Check]
    
    %% GitLab Events
    E --> E1{🦊 Event Type}
    E1 -->|MR Opened| E2[💬 Add JIRA Comment]
    E1 -->|MR Merged| E3[✅ Mark Issue Complete]
    E1 -->|Pipeline Event| E4[📊 Update Build Status]
    
    %% Auto Actions
    C2 --> F[🔐 Check User Permissions]
    F --> G{👤 Auto-Start Allowed?}
    G -->|Yes| H[🚀 Initialize Workflow]
    G -->|No| I[📧 Send Assignment Notification]
    
    C3 --> J[📊 Update Analytics]
    C4 --> K[🔔 Send Status Notifications]
    
    D2 --> L[🔗 Extract Issue Key from Branch]
    L --> M[💬 Update JIRA with PR Link]
    
    D3 --> N[🏁 Trigger Completion Workflow]
    D4 --> O[📋 Update CI/CD Dashboard]
    
    %% Final Actions
    H --> P[🔔 Team Notifications]
    I --> P
    J --> P
    K --> P
    M --> P
    N --> P
    O --> P
    P --> Q[📝 Log Webhook Event]
    Q --> R[✅ Webhook Processing Complete]
    
    classDef webhook fill:#fce4ec,stroke:#ad1457
    classDef jira fill:#e3f2fd,stroke:#1565c0
    classDef github fill:#f3e5f5,stroke:#6a1b9a
    classDef gitlab fill:#fff3e0,stroke:#ef6c00
    classDef action fill:#e8f5e8,stroke:#2e7d32
    
    class A,B webhook
    class C,C1,C2,C3,C4 jira
    class D,D1,D2,D3,D4 github
    class E,E1,E2,E3,E4 gitlab
    class F,G,H,I,J,K,L,M,N,O,P,Q,R action
```

#### 5. Team Management & Collaboration Flow
```mermaid
graph TD
    A[👥 Team Management Request] --> B{🔍 Request Type}
    
    B -->|Workload Check| C[📊 Get Team Workload]
    B -->|User Management| D[👤 User Operations]
    B -->|Permission Check| E[🔐 Permission Validation]
    B -->|Activity Report| F[📈 Generate Activity Report]
    
    %% Workload Flow
    C --> C1[📋 Query JIRA for Assigned Issues]
    C1 --> C2[👥 Get Team Members]
    C2 --> C3[📊 Calculate Individual Workloads]
    C3 --> C4[📈 Generate Team Dashboard]
    
    %% User Management Flow
    D --> D1{👤 Operation Type}
    D1 -->|Add User| D2[➕ Create User Profile]
    D1 -->|Update Role| D3[🔄 Update Permissions]
    D1 -->|Deactivate| D4[❌ Deactivate User]
    
    D2 --> D5[📧 Send Welcome Email]
    D3 --> D6[🔔 Notify Role Change]
    D4 --> D7[📝 Log Deactivation]
    
    %% Permission Flow
    E --> E1[👤 Load User Profile]
    E1 --> E2[🔍 Check Role Permissions]
    E2 --> E3{✅ Permission Granted?}
    E3 -->|Yes| E4[✅ Allow Action]
    E3 -->|No| E5[❌ Deny Access]
    E5 --> E6[📧 Send Access Denial Notice]
    
    %% Activity Report Flow
    F --> F1[📊 Query Activity Database]
    F1 --> F2[📈 Aggregate Team Metrics]
    F2 --> F3[📋 Generate Visual Reports]
    F3 --> F4[📧 Send Report to Stakeholders]
    
    %% Collaboration Features
    C4 --> G[🔔 Collaboration Notifications]
    D5 --> G
    D6 --> G
    E4 --> H[📝 Log Activity]
    E6 --> H
    F4 --> I[📊 Update Team Analytics]
    
    G --> J[💬 Slack Integration]
    G --> K[👥 Teams Integration]
    G --> L[📧 Email Notifications]
    
    H --> M[🗂️ Audit Trail]
    I --> N[📈 Performance Tracking]
    
    J --> O[✅ Team Collaboration Complete]
    K --> O
    L --> O
    M --> O
    N --> O
    
    classDef management fill:#e8f5e8,stroke:#2e7d32
    classDef user fill:#e3f2fd,stroke:#1565c0
    classDef permission fill:#fff3e0,stroke:#ef6c00
    classDef activity fill:#f3e5f5,stroke:#6a1b9a
    classDef notification fill:#fce4ec,stroke:#ad1457
    
    class C,C1,C2,C3,C4 management
    class D,D1,D2,D3,D4,D5,D6,D7 user
    class E,E1,E2,E3,E4,E5,E6 permission
    class F,F1,F2,F3,F4,H,I,M,N activity
    class G,J,K,L notification
```

### Workflow Complexity Breakdown

**🎯 Level 1 - Basic (Phase 1)**
- Simple linear flow: Issue → Branch → Develop → Commit
- Manual intervention at each step
- Basic Claude Code integration

**⚡ Level 2 - Enhanced (Phase 2)**
- Context preservation between commands
- Automated quality checks
- Automatic PR creation

**🚀 Level 3 - Advanced (Phase 3)**
- Multi-project support with templates
- CI/CD pipeline integration
- Analytics and reporting

**🏢 Level 4 - Enterprise (Phase 4)**
- AI-powered security scanning
- Role-based access control with approvals
- Real-time webhook integration
- Multi-channel notifications
- Comprehensive audit trails

**🏢 Phase 4 Enterprise Features Now Available!**
- AI-powered security and quality code review
- Role-based access control and approval workflows
- Real-time webhook integration (JIRA, GitHub, GitLab)
- Team collaboration and workload management
- External integrations (Slack, Teams, Email)
- Enterprise analytics and compliance reporting

**🚀 Phase 3 Advanced Features:**
- Multi-project support with auto-detection
- Project-specific workflow templates
- CI/CD pipeline integration and monitoring
- Analytics and reporting dashboard
- Automated deployment capabilities

**Phase 2 Enhanced Features:**
- Context preservation between commands
- Enhanced prompting strategies
- Automatic PR creation with GitHub CLI
- Professional workflow completion
- Comprehensive quality checks

## Features

- **Direct JIRA API Integration**: No external dependencies like MCP servers
- **Git Branch Management**: Automatic branch creation with standardized naming
- **Claude Code Integration**: Full development assistance with comprehensive tool permissions
- **Interactive Development**: Step-by-step workflow with analyze/implement/test/review commands
- **Progress Tracking**: Automatic JIRA updates throughout development lifecycle

## Quick Start

### 1. Setup Configuration

```bash
# Create sample configuration file
python example.py --create-config

# Edit .env file with your JIRA credentials
vim .env
```

Required environment variables:
```bash
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_API_TOKEN=your_api_token_here
JIRA_USERNAME=your.email@company.com
JIRA_PROJECT_KEY=PROJ  # Optional
```

### 2. Test Setup

```bash
# Run all tests
python example.py --test-all

# Test with specific issue
python example.py --demo PROJ-123
```

### 3. Start Working on an Issue

```bash
# Standard workflow
python jira_task.py PROJ-123

# Enhanced workflow with Phase 2 features
python jira_task.py PROJ-123 --enhanced

# Advanced workflow with Phase 3 features
python jira_task.py PROJ-123 --advanced

# Enterprise workflow with Phase 4 features (recommended for teams)
python jira_task.py PROJ-123 --enterprise --user john.doe

# Agent-flows mode-based workflow with Phase 5 features (intelligent orchestration)
python jira_task.py PROJ-123 --agent-modes --user john.doe

# Agent-flows workflow with custom modes directory
python jira_task.py PROJ-123 --agent-modes --modes-path /path/to/modes --user john.doe

# Specify project for multi-project support
python jira_task.py PROJ-123 --advanced --project my-project

# Or use specific commands
python jira_task.py PROJ-123 --command start
python jira_task.py PROJ-123 --command status
python jira_task.py PROJ-123 --command list
python jira_task.py PROJ-123 --command update --comment "Progress update"
```

## Workflow Phases

### Phase 1: Initial Setup (Automated)
1. **Issue Retrieval**: Fetch JIRA issue details and validate access
2. **Branch Creation**: Create feature branch with standardized naming
3. **JIRA Update**: Add comment indicating development started

### Phase 2: Interactive Development
Available commands in interactive mode:

- **`analyze`** - Analyze codebase to find relevant files
- **`implement`** - Get implementation help and make code changes
- **`test`** - Create/run tests for implemented functionality
- **`review`** - Review changes and prepare for commit
- **`done`** - Complete workflow with commits and PR creation
- **`quit`** - Exit development mode

### Phase 3: Completion
- Final code review and testing
- Git commit with descriptive message
- Branch push to remote
- Pull request creation
- JIRA update with completion status

## Enhanced Workflow Features (Phase 2)

### Context Preservation
- Maintains command history and file changes throughout session
- Builds upon previous analysis and work
- Avoids redundant operations
- Provides session summaries

### Enhanced Claude Code Integration
- Context-aware prompting with session history
- Task-specific instructions for better results
- Intelligent file modification tracking
- Professional workflow completion

### Automatic PR Creation
- GitHub CLI integration for seamless PR creation
- Comprehensive PR descriptions with change summaries
- Automatic JIRA issue linking
- Professional commit message generation

### Quality Assurance
- Code quality checks and linting integration
- Security and performance analysis
- Comprehensive testing coverage
- Professional review process

### Usage
```bash
# Use enhanced features
python jira_task.py PROJ-123 --enhanced

# Enhanced commands provide:
✨ Context preservation between commands
🔍 Deeper analysis with session awareness  
🛠️ Incremental implementation with quality focus
🧪 Comprehensive testing with coverage analysis
🔍 Professional code review with quality checks
🏁 Automated PR creation with GitHub integration
```

## Advanced Workflow Features (Phase 3)

### Multi-Project Support
- Automatic project detection from repository
- Project-specific configurations and templates
- Support for Python, JavaScript, TypeScript, React, Next.js, FastAPI, Django, Flask
- Custom build, test, lint, and deployment commands per project

### Project Templates
- **FastAPI Template**: API development with pytest, black, flake8, mypy
- **React TypeScript**: Component development with Jest, ESLint, Prettier
- **Node.js TypeScript**: Backend services with comprehensive testing
- Automatically applies best practices for detected project type

### CI/CD Integration
- Auto-detection of CI/CD systems (GitHub Actions, GitLab CI, Jenkins, etc.)
- Real-time build status monitoring
- Automated deployment triggers
- Integration with existing pipeline configurations

### Analytics & Reporting
- Comprehensive workflow analytics and metrics
- Project productivity reports
- Team dashboard with success rates and timing
- Visual charts and trend analysis
- Quality metrics tracking

### Configuration
Create `jira_projects.yml` for multi-project support:
```yaml
projects:
  my-project:
    type: fastapi
    jira_project_key: API
    repository_url: https://github.com/example/my-project.git
    build_command: "pip install -r requirements.txt"
    test_command: "pytest --cov=app"
    reviewers: ["team-lead", "senior-dev"]
    labels: ["api", "backend"]
```

### Usage
```bash
# Advanced workflow with all Phase 3 features
python jira_task.py PROJ-123 --advanced

# Advanced commands include:
🎯 project    - Show project configuration and settings
🔧 ci         - Check CI/CD pipeline status
🚀 deploy     - Trigger deployment to environment
📊 analytics  - Generate productivity reports
🔍 analyze    - Project-specific codebase analysis
```

## Enterprise Workflow Features (Phase 4)

### AI-Powered Code Review
- **Security Scanning**: Automated detection of security vulnerabilities
- **Quality Analysis**: Code complexity, style, and maintainability analysis
- **Intelligent Suggestions**: AI-generated recommendations for improvements
- **Compliance Reporting**: Enterprise-grade security and quality reports

### Team Management & Collaboration
- **Role-Based Access Control**: Admin, Tech Lead, Developer, Reviewer roles
- **Approval Workflows**: Required approvals for sensitive actions
- **Team Workload Tracking**: Real-time visibility into team capacity
- **Activity Analytics**: Comprehensive team productivity metrics

### Real-Time Webhook Integration
- **JIRA Events**: Automatic workflow triggers from issue updates
- **GitHub/GitLab**: PR and merge event processing
- **Custom Actions**: Configurable responses to webhook events
- **Event History**: Complete audit trail of all webhook activities

### External Integrations
- **Slack Integration**: Rich notifications with interactive buttons
- **Microsoft Teams**: Adaptive cards and team notifications
- **Email Notifications**: Professional HTML email templates
- **Calendar Integration**: Automated scheduling for reviews and deployments

### Enterprise Security & Compliance
- **Secret Detection**: Automated scanning for hardcoded credentials
- **Security Scoring**: Quantitative security assessment (0-100)
- **Audit Logging**: Complete activity tracking for compliance
- **Access Control**: Granular permission management

### Configuration
Create `team_config.yml` for team management:
```yaml
teams:
  backend:
    description: "Backend Development Team"
    lead: "tech_lead"
    members: ["dev1", "dev2", "dev3"]
    approval_rules:
      deploy_production: ["tech_lead", "admin"]
      force_merge: ["tech_lead"]

users:
  - username: "tech_lead"
    email: "tech.lead@company.com"
    role: "tech_lead"
    team: "backend"
```

Environment variables for integrations:
```bash
# Webhook Security
GITHUB_WEBHOOK_SECRET=your_github_webhook_secret
JIRA_WEBHOOK_SECRET=your_jira_webhook_secret

# Slack Integration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
SLACK_BOT_TOKEN=xoxb-your-bot-token

# Microsoft Teams
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/...

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your.email@company.com
SMTP_PASSWORD=your_app_password
```

### Usage
```bash
# Enterprise workflow with all Phase 4 features
python jira_task.py PROJ-123 --enterprise --user john.doe

# Start webhook server for real-time integration
python enterprise_workflow.py PROJ-123 --command webhook-server --webhook-port 8080

# Enterprise commands include:
🔍 analyze     - AI-powered codebase analysis
🛠️  implement   - Template-guided implementation
🧪 test        - Comprehensive testing with CI/CD
🔍 review      - Enterprise AI code review with security scanning
🔐 approve     - Handle team approval requests
🏢 dashboard   - Enterprise team dashboard and analytics
🔧 ci          - CI/CD pipeline status monitoring
🚀 deploy      - Deployment with approval workflows
🏁 done        - Complete enterprise workflow with notifications
```

### Phase 5 Agent-Flows Mode-Based Workflow

Phase 5 represents the evolution of the JIRA workflow to leverage sophisticated **agent-flows modes** for intelligent task orchestration. Unlike traditional workflows, Phase 5 uses an orchestrator that dynamically delegates tasks to specialized modes.

#### Agent-Flows Interactive Commands

```bash
# Start Phase 5 agent-flows workflow
python jira_task.py PROJ-123 --agent-modes --user john.doe

🎭 Agent-Flows Interactive Mode Commands:
📋 plan         - Review the orchestrator's master plan
🎭 orchestrate  - Strategic workflow coordination and guidance  
📖 story        - Break down requirements into user stories
🏗️  architect    - Design system architecture and approach
🔍 research     - Investigate solutions and best practices
🛠️  code         - Implement with production-ready code
🐛 debug        - Debug issues and troubleshoot problems
👨‍💼 review       - Expert technical review and validation
📝 write        - Create comprehensive documentation
🚀 devops       - Configure deployment and operations
🏁 done         - Complete workflow with synthesis
```

#### Mode-Based Orchestration Features

- **Dynamic Mode Selection**: Orchestrator analyzes JIRA issue and recommends appropriate modes
- **Intelligent Coordination**: Non-predetermined workflow sequence adapts to issue requirements
- **Expert-Level Capabilities**: Each mode provides specialized expertise (architecture, security, etc.)
- **Comprehensive Synthesis**: Final synthesis combines all mode results into actionable insights
- **Context Preservation**: Workflow context maintained across all mode executions

#### Requirements for Phase 5

```bash
# Required: Agent-flows modes directory with instruction files
modes/
├── orchestrator.md      # Strategic coordination
├── architect.md         # System design
├── code.md             # Implementation
├── debug.md            # Troubleshooting
├── researcher.md       # Investigation
├── user_story.md       # Requirements analysis
├── expert_consultant.md # Technical review
├── fact_checker.md     # Validation
├── writer.md           # Documentation
└── devops.md           # Deployment

# Demo and test Phase 5 setup
python example_phase5.py
```

## Claude Code Permissions

The workflow launches Claude Code with comprehensive development permissions:

```bash
claude -p --verbose --model sonnet --allowedTools \
  "read,write,edit,multiEdit,glob,grep,ls,bash,git,npm,cargo,python,pytest,webSearch,task"
```

**Tool Categories:**
- **File Operations**: read, write, edit, multiEdit
- **Code Search**: glob, grep, ls
- **Shell Commands**: bash (for cp, mv, grep, etc.)
- **Version Control**: git
- **Package Managers**: npm, cargo
- **Python Tools**: python, pytest
- **Research**: webSearch, task

## Example Usage

```bash
# Start work on issue
$ python jira_task.py PROJ-123

🚀 Starting work on JIRA issue: PROJ-123
📋 Retrieving issue details...
🌿 Creating feature branch...
💬 Updating JIRA with development status...
✅ Ready to work on PROJ-123: Implement user authentication
📋 Issue: Implement user authentication
🌿 Branch: feature/proj-123-implement-user-authentication

🤖 Launching Claude Code development assistant...
📅 Creating development plan...
[Claude Code analyzes codebase and creates plan]

🚀 Ready for development! Claude Code will assist you.
Available commands:
  - 'analyze': Analyze codebase for relevant files
  - 'implement': Get implementation suggestions
  - 'test': Create or run tests
  - 'review': Review changes before commit
  - 'done': Mark issue complete and create PR

==================================================

👷 [PROJ-123] What would you like to do? (help/analyze/implement/test/review/done/quit): 
```

## Dependencies

### Core Dependencies
- Python 3.7+
- requests
- python-dotenv
- pydantic
- git (command line tool)

### Phase 2 Enhanced Features
- GitHub CLI (gh) for automated PR creation
- Additional Python packages for enhanced functionality

### Installation
```bash
# Core dependencies
pip install requests python-dotenv pydantic

# Install GitHub CLI for PR creation
# macOS: brew install gh
# Ubuntu: apt install gh  
# Windows: winget install GitHub.cli

# Authenticate GitHub CLI
gh auth login
```

## File Structure

```
jira_task/
├── __init__.py               # Package initialization with all phases
├── config.py                 # Configuration management
├── jira_client.py            # JIRA API client
├── git_integration.py        # Git operations
├── jira_task.py              # Main workflow implementation
├── enhanced_workflow.py      # Phase 2 enhanced features
├── advanced_automation.py    # Phase 3 advanced features
├── enterprise_workflow.py    # Phase 4 enterprise features
├── webhook_integration.py    # Phase 4 webhook processing
├── ai_code_review.py         # Phase 4 AI code review
├── team_management.py        # Phase 4 team collaboration
├── external_integrations.py  # Phase 4 external tools
├── pr_creator.py             # GitHub PR creation utility
├── analytics.py              # Analytics and reporting
├── jira_projects.yml         # Multi-project configuration
├── team_config.yml           # Team management configuration
├── example.py                # Example usage and testing
└── README.md                # This documentation
```

## JIRA API Token Setup

1. Go to [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click "Create API token"
3. Give it a label (e.g., "Claude Code Workflow")
4. Copy the token to your `.env` file

## Troubleshooting

### Configuration Issues
```bash
# Test configuration
python example.py --test-all
```

### JIRA Connection Issues
- Verify JIRA_BASE_URL is correct
- Check API token is valid
- Ensure username/email is correct

### Git Issues
- Ensure you're in a git repository
- Check git is installed and configured
- Verify GitHub CLI (gh) is installed for PR creation

### Permission Issues
- Verify JIRA permissions for the project
- Check if issue is assigned to you
- Ensure git repository has push permissions

## Development

To modify or extend the workflow:

1. **Add new commands**: Extend `_interactive_development_mode()` in `jira_task.py`
2. **Modify JIRA operations**: Update methods in `jira_client.py`
3. **Change git behavior**: Modify `git_integration.py`
4. **Add configuration options**: Update `config.py`

## License

This workflow is part of the Claude Code agent-flows repository.