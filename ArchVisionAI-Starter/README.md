# ArchVision AI

## Four Canvas Questions

1) **Team Members:** Jordan Burgess, Seyitan, and Aidan.

2) **Project Idea:** We are creating an AI-powered 3D software architecture designer that allows users to manually build, visualize, edit, and generate software architecture models using a visual 3D interface and plain-English AI assistance.

3) **Target Audience:** Software engineering students, new developers, project teams, and anyone who needs help planning, understanding, or generating a software project structure before writing code.

4) **Project Goal:** We hope to make software architecture easier to understand by turning abstract system designs into interactive 3D models that users can edit, receive AI feedback on, and export into starter project folders.

---

## General Information

ArchVision AI is a full-stack software engineering project that combines a React/JSX frontend, a Python FastAPI backend, 3D visualization, and AI-assisted architecture generation. The user can describe a software system in plain English, and the AI assistant returns a structured model that is rendered as an interactive 3D architecture diagram.

Users can also manually create components such as frontends, backends, databases, authentication services, APIs, storage systems, caches, and message queues. The long-term goal is to allow users to upload an existing codebase, inspect the architecture visually, improve the design with AI feedback, and export a starter project structure based on models created by the user.

### What problem does it solve?

- Helps users understand software architecture visually instead of only through text or flat diagrams.
- Makes project planning easier for students and developers.
- Allows users to generate architecture diagrams from plain English.
- Gives AI-powered design feedback based on common architecture patterns.
- Helps users create a starter folder/file structure from their architecture design.

### Purpose of the project

- To create an intuitive 3D architecture design tool.
- To help users learn better software architecture practices.
- To combine AI, visualization, project generation, and full-stack development into one polished application.
- To create a useful software engineering portfolio project within a 4-week timeline.

### Why undertake this project?

- It demonstrates frontend engineering, backend API design, AI integration, project architecture, state management, and 3D visualization.
- It is more impressive than a basic chatbot because AI is directly tied to the app’s main workflow.
- It gives users a practical tool for planning real software projects.

---

## Technologies Used

### Frontend

- **JavaScript / JSX** – Main frontend language.
- **React** – Component-based UI framework.
- **Vite** – Fast frontend development server and build tool.
- **Tailwind CSS** – Styling and layout.
- **Three.js** – 3D rendering engine.
- **React Three Fiber** – React renderer for Three.js.
- **Drei** – Helper components for React Three Fiber.
- **Zustand** – Frontend state management.
- **Axios** – API calls from frontend to backend.
- **Lucide React** – Icons.
- **React Hook Form** – Form handling.
- **Framer Motion** – UI animations.

### Backend

- **Python** – Main backend language.
- **FastAPI** – Backend API framework.
- **Uvicorn** – ASGI server for running FastAPI.
- **Pydantic** – Request/response validation.
- **SQLAlchemy** – Database ORM.
- **PostgreSQL or SQLite** – Database for saved architecture projects.
- **OpenAI API** – AI model generation and architecture feedback.
- **NetworkX** – Architecture graph analysis.
- **Jinja2** – Template-based starter project file generation.
- **Pytest** – Backend testing.

---

## MVP Features

- **Interactive 3D Architecture Canvas** – Users can see frontend, backend, database, and service nodes in a 3D workspace.
- **Manual Component Creation** – Users can add architecture components from a sidebar.
- **Plain-English AI Generation** – Users can describe a system and generate a starting architecture model.
- **AI Architecture Feedback** – AI or rule-based backend checks identify weak points in the design.
- **Save/Load Project Structure** – Backend route scaffold included for project persistence.
- **Export Starter Project** – Backend service creates starter folders and an `architecture.json` file based on the model.

---

## Stretch Goals

- Drag-and-drop movement for 3D nodes.
- Visual connection lines/arrows between components.
- User authentication.
- Full PostgreSQL persistence.
- Codebase ZIP upload and architecture detection.
- Export as image, JSON, or ZIP.
- C4 model, UML, or ERD mode.
- More detailed AI design scoring.

---

## Project Requirements & Dependencies

### Required Installs

- Node.js 18+
- npm
- Python 3.10+
- Git
- VS Code or another editor
- OpenAI API key
- Docker Desktop

### Optional Installs

- PostgreSQL
- Postman or Insomnia

---

## Installation & Setup

Verify installations:

```bash
python --version
node -v
npm -v
docker --version
```

---

# Clone the Repository

```bash
git clone <repository-url>

cd ArchVisionAI-Starter
```

---

# Environment Variables

Copy

```
.env.example
```

to

```
.env
```

Example:

```text
OPENAI_API_KEY=your_openai_api_key_here

DATABASE_URL=postgresql://postgres:password@localhost:5432/archvision_ai

CORS_ORIGINS=http://localhost:5173

VITE_API_BASE_URL=http://localhost:8000

POSTGRES_DB=archvision_ai

POSTGRES_USER=postgres

POSTGRES_PASSWORD=password
```

---

# Start PostgreSQL

Docker Desktop must be running.

Start the database:

```bash
docker compose up -d
```

Verify the container:

```bash
docker compose ps
```

Expected output:

```
archvision-postgres
```

Stop the database:

```bash
docker compose down
```

---

### 1. Backend setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r ../requirements.txt
```

Create a `.env` file in the root folder using `.env.example` as a guide:

```bash
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=sqlite:///./archvision.db
CORS_ORIGINS=http://localhost:5173
```

Run the backend:

```bash
uvicorn app.main:app --reload --port 8000
```

Backend will run at:

```text
http://localhost:8000
```

API docs will be available at:

```text
http://localhost:8000/docs
```

### 2. Frontend setup

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend will run at:

```text
http://localhost:5173
```

---

### Running the Project

The project requires **three running processes**.

### Terminal 1

Docker

```bash
docker compose up -d
```

### Terminal 2

Backend

```bash
cd backend

venv\Scripts\activate

uvicorn app.main:app --reload
```

### Terminal 3

Frontend

```bash
cd frontend

npm run dev
```

---

## Usage

1. Start the FastAPI backend.
2. Start the React frontend.
3. Open the frontend in your browser.
4. Use the left sidebar to add architecture components.
5. Use the AI assistant panel to describe a project in plain English.
6. Click **Generate Model** to replace the current model with an AI-generated architecture.
7. Click **Get Architecture Feedback** to receive suggestions.
8. Use the export endpoint to generate starter project folders from the current model.

---

## Suggested 4-Week Timeline

### Week 1: Project Foundation

- Set up frontend and backend folders.
- Build the basic React layout.
- Add Tailwind styling.
- Add FastAPI backend routes.
- Create the architecture JSON schema.
- Display starter 3D nodes on the canvas.

### Week 2: 3D Visualization and Manual Tools

- Add component sidebar.
- Add manual component creation.
- Add selected component state.
- Improve component visuals with icons, labels, colors, and positions.
- Begin connection rendering between components.

### Week 3: AI Integration

- Add plain-English architecture generation.
- Add AI/rule-based feedback endpoint.
- Validate AI JSON before rendering.
- Add error handling for bad AI responses.
- Improve the AI assistant panel UI.

### Week 4: Export, Polish, and Presentation

- Add starter project export.
- Add save/load project functionality.
- Improve UI/UX.
- Add README documentation.
- Add screenshots/demo video.
- Prepare final presentation and testing plan.

---

## Project Status

Starter scaffold created. The current version includes separate frontend and backend folders, basic 3D visualization, AI route scaffolding, architecture schemas, project export scaffolding, and a proposal-style README.

---

## Room for Improvement

### Areas for Improvement

- Add real persistent database support instead of in-memory project storage.
- Add better 3D controls for dragging and connecting nodes.
- Add visual arrows/lines for connections.
- Improve AI prompt validation and schema enforcement.
- Add authentication and user-owned projects.
- Add ZIP export for generated projects.

### To Do

- Implement database models.
- Add drag-and-drop movement.
- Render connection lines.
- Add component editing panel.
- Add project save/load UI.
- Add frontend tests and backend tests.
- Deploy frontend and backend.

---

## Acknowledgements

This README was adapted from the structure of the uploaded SpiritSmith README template, including its sections for project idea, general information, technologies, features, setup, usage, sprint planning, and future improvements.

---

## Contact

Jordan Burgess
