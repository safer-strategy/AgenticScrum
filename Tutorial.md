Of course. Here is a full tutorial to guide a user in creating a full-stack cattle ranching application, setting up the development environment according to the guidelines we've established.

### **Tutorial: Building a Full-Stack Cattle Ranching Desktop App**

Welcome! This tutorial will guide you, step-by-step, through setting up a complete development environment for a full-stack application. We'll create a desktop app for macOS to manage a cattle ranch. 🤠

By the end, you'll have a running application with a **FastAPI** backend and an **Electron** with **React** frontend, all managed within a **Docker** environment and structured using the **AgenticScrum** methodology.

#### **Prerequisites**

Before we start, make sure you have the following installed on your macOS machine:
* **Python** (version 3.10 or newer)
* **Node.js** (version 18 or newer), which includes `npm`
* **Docker Desktop** (with Docker Compose)
* A code editor like **Visual Studio Code**
* Our custom **`agentic-scrum-setup`** utility (for this tutorial, we'll assume it's installed).

---

### **Step 1: Scaffold Your Project with AgenticScrum**

First, we'll generate the entire project structure using our setup utility. This ensures all the boilerplate, configuration, and agent personas are created correctly from the start.

Open your terminal and run the following command:

```bash
agentic-scrum-setup init \
  --project-name "RanchHand" \
  --language "python" \
  --agents "poa,sma,deva_claude_python,qaa"
```

This command creates a new folder named `RanchHand` with the complete directory structure, including configurations for our core agents and the Claude developer agent.

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

1.  **Define the Data Model:** Open `/src/backend/models.py` and add a simple data model for a cow.

    ```python
    # /src/backend/models.py
    from pydantic import BaseModel

    class Cattle(BaseModel):
        tag_id: str
        breed: str
        age: int
        weight_kg: float
    ```

2.  **Create the API Endpoint:** Now, let's create an endpoint in `/src/backend/main.py` to return a list of cattle.

    ```python
    # /src/backend/main.py
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
    # /src/backend/requirements.txt
    fastapi
    uvicorn[standard]
    ```

---

### **Step 4: Build the Electron + React Frontend**

The frontend is a desktop application built with Electron that displays a React user interface.

1.  **Configure Electron:** The main Electron process is configured in `/src/frontend/electron.js`. It's responsible for creating the application window and loading your React app.

2.  **Create a React Component:** Let's create a component in `/src/frontend/src/App.js` to fetch and display the cattle data.

    ```jsx
    // /src/frontend/src/App.js
    import React, { useState, useEffect } from 'react';

    function App() {
      const [cattle, setCattle] = useState([]);

      useEffect(() => {
        // In an Electron app, you fetch from the backend's Docker service URL
        fetch('http://localhost:8000/api/cattle')
          .then(response => response.json())
          .then(data => setCattle(data))
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

* **`backend`**: Builds a Docker image from `/src/backend`, installs the Python dependencies, and runs the FastAPI server on port 8000.
* **`frontend`**: Builds from `/src/frontend`, installs `npm` dependencies, and starts the React development server.

Docker Compose creates a virtual network where these services can easily communicate with each other.

---

### **Step 6: Launch the Application!**

This is the moment of truth. To build the Docker images, install all dependencies, and start both the backend and frontend servers, run the single command from your project's root directory:

```bash
./init.sh up
```

After the build process completes, you will see logs from both services. An Electron application window for "RanchHand" will automatically pop up on your screen, displaying the list of cattle fetched live from your FastAPI backend.

🎉 **Congratulations!** You now have a fully functional, containerized, full-stack development environment set up and structured according to our AgenticScrum guidelines.

### **Next Steps: Developing with Agents**

From here, you would use the AgenticScrum framework to add new features.

* A **ProductOwnerAgent** would manage the `product_backlog.md`.
* You would create a new user story for a feature, like "Add a form to register a new cow."
* The **DeveloperAgent** (our Claude persona) would be prompted to write the new FastAPI endpoint and React form components, using the `CLAUDE.md` file for context on project standards.
* The **QAAgent** would use the `code_review_checklist.md` to ensure the new code meets quality standards.