# 🚀 MISSION BRAVO: ENGINEER

## 📜 The Story
**Status: CRITICAL FAILURE**  
**Location: Starship "Ozymandias", Deep Space**

You are the Lead Engineer to help with the mission on the *Ozymandias*. Where you will need to rescue helpless people to leave the planet using a broken rocket in Alien tech. The main Warp Drive has destabilized. To save the ship, you must manually assemble a replacement drive using the **Volatile Workbench**.

However, the ship's sensors are corrupted. The labels on the parts and the disposal bins are unreliable holograms.
-   **The Tech Issue**: You are not familiar with this specific Alien Tech. 
-   **The AI Partner**: You are connected to "DISPATCH" agent, a Central AI Node. Dispatch cannot move the parts, but it can access the **Alien Database**.
-   **The Protocol**:
    1.  **Start**: Ask Dispatch for the correct "Blueprint" for the required drive.
    2.  **Verify**: Dispatch will query the **Architect Agent** from the alien planet to get the true parts list.
    3.  **Hazard**: If a part glows or triggers an alarm, it is radioactive. 
    4.  **Disposal**: Dispatch must query the **Safety Officer** for the "Bio-Key" (Correct Color) to dispose of the hazard safely.

**Objective**: Assemble the drive before the system collapses.

---

![Mission Bravo Engineer](img/mission_bravo.gif)

## 🏗️ Architecture Overview

The system creates a **Multimodal Human-AI Loop** using Google's GenAI tools and a WebSocket bridge.

### 1. Frontend: The Volatile Workbench
-   **Tech**: React, Vite, TailwindCSS.
-   **Role**: Simulates the physical workstation. Handles drag-and-drop physics, "Alien" encryption UI effects, and captures microphone audio/camera frames to stream to the backend.
-   **Key Feature**: "Deterministic Chaos". The workbench introduces hazards (glowing parts) and randomized drive targets that require external validation.

### 2. Backend: The Agent Swarm
-   **Tech**: Python, `google.adk` (Agent Development Kit), `google.genai`, WebSockets.
-   **The Hive Mind**:
    -   **Dispatch Agent (The Brain)**: The primary Multimodal Agent. It processes the Audio/Video stream from the user. It is instructed to be "Visual-Skeptical"—it assumes visual inputs might be decoys and enforces tool use.
    -   **Architect Agent (The Library)**: A specialized sub-agent with access to the `SCHEMATICS_DB`. It is the source of truth for drive recipes.
    -   **Safety Agent (The Shield)**: A specialized sub-agent with access to the `HAZMAT_DB`. It provides the only valid disposal instructions for hazardous parts.

### 3. Data Flow
1.  **User** speaks/acts on Frontend -> **WebSocket** -> **Dispatch Agent**.
2.  **Dispatch Agent** analyzes input + visual frame.
3.  **IF** Assembly needed -> Calls **Architect** -> Returns Parts List -> TTS back to User.
4.  **IF** Hazard detected -> Calls **Safety** -> Returns Color -> TTS back to User.

---

## 🚦 How to Run

### Prerequisites
-   Node.js (v18+)
-   Python (v3.10+)
-   Google Cloud API Key with access to Gemini Models.

### 1. Backend Setup
Navigate to the `backend` directory:
```bash
cd backend
```

Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Set up your environment variables:
Create a `.env` file in `backend/`:
```env
GOOGLE_API_KEY=your_api_key_here


# Option 2: Vertex AI Config
# GOOGLE_GENAI_USE_VERTEXAI=True
# GOOGLE_CLOUD_PROJECT=your_project
# GOOGLE_CLOUD_LOCATION=us-central1
```

### 2. Run the Agent Swarm (3 Terminals)
You need to run the **Dispatch Agent** and its two sub-agents simultaneously. Open **3 separate terminals** in the `backend/` directory:

**Terminal A: Safety Agent (Port 8080)**
```bash
# Serves the Hazmat Database
source venv/bin/activate
cd safety_agent
python server.py
```

**Terminal B: Architect Agent (Port 8081)**
```bash
# Serves the Drive Blueprints
source venv/bin/activate
cd architect_agent
python server.py
```

**Terminal C: Dispatch Agent (Main Logic)**
```bash
# Connects to Frontend and Sub-Agents
source venv/bin/activate
python main.py
```

*Wait until all three show "Systems Online" or similar logs.*

### 3. Frontend Setup
Open a new terminal (Terminal D) and navigate to the `frontend` directory:
```bash
cd frontend
```

Install dependencies:
```bash
npm install
```

Start the interface:
```bash
npm run dev
```

### 4. Start the Mission
1.  Open the localhost URL (http://localhost:5173).
2.  Click **"INITIALIZE SYSTEM"**.
3.  Allow Permissions.
4.  Say **"Start Mission"** to begin!

