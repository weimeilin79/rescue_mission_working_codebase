# Biometric Lock - Mission Alpha Drone

## Overview
A "Biometric Lock" minigame where users mimic a sequence of numbers using hand gestures. The system uses a React frontend and a Python backend following the Google Cloud ADK Streaming Agent pattern.

## Prerequisites
- Node.js (Frontend)
- Python 3.9+ (Backend)
- Google Cloud API Key (or Vertex AI credentials)

## Setup & Run
1. Backend (Python ADK pattern)
The backend uses FastAPI and a simulated Runner to handle Bidi-streaming with Gemini.

```bash 
cd mission-alpha-drone/backend
# Activate virtual environment
source venv/bin/activate
# Install dependencies
pip install -r requirements.txt
# Run the agent server
python app/main.py
Server listens on http://0.0.0.0:8080
```
2. Frontend (React)

```bash
cd mission-alpha-drone/frontend
# Install dependencies
npm install
# Start development server
npm run dev
Open http://localhost:5173 to play.
```
## Project Structure
- backend/app/main.py
: FastAPI server using google.adk for the Runner implementation.
- backend/app/biometric_agent/agent.py
: Agent definition.
- frontend/src/BiometricLock.jsx
: Game logic & HUD.
Dependencies: Requires google-genai and google-adk (or equivalent internal package).

##Configuration
Update 
`.env`
 in 
`backend/app/.env`
 with your project details:

```properties
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=True
```

**Authentication**: You must have credentials configured.
- Local Development: Run `gcloud auth application-default login`.
- Service Account: Set `GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json` in 
.env
.

- The agent uses model gemini-2.0-flash-exp by default.

## Features
- Multimodal Input: Processes live video (16kHz PCM audio + JPEG frames) simultaneously.
- Biometric Calibration: Responds to "Calibrate" command to count fingers.
- Anti-Cheat/Security: Requires exact sequence matching.
- Dynamic UI:
    - Single Round: 1 round of 4 digits.
    - Auto-Termination: Connection closes on Success/Fail.
    - Visual Feedback: "Access Granted" (Green) / "Critical Fail" (Red) effects.
    - Clean Logging: Backend logs minimize noise, showing only transcripts and tool calls.

## Verification
- Start Backend: `python main.py`
- Start Frontend: `npm run dev`
- Command: Say "Calibrate" to the agent.
- Feedback: Agent should scan, call tool, and remain silent (no double-speak).
- Game Loop
    - Win: Match 4 numbers -> Green Success Screen -> Socket Disconnects.
    - Lose: Wait 90s -> Red Fail Screen -> Socket Disconnects.