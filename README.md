# **AgenticScrum: A Framework for Structured AI-Driven Code Generation**

**AgenticScrum** is an open-source framework designed to bring structure, efficiency, and agile principles to software development powered by AI agents. It provides a comprehensive setup utility, defines clear roles for AI agents within a Scrum-like workflow, and integrates best practices for coding standards and project management.

---

## **Table of Contents**

* [Overview](#overview)  
* [Core Principles](#core-principles)  
* [Key Features](#key-features)  
* [Getting Started](#getting-started)  
  * [The Setup Utility](#the-setup-utility)  
  * [Retrofitting Existing Projects](#retrofitting-existing-projects)  
* [Project Directory Structure](#project-directory-structure)  
* [The AgenticScrum Workflow](#the-agenticscrum-workflow)  
  * [Agent Personas & Rules](#agent-personas--rules)  
  * [Priming Scripts](#priming-scripts)  
  * [Coding Standards](#coding-standards)  
  * [Workflow Orchestration](#workflow-orchestration)  
  * [Human-in-the-Loop (HITL)](#human-in-the-loop-hitl)  
* [Multi-Stack and Multi-Repository Support](#multi-stack-and-multi-repository-support)  
* [Inspiration](#inspiration)  
* [Benefits](#benefits)  
* [Limitations](#limitations)  
* [Future Directions](#future-directions)  
* [Additional Resources](#additional-resources)  
  * [Conceptual Design Document](#conceptual-design-document)  
  * [Tutorial & Getting Started Guide](#tutorial--getting-started-guide)  
  * [Retrofitting Guide](#retrofitting-guide)  
* [Contributing](#contributing)  
* [License](#license)

---

## **Overview**

The rise of sophisticated AI agents for code generation offers immense potential but often lacks standardized processes, leading to challenges in managing multiple agents, ensuring code quality, and scaling efforts.

**AgenticScrum** addresses these challenges by:

* Integrating core Scrum methodologies with specialized AI agents.  
* Providing a setup utility to automate the creation of a standardized project structure.  
* Generating foundational rules and persona definitions for AI agents.  
* Incorporating coding standards and priming scripts to initialize agent behavior.

This framework aims to bring predictability, quality control, and collaborative structure to AI-assisted software development.

## **Core Principles**

AgenticScrum is built upon the following foundational principles:

1. **Simplicity:** Easy to understand and implement, minimizing cognitive overhead.  
2. **Power:** Capable of handling complex code generation tasks through specialized, collaborative AI agents.  
3. **Ease of Use:** Intuitive setup and operational experience, primarily via a Command-Line Interface (CLI).  
4. **Open-Source:** All components are open-source to encourage community contribution, transparency, and evolution.  
5. **Scrum Alignment:** Adapts key Scrum elements (artifacts, roles, events) to an agentic context, providing a familiar structure for agile teams.

## **Key Features**

* **Automated Project Scaffolding:** CLI utility to instantly set up a standardized project.  
* **Fullstack Support:** Create projects with multiple languages and frameworks in a single command.
* **Defined AI Agent Roles:** Pre-defined personas (ProductOwnerAgent, ScrumMasterAgent, DeveloperAgent, QAAgent, SecurityAuditAgent) with customizable rules.  
* **Scrum-Inspired Workflow:** Structured sprints, task decomposition, and agent collaboration mimicking agile practices.  
* **Integrated Coding Standards:** Mechanisms for defining and enforcing project-specific coding conventions and quality.  
* **Framework-Specific Templates:** Built-in support for FastAPI, Express, React, Spring Boot, and more.
* **Priming Scripts:** Contextual initialization for agents to guide their behavior effectively.  
* **Human-in-the-Loop Design:** Critical human oversight integrated into the workflow for validation and decision-making.  
* **Multi-Stack & Multi-Repo Adaptability:** Flexible structure to support diverse technology stacks and complex project organizations.  
* **Checklist-Driven Quality:** Utilizes checklists (e.g., Definition of Done, Code Review) to ensure thoroughness and consistency.
* **MCP Integration (NEW):** Enhanced agent capabilities through Model Context Protocol:
  * **Persistent Memory:** Agents learn and improve from past experiences across sessions
  * **Advanced Web Search:** Access to current information via Perplexity API integration
  * **Secure API Management:** Environment-based configuration keeps credentials safe

## **Getting Started**

### **The Setup Utility**

The primary way to start an AgenticScrum project is by using the agentic-scrum-setup CLI utility. To simplify the complex command-line arguments, we provide an `init.sh` helper script.

**Quick Start with init.sh:**

```bash
# Install the utility (first time only)
./init.sh install

# Create a new project interactively
./init.sh new

# Or use quick setup with defaults
./init.sh quick MyNewWebApp
```

**Direct CLI Usage:**

Single language project:
```bash
agentic-scrum-setup init \
  --project-name MyNewWebApp \
  --language python \
  --framework fastapi \
  --agents poa,sma,deva_python,qaa,saa \
  --llm-provider anthropic \
  --default-model claude-sonnet-4-0
```

Fullstack project:
```bash
agentic-scrum-setup init \
  --project-name MyFullstackApp \
  --project-type fullstack \
  --language python \
  --backend-framework fastapi \
  --frontend-language typescript \
  --frontend-framework react \
  --agents poa,sma,deva_python,deva_typescript,qaa,saa \
  --llm-provider anthropic \
  --default-model claude-sonnet-4-0
```

This command will:

1. Create a new project directory (e.g., MyNewWebApp/).  
2. Generate a standardized hierarchical directory structure (see below).  
3. Create agent configuration files (persona\_rules.yaml) and priming\_script.md for each specified agent.  
4. Generate template documents for coding standards (coding\_standards.md) and linter configurations.  
5. Create an agentic\_config.yaml for global project settings.  
6. Scaffold checklist documents like definition\_of\_done.md.

If run interactively (e.g., agentic-scrum-setup init), the CLI will prompt for necessary information.

### **Claude Code Integration**

AgenticScrum is optimized for use with Claude Code (claude.ai/code). When using Claude Code:

**Quick Setup:**
```bash
# Use the --claude-code flag for optimal defaults
agentic-scrum-setup init --project-name MyProject --language python --agents poa,sma,deva_python,qaa --claude-code
```

**Key Features:**
- Automatic selection of Anthropic provider and claude-sonnet-4-0 model
- Model parameters (temperature, max_tokens) are controlled by Claude Code IDE
- Agent configurations include model recommendations for different tasks
- Seamless integration with Claude Code's model switching commands

**Model Selection Strategy:**
- Use `/model opus` for complex planning and architecture tasks
- Use `/model sonnet` (default) for development and implementation
- Use `/model haiku` for quick, simple tasks

### **MCP Integration (Model Context Protocol)**

AgenticScrum now supports MCP servers to enhance agent capabilities beyond Claude Code's native features:

**Enable MCP Features:**
```bash
# Create project with MCP integration
agentic-scrum-setup init \
  --project-name "MyEnhancedProject" \
  --language python \
  --agents poa,sma,deva_python,qaa \
  --enable-mcp \
  --enable-search

# Configure API keys (required for search)
export PERPLEXITY_API_KEY="your-key-here"
```

**MCP Benefits:**
- **Persistent Memory**: Agents remember past decisions, patterns, and solutions across sessions
- **Advanced Search**: Global web search via Perplexity (not limited to US like native search)
- **Learning Agents**: Performance improves over time as agents build knowledge
- **Secure Configuration**: API keys managed through environment variables

For detailed MCP setup, see the [MCP Integration Guide](docs/MCP_INTEGRATION_GUIDE.md).

### **Retrofitting Existing Projects**

AgenticScrum can be gradually integrated into existing codebases without disrupting current workflows. This approach is ideal for teams who want to leverage AI agents without starting from scratch.

**Quick Start for Retrofitting:**

```bash
# Assess your existing project
python scripts/retrofit_project.py assess --path /path/to/your/project

# Generate a customized retrofit plan
python scripts/retrofit_project.py plan --path /path/to/your/project

# Initialize agents for your specific tech stack
python scripts/retrofit_project.py init-agents --path /path/to/your/project \
  --languages python,javascript --frameworks django,react
```

**Key Benefits of Retrofitting:**
- **Non-disruptive integration** - Keep your existing structure and workflows
- **Gradual adoption** - Start with one agent, expand as comfortable
- **Respect existing patterns** - Agents learn and match your code style
- **Preserve team dynamics** - Enhance rather than replace current processes

For detailed retrofitting instructions, see the [Retrofitting Guide](docs/RETROFITTING_GUIDE.md).

## **Project Directory Structure**

A well-defined structure is crucial. AgenticScrum proposes the following:

```
MyNewWebApp/  
├── agentic_config.yaml       # Global AgenticScrum settings (LLM provider, API keys, etc.)  
├── README.md                 # Project overview and setup  
├── .gitignore                # Standard git ignore  
├── requirements.txt          # Or pyproject.toml, package.json, etc. for dependencies  
│  
├── agents/                   # Agent-specific configurations  
│   ├── product_owner_agent/  
│   │   ├── persona_rules.yaml  # Role, goals, rules, LLM config for POA  
│   │   └── priming_script.md   # Initial prompt for POA  
│   ├── scrum_master_agent/   # Similar structure for SMA  
│   ├── developer_agent/      # Can have sub-specializations (e.g., python_expert/)  
│   │   └── python_expert/  
│   │       ├── persona_rules.yaml  
│   │       └── priming_script.md  
│   ├── qa_agent/             # Similar structure for QAA  
│   └── security_audit_agent/ # Similar structure for SAA  
│  
├── src/                      # Source code generated by DeveloperAgents  
│   ├── backend/              # Example for full-stack  
│   └── frontend/             # Example for full-stack  
│  
├── tests/                    # Unit, integration, and E2E tests (mirroring /src)  
│  
├── docs/                     # Project documentation  
│   ├── requirements/  
│   │   ├── product_backlog.md  
│   │   └── user_stories/  
│   │       └── sprint_N/     # User stories for each sprint  
│   ├── architecture/         # Architecture diagrams, design decisions  
│   └── sprint_reports/       # Daily logs, review summaries, retrospective notes  
│  
├── standards/                # Coding standards and quality guidelines  
│   ├── coding_standards.md   # Human-readable coding conventions  
│   └── linter_configs/       # Config files for linters (e.g.,.eslintrc, pyproject.toml for flake8/black)  
│  
├── checklists/               # Actionable checklists  
│   ├── definition_of_done.md  
│   ├── code_review_checklist.md  
│   ├── sprint_planning_checklist.md  
│   └── security_audit_checklist.md  
│  
└── scripts/                  # Utility scripts for automation (e.g., run_linters.sh)
```

This structure is inspired by best practices from frameworks like CrewAI [1] and LangGraph [3].

## **The AgenticScrum Workflow**

### **Agent Personas & Rules**

Effective agentic systems rely on well-defined "persona engineering."

* **Core Agents:**  
  * **ProductOwnerAgent (POA):** Manages product backlog, creates user stories.  
  * **ScrumMasterAgent (SMA):** Facilitates the process, monitors interactions, flags impediments.  
  * **DeveloperAgent (DevA):** Generates code and unit tests based on user stories. Can be specialized (e.g., PythonDeveloperAgent).  
  * **QAAgent (QAA):** Reviews code, runs tests, ensures adherence to Definition of Done.  
  * **SecurityAuditAgent (SAA):** Conducts comprehensive security audits, identifies vulnerabilities, ensures secure coding practices.  
* **persona_rules.yaml:** Located in each agent's directory (e.g., /agents/developer_agent/persona_rules.yaml), this file defines:  
  * role: The agent's primary function.  
  * goal: The agent's main objective.  
  * backstory: Context for the LLM to adopt the persona.  
  * llm\_config: Specific LLM settings (model, temperature).  
  * capabilities: List of skills.  
  * rules: Specific operational heuristics and constraints.  
  * knowledge\_sources: Pointers to relevant documents (standards, checklists).  
  * tools: (Conceptual) Placeholder for future tool integrations.  
This detailed configuration, inspired by practices in BMAD-METHOD [5], guides the LLM's behavior.

### **Priming Scripts**

Located in [agent_dir]/priming_script.md, these scripts are the initial textual input to the LLM:

* Invoke the specific agent persona by referencing its persona\_rules.yaml.  
* Set the context and define the immediate task or mission.  
* Point to necessary resources (user stories, coding standards).  
* Specify output expectations and contingency instructions.

### **Coding Standards**

AgenticScrum integrates coding standards through:

1. **standards/coding_standards.md:** A human-readable document detailing naming conventions, commenting guidelines, style guides, etc.  
2. **standards/linter_configs/:** Configuration files for automated linters (e.g., Flake8, ESLint) and formatters (e.g., Black, Prettier).  

Enforcement occurs via:  
* Explicit rules in agent persona_rules.yaml.  
* Reinforcement in priming_script.md.  
* Checklist items in checklists/code_review_checklist.md for the QAAgent.

### **Workflow Orchestration**

The conceptual sprint lifecycle includes:

1. **Sprint Planning:** POA generates user stories from high-level goals.  
2. **User Story Assignment:** Stories assigned to appropriate DevAs.  
3. **Development:** DevAs generate code and unit tests.  
4. **Security Audit:** SAA performs comprehensive security review of the code.  
5. **Code Review & QA:** QAA reviews code, runs tests, verifies against Definition of Done.  
6. **Daily Stand-up (Conceptual):** Agents report status, SMA logs progress/impediments.  
7. **Sprint Review:** Human stakeholders review completed work.  
8. **Sprint Retrospective:** Analyze agent performance and process for improvements.

Future automation can leverage frameworks like CrewAI [6], AutoGen [6], or LangGraph [6].

### **Human-in-the-Loop (HITL)**

Human oversight is critical [9]. Responsibilities include:

* Setting strategic direction.  
* Reviewing and approving agent outputs (especially user stories, final code).  
* Resolving complex ambiguities.  
* Making critical design decisions.  
* Continuously refining agent personas and prompts.

## **Multi-Stack and Multi-Repository Support**

AgenticScrum is designed for flexibility:

* **Fullstack Projects:**
  * Use `--project-type fullstack` to create projects with separate backend and frontend
  * Automatically creates `/backend` and `/frontend` directories with appropriate structures
  * Generates multiple DeveloperAgents for different languages (e.g., `deva_python` for backend, `deva_typescript` for frontend)
  * Separate standards and linter configurations for each stack in `/standards/backend/` and `/standards/frontend/`
  
* **Multiple Tech Stacks (Monorepo):**  
  * The /standards directory can house separate coding_standards.md and linter_configs/ for each technology (e.g., /standards/python/, /standards/javascript/).  
  * The /src and /tests directories can be subdivided (e.g., /src/backend/, /src/frontend/).  
  * DeveloperAgents are specialized (e.g., PythonDeveloperAgent, ReactDeveloperAgent), with their persona_rules.yaml pointing to the relevant stack-specific standards and source directories.  
  * Tools like Nx, Lerna, or Rush can complement AgenticScrum for managing complex monorepos.  
  
* **Multiple Repositories (Polyrepo):**  
  * Each repository can have its own lightweight AgenticScrum configuration (relevant standards, agent personas).  
  * Cross-repository orchestration requires higher-level coordination (e.g., a "ProjectCoordinatorAgent" or human oversight) and potentially tools like mani or gita.

## **Inspiration**

AgenticScrum draws inspiration from pioneering open-source frameworks, adapting their successful patterns into a Scrum-like context:

* **BMAD-METHOD [5]:**  
  Influences persona engineering, detailed prompting, and the crucial role of checklists.  
* **CrewAI [6]:**  
  Informs the standardized project structure, YAML-based agent definitions, and role-based agent collaboration.  
* **AutoGen [6]:**  
  Provides models for multi-agent communication and orchestration.  
* **LangGraph [6]:**  
  Offers paradigms for complex, stateful multi-agent interactions.

## **Benefits**

* **Increased Efficiency & Speed:** Automates parts of coding, documentation, and testing [9].  
* **Improved Consistency:** Standardized personas, rules, and coding standards.  
* **Enhanced Code Quality (Potentially):** Systematic QA by QAAgents and feedback loops [9].  
* **Improved Security:** Automated security audits by SecurityAuditAgent to identify vulnerabilities early.  
* **Scalability:** Structure for distributing tasks among multiple AI agents [9].  
* **Structured Agentic Development:** Methodical process for AI-assisted projects.  
* **Knowledge Centralization:** Explicit definition of personas, rules, and standards.

## **Agent Optimization and Feedback Loops**

AgenticScrum includes a comprehensive system for continuously improving agent performance through feedback loops and automated optimization. This addresses one of the key limitations - the dependence on well-crafted configurations.

### **Key Components:**

* **Performance Metrics Collection**: Automated tracking of code quality, complexity, coverage, and other metrics
* **Feedback Forms**: Structured templates for collecting human feedback on agent performance
* **Automated Analysis**: Scripts that identify patterns in feedback and suggest configuration improvements
* **Configuration Updates**: Tools to apply improvements to persona_rules.yaml and priming_script.md

### **Documentation:**
- [Agent Optimization Guide](docs/AGENT_OPTIMIZATION.md) - Comprehensive guide to crafting effective personas and priming scripts
- [Feedback Workflow](docs/FEEDBACK_WORKFLOW.md) - Step-by-step process for implementing feedback loops
- [Agent Feedback Form](checklists/agent_feedback_form.md) - Template for collecting structured feedback

### **Quick Start:**
```bash
# Collect metrics for agent-generated code
python scripts/collect_agent_metrics.py --agent deva_python --file src/api/users.py --save

# Analyze feedback and generate recommendations
python scripts/update_agent_config.py recommend --agent deva_python

# Apply recommended updates (dry run)
python scripts/update_agent_config.py apply --agent deva_python --dry-run
```

## **Limitations**

* **LLM "Hallucinations":** Requires robust QA and human oversight.  
* **Dependence on Prompt Quality:** Effectiveness hinges on well-crafted persona_rules.yaml and priming_script.md. *(Mitigated by feedback loops and optimization system)*  
* **Agent Management Overhead:** Coordinating multiple agents can be complex.  
* **Current LLM Reasoning Limits:** May struggle with highly novel or abstract problems.  
* **Cost of LLM API Usage:** Can be significant for cloud-based LLMs.  
* **Integration Challenges:** Integrating AI-generated code into existing complex systems.

## **Future Directions**

* **Advanced Orchestration Engine:** Leveraging frameworks like CrewAI, AutoGen, or LangGraph.  
* **Enhanced Tool Integration:** Enabling agents to actively use linters, test runners, VCS, APIs.  
* **Feedback Loops & Agent Learning:** Implementing RAG, learning from human feedback.  
* **Sophisticated Agent Specializations & Collaboration Patterns.**  
* **Community-Driven Development:** Shared repository of personas, rules, and tool integrations.

## **Additional Resources**

### **Conceptual Design Document**

For a comprehensive understanding of the AgenticScrum framework's theoretical foundations and detailed design principles, please refer to [Design.md](Design.md). This document provides:

* In-depth exploration of the framework's conceptual architecture
* Detailed agent persona engineering principles
* Advanced workflow orchestration patterns
* Multi-agent collaboration strategies
* Comprehensive project structure rationale

### **Tutorial & Getting Started Guide**

If you're looking for a hands-on, step-by-step guide to building your first AgenticScrum project, check out [Tutorial.md](Tutorial.md). This tutorial walks you through:

* Building a full-stack cattle ranching desktop application
* Setting up a FastAPI backend with proper structure
* Creating an Electron + React frontend
* Integrating with Docker for containerized development
* Practical examples of using AgenticScrum agents in development

### **Retrofitting Guide**

For teams with existing projects who want to adopt AgenticScrum incrementally, see the [Retrofitting Guide](docs/RETROFITTING_GUIDE.md). This guide covers:

* Assessing your existing codebase for AgenticScrum compatibility
* Creating a phased adoption plan
* Configuring agents to respect existing patterns
* Integrating with current CI/CD pipelines
* Managing the transition with minimal disruption

## **Contributing**

AgenticScrum is an open-source project, and contributions are highly welcome! Whether it's improving the setup utility, refining agent personas, adding support for new languages/frameworks, or enhancing documentation, your input is valuable.

Please refer to CONTRIBUTING.md for guidelines on how to contribute.

## **License**

This project is intended to be licensed under an open-source license (e.g., MIT License). See the LICENSE file for details once finalized.

#### **Works cited**

1. Building Multi-Agent Systems With CrewAI - A Comprehensive Tutorial - Firecrawl, accessed June 11, 2025, [https://www.firecrawl.dev/blog/crewai-multi-agent-systems-tutorial](https://www.firecrawl.dev/blog/crewai-multi-agent-systems-tutorial)  
2. How to build a game-building agent system with CrewAI - WorkOS, accessed June 11, 2025, [https://workos.com/blog/how-to-build-a-game-building-agent-system-with-crewai](https://workos.com/blog/how-to-build-a-game-building-agent-system-with-crewai)  
3. Application structure - GitHub Pages, accessed June 11, 2025, [https://langchain-ai.github.io/langgraph/concepts/application_structure/](https://langchain-ai.github.io/langgraph/concepts/application_structure/)  
4. 10 Langgraph Projects to Build Intelligent AI Agents - ProjectPro, accessed June 11, 2025, [https://www.projectpro.io/article/langgraph-projects-and-examples/1124](https://www.projectpro.io/article/langgraph-projects-and-examples/1124)  
5. BMAD-METHOD V2 in an Evolution IMO - The POWER of Custom Agents, Smaller Docs, and CHECKLISTS! - How To - Cursor - Community Forum, accessed June 11, 2025, [https://forum.cursor.com/t/bmad-method-v2-in-an-evolution-imo-the-power-of-custom-agents-smaller-docs-and-checklists/87218](https://forum.cursor.com/t/bmad-method-v2-in-an-evolution-imo-the-power-of-custom-agents-smaller-docs-and-checklists/87218)  
6. Top 10 Open-Source AI Agent Frameworks to Know in 2025, accessed June 11, 2025, [https://opendatascience.com/top-10-open-source-ai-agent-frameworks-to-know-in-2025/](https://opendatascience.com/top-10-open-source-ai-agent-frameworks-to-know-in-2025/)  
7. How to use the Microsoft Autogen framework to Build AI Agents? - ProjectPro, accessed June 11, 2025, [https://www.projectpro.io/article/autogen/1139](https://www.projectpro.io/article/autogen/1139)  
8. AutoGen Tutorial: Build Multi-Agent AI Applications - DataCamp, accessed June 11, 2025, [https://www.datacamp.com/tutorial/autogen-tutorial](https://www.datacamp.com/tutorial/autogen-tutorial)  
9. Agentic Workflows: Everything You Need to Know - Automation Anywhere, accessed June 11, 2025, [https://www.automationanywhere.com/rpa/agentic-workflows](https://www.automationanywhere.com/rpa/agentic-workflows)  
10. Top Agent Workflow Configuration Best Practices for Optimal Efficiency | NICE, accessed June 11, 2025, [https://www.nice.com/info/agent-workflow-configuration-best-practices](https://www.nice.com/info/agent-workflow-configuration-best-practices)  
11. bmadcode/BMAD-METHOD: Breakthrough Method for ... - GitHub, accessed June 11, 2025, [https://github.com/bmadcode/BMAD-METHOD](https://github.com/bmadcode/BMAD-METHOD)  
12. BMad Code - YouTube, accessed June 11, 2025, [https://www.youtube.com/@BMadCode/community](https://www.youtube.com/@BMadCode/community)
