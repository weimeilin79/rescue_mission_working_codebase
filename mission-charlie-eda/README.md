# 🛰️ MISSION CHARLIE: DRONE SWARM

## 📜 The Story
**Status: STRANDED**  
**Location: Surface of Planet X-42**

Fifteen civilians are trapped on the surface of a hostile planet. Their only hope of escape relies on **15 ancient pods** that must be synchronized to transmit a distress signal to their mothership in orbit.

However, the pods have lost connection to their primary **Control Satellite**.
-   **The Situation**: The satellite's main navigation computer is damaged. The pods are drifting aimlessly.
-   **The Hack**: We have managed to establish a backdoor connection to the satellite, but the uplink is plagued by **severe interstellar interference**, causing massive latency in request-response cycles.
-   **The Solution**: Request/Response is too slow. We have deployed an **Event-Driven Architecture (EDA)** with **Server-Sent Events (SSE)** to stream telemetry through the noise.
-   **Your Role**: You are the Operator. You have access to a custom **GenAI Agent** that can calculate the complex vector math needed to force the pods into specific signal-boosting formations (Circle, Star, Line).

**Objective**: Override the manual controls, lock the formations, and boost the signal to 100% to trigger the rescue.

---

![Mission Charlie Demo](img/mission_charlie.gif)

## 🏗️ Architecture Overview

The system creates a **Real-Time Event-Driven Loop** using Kafka, Server-Sent Events (SSE), and Generative AI.

### 1. Frontend: Mission Dashboard
-   **Tech**: React, Vite, TailwindCSS, EventSource API.
-   **Role**: A "Sci-Fi HUD" that provides real-time visualization of the fleet.
-   **Key Feature**: **Haptic UI**. The interface simulates effective connection status with transmission delays, signal noise, and "glitch" effects when manual overrides occur.

### 2. Backend: The Agent Mesh
-   **Tech**: Python, FastAPI, `google.genai`, Apache Kafka (Managed Service).
-   **The Components**:
    -   **Commander Agent (agent/)**: The intelligence. It transforms high-level commands ("Form a Star") into precise coordinate vectors using Gemini 2.0. It publishes these targets to the Kafka Event Bus.
    -   **Satellite Simulation (satellite/)**: The physics engine. It consumes target vectors from Kafka and simulates the physical movement (velocity, drag) of the drones. It broadcasts the state @ 60fps to the frontend via SSE.

### 3. Data Flow
1.  **User** clicks "CIRCLE" -> **HTTP POST** -> **Commander Agent**.
2.  **Commander Agent** prompts Gemini -> Calculates Vectors -> Publishes to **Kafka**.
3.  **Satellite Agent** consumes Kafka Message -> Updates Drone Target Coordinates.
4.  **Satellite Agent** runs Physics Loop -> Pushes updates via **SSE** -> **Dashboard**.

Others
1.  **User** drags Drone -> **HTTP POST** (`/update_pod`) -> Forces **Global Chaos State**.

---

## 🚦 How to Run

### Prerequisites
-   Node.js (v18+)
-   Python (v3.10+)
-   Access to a Kafka Cluster (or local Redpanda/Kafka)
-   Google Cloud API Key

### 1. Environment Setup
You need to configure the Agents to talk to Kafka and Gemini.

Create a `.env` file in **BOTH** `agent/` and `satellite/` directories:
```env
# Google AI
GOOGLE_API_KEY=your_gemini_key

# Kafka Configuration
BOOTSTRAP_SERVER=your_kafka_broker_ip:9092
KAFKA_USERNAME=your_username
KAFKA_PASSWORD=your_password
```

### 2. Kafka Cluster Setup
You MUST manually create the following topics in your Kafka Cluster before starting the system:
-   `a2a-formation-request`
-   `a2a-reply-satellite-dashboard`

(No specific partition count required, default is fine).

### 3. Start the Backend (2 Terminals)

**Terminal A: Commander Agent**
(Handles Logic & Kafka Publishing)
```bash
cd agent
source ../.venv/bin/activate  # or your venv path
python agent/server.py
```

**Terminal B: Satellite Simulation**
(Handles Physics & Kafka Consumption)
```bash
source ../.venv/bin/activate
python satellite/main.py
```
*Wait for "Kafka Consumer Started" logs.*

### 4. Start the Dashboard (Terminal C)

**Terminal C: Frontend**
```bash
cd frontend
npm install
npm run dev
```

### 5. Execute Mission
1.  Open **http://localhost:5173**.
2.  Observe the startup sequence (Starfield + Random Formation).
3.  Click **"STAR"** or **"CIRCLE"** to request a formation.
4.  Wait for the **"TRANSMITTING SEQUENCE"** (15s) to complete.
5.  Watch the drones align!
6.  **Experiment**: Drag a drone with your mouse to trigger a "Manual Override" and watch the signal destabilize.
