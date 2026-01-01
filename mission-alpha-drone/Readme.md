# 🦅 MISSION ALPHA: RESCUE DRONE

## 📜 The Story
**Status: SYSTEM RESET**  
**Location: Sector 7 "The Ravine", Planet X-42**

**The Situation**:
You have located 5 survivors trapped in a sector inaccessible to your main ship. You have a fleet of **Autonomous Rescue Drones**, but the solar storm that crashed your ship also reset the drone fleet's control system. They are currently unresponsive.

**The Solution**:
To launch the fleet, you must build an AI Agent to establish a **Biometric Neural Sync**. This will allow you to bypass the damaged circuits and control the drones manually via your own biological inputs.

**The Rescue Mission**:
You must perform the synchronization protocol to lock in the neural link.
-   **The Protocol**: Stand in front of the optical sensors and complete the finger sequences (1 to 5).
-   **The Outcome**: If successful, the **"Biometric Sync"** engages, giving you full manual control to launch the fleet and retrieve the survivors.

![Mission Alpha](img/mission_alpha.gif)
---

## 🏗️ Architecture Overview

The system creates a **Multimodal Real-Time Loop** using Google's GenAI Live API.

### 1. Frontend: Biometric Interface
-   **Tech**: React, Vite, TailwindCSS.
-   **Role**: Simulates the drone's optical sensor interface. It captures the video stream from your webcam and sends it to the backend via WebSocket.
-   **Key Feature**: **Visual Feedback**. The UI updates in real-time as the AI recognizes your gestures.

### 2. Backend: The Agent
-   **Tech**: Python, FastAPI, `google.adk` (Agent Development Kit), Google Gemini 2.0.
-   **The Intelligence**: The agent is powered by **Gemini Multimodal Live API**. It processes the video stream frame-by-frame to identify hand gestures (counting fingers 1-5) and verifies the sequence against the security protocol.

### 3. Data Flow
1.  **User** shows hand signal to Webcam -> **WebSocket** -> **Backend**.
2.  **Backend** sends video frame -> **Gemini Live API**.
3.  **Gemini** analyzes gesture -> Returns count -> **Backend**.
4.  **Backend** verifies sequence -> Sends feedback -> **Frontend UI**.

---

## 🚦 How to Run

### Prerequisites
-   Node.js (v18+)
-   Python (v3.10+)
-   Google Cloud API Key

### 1. Environment Setup

Create a `.env` file in the `backend/` directory:
```env
GOOGLE_API_KEY=your_gemini_key
```

### 2. Start the Backend (Terminal A)
Navigate to the `backend` directory and run the server:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run the Agent
python app/main.py
```
*Server will start on http://localhost:8080*

### 3. Start the Frontend (Terminal B)
Navigate to the `frontend` directory:

```bash
cd frontend
npm install
npm run dev
```

### 4. Execute Mission
1.  Open **http://localhost:5173**.
2.  Click **"CONNECT SYSTEM"**.
3.  Follow the on-screen prompts to calibrate.
4.  Show the correct number of fingers (1, then 2, etc.) to unlock the drones!