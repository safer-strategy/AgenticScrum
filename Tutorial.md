### **Tutorial: Building a Full-Stack Cattle Ranching Desktop App**

Welcome! This tutorial will guide you, step-by-step, through setting up a complete development environment for a full-stack application. We'll create a desktop app for macOS to manage a cattle ranch. 🤠

By the end, you'll have a running application with a **FastAPI** backend and an **Electron** with **React** frontend, all managed within a **Docker** environment and structured using the **AgenticScrum** methodology.

#### **Prerequisites**

Before we start, make sure you have the following installed on your macOS machine:
* **Python** (version 3.10 or newer) with pip
* **Node.js** (version 18 or newer), which includes `npm`
* **Docker Desktop** (with Docker Compose)
* A code editor like **Visual Studio Code**
* **Git** (to clone the AgenticScrum repository)

---

### **Step 1: Set Up AgenticScrum and Create Your Project**

First, let's get the AgenticScrum framework and use it to create our project.

#### **1a. Clone and Install AgenticScrum**

```bash
# Clone the AgenticScrum repository
git clone https://github.com/yourusername/AgenticScrum.git
cd AgenticScrum

# Install the setup utility using the helper script
./init.sh install
```

#### **1b. Create Your Project Using init.sh**

The `init.sh` helper script makes it easy to create projects without remembering complex command-line arguments. Let's use it to create our cattle ranching app:

```bash
# Interactive mode - the script will guide you through all options
./init.sh new
```

When prompted, enter the following:
- **Project Type:** Fullstack project (option 2)
- **Project Name:** RanchHand
- **Backend Language:** Python (option 1)
- **Backend Framework:** FastAPI (option 1)
- **Frontend Language:** TypeScript (option 2)
- **Frontend Framework:** React (option 1)
- **Agents:** poa,sma,deva_python,deva_typescript,qaa,saa (or press Enter for smart defaults)
- **LLM Provider:** Choose based on your API keys (OpenAI, Anthropic, etc.)

**Alternative: Quick Setup**

If you prefer a one-liner with defaults:
```bash
./init.sh quick RanchHand
```

**Alternative: Direct CLI Command**

For those who prefer the direct approach:
```bash
agentic-scrum-setup init \
  --project-name "RanchHand" \
  --project-type "fullstack" \
  --language "python" \
  --backend-framework "fastapi" \
  --frontend-language "typescript" \
  --frontend-framework "react" \
  --agents "poa,sma,deva_python,deva_typescript,qaa,saa" \
  --llm-provider "openai" \
  --default-model "gpt-4-turbo-preview"
```

The setup utility creates a new folder named `RanchHand` with separate backend and frontend directories, framework-specific configurations, and all agent personas for both Python and TypeScript development.

---

### **Step 2: Meet Your Environment Manager: `init.sh`**

Navigate into your new project directory: `cd RanchHand`.

Inside, you'll find `init.sh`. This is your "pretty awesome", centralized script for managing the entire development environment. It handles starting, stopping, and monitoring all the services defined in `docker-compose.yml`.

To see what it can do, run:

```bash
./init.sh help
```

You'll see a themed menu with all the available commands. This is your go-to tool for managing the project's lifecycle.

---

### **Step 3: Build the FastAPI Backend**

Our backend will be a simple API that serves data about our cattle.

1.  **Define the Data Model:** Open `/backend/app/models.py` and add a simple data model for a cow.

    ```python
    # /backend/app/models.py
    from pydantic import BaseModel

    class Cattle(BaseModel):
        tag_id: str
        breed: str
        age: int
        weight_kg: float
    ```

2.  **Create the API Endpoint:** Now, let's create an endpoint in `/backend/app/main.py` to return a list of cattle.

    ```python
    # /backend/app/main.py
    from fastapi import FastAPI
    from .models import Cattle

    app = FastAPI()

    # Sample data
    db_cattle = [
        Cattle(tag_id="A001", breed="Angus", age=3, weight_kg=550.5),
        Cattle(tag_id="H002", breed="Hereford", age=4, weight_kg=610.0),
    ]

    @app.get("/api/cattle", response_model=list[Cattle])
    def get_cattle_list():
        return db_cattle
    ```

3.  **Add Dependencies:** Make sure your backend's `requirements.txt` includes FastAPI and its server.

    ```text
    # /backend/requirements.txt
    fastapi
    uvicorn[standard]
    ```

---

### **Step 4: Build the React Frontend**

The frontend is built with React and TypeScript to display our cattle management interface.

1.  **Configure TypeScript:** The TypeScript configuration is already set up in `/frontend/tsconfig.json`.

2.  **Create a React Component:** Let's create a component in `/frontend/src/App.tsx` to fetch and display the cattle data.

    ```tsx
    // /frontend/src/App.tsx
    import React, { useState, useEffect } from 'react';
    
    interface Cattle {
      tag_id: string;
      breed: string;
      age: number;
      weight_kg: number;
    }

    function App() {
      const [cattle, setCattle] = useState<Cattle[]>([]);

      useEffect(() => {
        // Fetch from the backend API
        fetch('http://localhost:8000/api/cattle')
          .then(response => response.json())
          .then((data: Cattle[]) => setCattle(data))
          .catch(error => console.error('Error fetching cattle data:', error));
      }, []);

      return (
        <div className="App">
          <h1>RanchHand Cattle Manager</h1>
          <table>
            <thead>
              <tr>
                <th>Tag ID</th>
                <th>Breed</th>
                <th>Age (years)</th>
                <th>Weight (kg)</th>
              </tr>
            </thead>
            <tbody>
              {cattle.map(cow => (
                <tr key={cow.tag_id}>
                  <td>{cow.tag_id}</td>
                  <td>{cow.breed}</td>
                  <td>{cow.age}</td>
                  <td>{cow.weight_kg}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }

    export default App;
    ```

---

### **Step 5: Connect Everything with Docker Compose**

The magic that connects our two services is the `docker-compose.yml` file. It was generated for us by the setup utility. It defines two main services: `backend` and `frontend`.

* **`backend`**: Builds a Docker image from `/backend`, installs the Python dependencies, and runs the FastAPI server on port 8000.
* **`frontend`**: Builds from `/frontend`, installs `npm` dependencies, and starts the React development server on port 3000.

Docker Compose creates a virtual network where these services can easily communicate with each other.

---

### **Step 6: Launch the Application!**

This is the moment of truth. To build the Docker images, install all dependencies, and start both the backend and frontend servers, run the single command from your project's root directory:

```bash
./init.sh up
```

After the build process completes, you will see logs from both services. Navigate to http://localhost:3000 in your browser to see the React frontend displaying the list of cattle fetched live from your FastAPI backend.

🎉 **Congratulations!** You now have a fully functional, containerized, full-stack development environment set up and structured according to our AgenticScrum guidelines.

### **Next Steps: Developing with Agents**

From here, you would use the AgenticScrum framework to add new features.

* A **ProductOwnerAgent** would manage the `product_backlog.md`.
* You would create a new user story for a feature, like "Add a form to register a new cow."
* The **DeveloperAgent** (our Claude persona) would be prompted to write the new FastAPI endpoint and React form components, using the `CLAUDE.md` file for context on project standards.
* The **SecurityAuditAgent** would perform a comprehensive security review, checking for vulnerabilities like:
  - Input validation issues in the cow registration form
  - SQL injection vulnerabilities in database queries
  - Proper authentication and authorization
  - Secure handling of sensitive data
* The **QAAgent** would use the `code_review_checklist.md` to ensure the new code meets quality standards.

---

### **Appendix: Using init.sh for Different Scenarios**

The `init.sh` helper script provides several convenient ways to create AgenticScrum projects. Here are some common scenarios:

#### **Creating a Fullstack Project**

```bash
./init.sh new
# Select: Fullstack project (option 2)
# Backend: Python with FastAPI
# Frontend: TypeScript with React
# Agents: poa,sma,deva_python,deva_typescript,qaa,saa
```

#### **Creating a Single Language React Project**

```bash
./init.sh new
# Select: Single language project (option 1)
# Select: TypeScript (option 3)
# Select: React framework (option 2)
# Agents: poa,sma,deva_typescript,qaa,saa
```

#### **Creating an Electron Desktop App**

```bash
./init.sh new
# Select: JavaScript (option 2)
# Select: Electron framework (option 4)
```

#### **Custom Setup with All Options**

```bash
./init.sh custom
# This mode allows you to specify:
# - Custom output directory
# - Specific model configurations
# - Advanced agent selections
```

#### **Direct CLI for Fullstack Projects**

```bash
# Java Spring Boot backend with React frontend
agentic-scrum-setup init \
  --project-name "EnterpriseApp" \
  --project-type fullstack \
  --language java \
  --backend-framework spring \
  --frontend-language typescript \
  --frontend-framework react \
  --agents poa,sma,deva_java,deva_typescript,qaa,saa \
  --llm-provider openai \
  --default-model gpt-4-turbo-preview

# Node.js Express backend with Vue frontend
agentic-scrum-setup init \
  --project-name "ModernWebApp" \
  --project-type fullstack \
  --language typescript \
  --backend-framework express \
  --frontend-language typescript \
  --frontend-framework vue \
  --agents poa,sma,deva_typescript,qaa,saa \
  --llm-provider anthropic \
  --default-model claude-3-opus-20240229
```

#### **Viewing Available Options**

```bash
./init.sh help
```

This displays:
- All supported languages (Python, JavaScript, TypeScript, Java, Go, Rust, C#, PHP, Ruby)
- Available frameworks for each language
- All agent types and their purposes
- Command examples

#### **Tips for Using init.sh**

1. **First Time Setup**: Always run `./init.sh install` first to ensure the agentic-scrum-setup utility is installed.

2. **Framework Selection**: The script automatically shows relevant frameworks based on your language choice.

3. **Agent Selection**: The script suggests appropriate default agents based on your language choice.

4. **LLM Configuration**: Have your API keys ready when selecting your LLM provider.

5. **Project Location**: By default, projects are created in the current directory. Use the custom mode to specify a different location.

---

### **Optimizing Agent Performance**

AgenticScrum includes powerful tools for continuously improving agent performance through feedback loops. Here's how to use them:

#### **Step 1: Collect Performance Metrics**

After your agents generate code, collect metrics:

```bash
# Collect metrics for a specific file
python scripts/collect_agent_metrics.py \
  --agent deva_python \
  --file backend/app/api/cattle.py \
  --save

# View the metrics
cat metrics/agent_performance/deva_python_*.json
```

#### **Step 2: Provide Feedback**

When reviewing agent-generated code, fill out the feedback form:

```bash
# Copy and fill out the feedback form
cp checklists/agent_feedback_form.md feedback/deva_python_sprint15.md
# Edit with your feedback
```

#### **Step 3: Analyze Performance**

Run the feedback analyzer to identify patterns:

```bash
# Generate performance report
python scripts/feedback_analyzer.py \
  --agent deva_python \
  --output reports/

# View the report
cat reports/deva_python_performance_report.md
```

#### **Step 4: Apply Improvements**

Based on the analysis, update agent configurations:

```bash
# Get recommendations
python scripts/update_agent_config.py recommend --agent deva_python

# Review and apply updates
python scripts/update_agent_config.py apply --agent deva_python --dry-run
python scripts/update_agent_config.py apply --agent deva_python --confirm
```

#### **Example: Improving Error Handling**

If feedback shows the agent frequently misses error handling:

1. **Update persona_rules.yaml**:
```yaml
rules:
  - "ALWAYS wrap database operations in try-except blocks"
  - "ALWAYS provide specific error messages"
  - "ALWAYS log errors with context"
```

2. **Update priming_script.md**:
```markdown
## Error Handling Pattern
Always follow this pattern:
\```python
try:
    result = perform_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    raise HTTPException(status_code=400, detail=str(e))
\```
```

3. **Test the improvements**:
```bash
# Have the agent generate similar code
# Check if error handling is now included
```

### **Security Considerations with SecurityAuditAgent**

When including the SecurityAuditAgent (SAA) in your project, you get automated security reviews throughout development:

#### **What SAA Checks**

1. **Input Validation**
   - Form inputs are properly validated
   - SQL injection prevention
   - XSS protection
   - File upload security

2. **Authentication & Authorization**
   - Secure password storage
   - Session management
   - API endpoint protection
   - Role-based access control

3. **Data Protection**
   - Encryption in transit (HTTPS)
   - Secure data storage
   - Protection of sensitive information
   - Secure API key management

4. **Security Headers & Configuration**
   - CORS settings
   - Security headers (CSP, HSTS, etc.)
   - Error handling that doesn't leak information
   - Secure cookie settings

#### **Using SAA Effectively**

1. **Run Security Audits After Major Changes**
   ```bash
   # After implementing new features, prompt SAA to review
   "Please conduct a security audit of the new user registration feature"
   ```

2. **Review the Security Checklist**
   - Check `/checklists/security_audit_checklist.md`
   - Use it as a guide for manual reviews
   - Ensure all items are addressed before deployment

3. **Act on SAA Recommendations**
   - SAA provides severity levels (Critical, High, Medium, Low)
   - Address Critical and High issues immediately
   - Include security fixes in your Definition of Done

4. **Integrate with Development Workflow**
   - Run SAA after DeveloperAgent completes code
   - Run SAA before QAAgent final review
   - Include security findings in sprint retrospectives

### **Retrofitting an Existing Project**

If you have an existing project and want to adopt AgenticScrum gradually, here's a quick example:

#### **Step 1: Assess Your Project**

```bash
# From the AgenticScrum directory
python scripts/retrofit_project.py assess --path ~/my-existing-project

# This outputs:
# - Detected languages and frameworks
# - Complexity score
# - Recommended timeline
# - Risk assessment
```

#### **Step 2: Create Retrofit Plan**

```bash
python scripts/retrofit_project.py plan --path ~/my-existing-project
```

#### **Step 3: Initialize Agents**

```bash
# Start with just POA and one developer agent
python scripts/retrofit_project.py init-agents \
  --path ~/my-existing-project \
  --languages python \
  --frameworks django
```

#### **Step 4: Gradual Integration**

1. **Week 1-2**: Use POA to manage new feature requests
2. **Week 3-4**: Introduce DeveloperAgent for new code only
3. **Week 5-6**: Add QAAgent for code reviews
4. **Week 7+**: Expand to full agent ecosystem

#### **Example: Adding AgenticScrum to a Django Project**

```yaml
# ~/my-django-project/agentic_config.yaml
project_name: "MyDjangoApp"
project_type: "retrofit"
retrofit_mode: true

existing_structure:
  type: "django-standard"
  source_dirs: ["myapp/", "api/", "core/"]
  test_dirs: ["tests/"]
  
agents:
  enabled: ["poa", "deva_python", "qaa"]
  pilot_features: ["new-payment-api"]
  
integration:
  ci_cd: "github-actions"
  preserve_workflows: true
```

The agents will automatically learn your Django patterns and generate code that fits seamlessly with your existing codebase.

Happy coding with AgenticScrum! 🚀