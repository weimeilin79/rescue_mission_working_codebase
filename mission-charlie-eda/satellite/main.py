import asyncio
import json
import random
import logging
import ssl
import os
from dotenv import load_dotenv

# Load env from project root
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel

# A2A Imports
from a2a.client.transports.kafka import KafkaClientTransport
from a2a.client.middleware import ClientCallContext
from a2a.types import (
    AgentCard,
    AgentCapabilities,
    MessageSendParams,
    Message,
    Task,
)


# Configure Logging
logging.basicConfig(level=logging.INFO)
# logging.getLogger("aiokafka").setLevel(logging.DEBUG)
logger = logging.getLogger("satellite_dashboard")
logger.setLevel(logging.INFO)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    global kafka_transport
    logger.info("Initializing Kafka Client Transport...")
    
    # Redpanda Cloud Config (Matches Server)
    bootstrap_server = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
    username = os.getenv("KAFKA_SASL_USERNAME")
    password = os.getenv("KAFKA_SASL_PASSWORD")
    request_topic = "a2a-formation-request"
    reply_topic = "a2a-reply-satellite-dashboard"
    
    # --- Initialize Transport ---
    
    # Create AgentCard for the Client
    client_card = AgentCard(
        name="SatelliteDashboard",
        description="Frontend Dashboard Client",
        version="1.0.0",
        url="https://example.com/satellite-dashboard",
        capabilities=AgentCapabilities(),
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        skills=[]
    )
    
    kafka_transport = KafkaClientTransport(
        agent_card=client_card,
        bootstrap_servers=bootstrap_server,
        request_topic=request_topic,
        reply_topic=reply_topic, # Explicit static reply topic
        
        # Security & Auth
        security_protocol="SASL_SSL",
        sasl_mechanism="SCRAM-SHA-256",
        sasl_plain_username=username,
        sasl_plain_password=password,
        ssl_context=ssl.create_default_context(),
    )
    
    try:
        await kafka_transport.start()
        logger.info("Kafka Client Transport Started Successfully.")
    except Exception as e:
        logger.error(f"Failed to start Kafka Client: {e}")
        
    yield
    
    if kafka_transport:
        logger.info("Stopping Kafka Client Transport...")
        await kafka_transport.stop()
        logger.info("Kafka Client Transport Stopped.")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# State
# Pods: 15 items. Default freeform random.
PODS = []
TARGET_PODS = []
FORMATION = "FREEFORM"

# Global Transport
kafka_transport = None

class FormationRequest(BaseModel):
    formation: str

def init_pods():
    global PODS, TARGET_PODS
    PODS = [{"id": i, "x": random.randint(50, 850), "y": random.randint(100, 600)} for i in range(15)]
    TARGET_PODS = [p.copy() for p in PODS]

init_pods()

@app.get("/stream")
async def message_stream(request: Request):
    async def event_generator():
        logger.info("New SSE stream connected")
        try:
            while True:
                # payload copy to avoid race conditions if PODS validation changes
                current_pods = list(PODS) 
                
                # Send updates one by one to simulate low bandwidth / scanning
                for pod in current_pods:
                     payload = {"pod": pod}
                     yield {
                         "event": "pod_update",
                         "data": json.dumps(payload)
                     }
                     # trickling updates
                     await asyncio.sleep(0.02) 
                
                # Send formation info occasionally
                yield {
                    "event": "formation_update",
                    "data": json.dumps({"formation": FORMATION})
                }
                
                # Main loop delay
                await asyncio.sleep(0.5)
                
        except asyncio.CancelledError:
             logger.info("SSE stream disconnected (cancelled)")
        except Exception as e:
             logger.error(f"SSE stream error: {e}")
             # Don't re-raise, checking if this stabilizes the connection close
             
    return EventSourceResponse(event_generator())

@app.post("/formation")
async def set_formation(req: FormationRequest):
    global FORMATION, PODS
    FORMATION = req.formation
    logger.info(f"Received formation request: {FORMATION}")
    
    if not kafka_transport:
        logger.error("Kafka Transport is not initialized!")
        return {"status": "error", "message": "Backend Not Connected"}
    
    try:
        # Construct A2A Message
        # The agent expects a natural language prompt
        prompt = f"Create a {FORMATION} formation"
        logger.info(f"Sending A2A Message: '{prompt}'")
        
        # Correctly structure the message params
        from a2a.types import TextPart, Part, Role
        import uuid
        
        # Create Message ID
        msg_id = str(uuid.uuid4())
        
        # Create Message Parts with Part wrapper
        message_parts = [Part(TextPart(text=prompt))]
        
        # Create Message Object (Strict Schema)
        msg_obj = Message(
            message_id=msg_id,
            role=Role.user,
            parts=message_parts
        )
        
        message_params = MessageSendParams(
            message=msg_obj
        )
        
        # Send and Wait for Response
        # Timeout increased to 120s for GenAI latency using Context State
        ctx = ClientCallContext()
        ctx.state["kafka_timeout"] = 120.0
        response = await kafka_transport.send_message(message_params, context=ctx)
        
        logger.info("Received A2A Response.")
        
        logger.info(f"Received A2A Response type: {type(response)}")

        content = None
        if isinstance(response, Message):
            content = response.content 
            if not content and response.parts:
                content = response.parts[0].root.text
                
        elif isinstance(response, Task):
            # Check for artifacts (common for structured output)
            if response.artifacts:
                for art in response.artifacts:
                    if art.parts:
                         # root.text because Part is a RootModel[TextPart|...]
                         if hasattr(art.parts[0].root, 'text'):
                             content = art.parts[0].root.text
                             break
            
            # Fallback to history
            if not content and response.history:
                for msg in reversed(response.history):
                     if msg.role == "agent" and msg.parts:
                          if hasattr(msg.parts[0].root, 'text'):
                               content = msg.parts[0].root.text
                               break

        if content:
            logger.info(f"Response Content: {content[:100]}...")
            
            try:
                # content is likely the JSON string
                clean_content = content.replace("```json", "").replace("```", "").strip()
                coords = json.loads(clean_content)
                
                if isinstance(coords, list):
                    logger.info(f"Parsed {len(coords)} coordinates.")
                    for i, pod_target in enumerate(coords):
                        if i < len(PODS):
                            PODS[i]["x"] = pod_target["x"]
                            PODS[i]["y"] = pod_target["y"]
                            await asyncio.sleep(0.05)
                    return {"status": "success", "formation": FORMATION}
                else:
                    logger.error("Response JSON is not a list.")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Agent JSON response: {e}")
        else:
            logger.error(f"Could not extract content from response type {type(response)}")

    except Exception as e:
        logger.error(f"Error calling agent via Kafka: {e}")
        return {"status": "error", "message": str(e)}

class PodUpdate(BaseModel):
    id: int
    x: int
    y: int

@app.post("/update_pod")
async def update_pod_manual(update: PodUpdate):
    """Manual override for drag-and-drop."""
    global FORMATION
    FORMATION = "RANDOM"
    
    # Find the pod and update both current and target to stop it from drifting back
    # effectively "teleporting" it or re-anchoring it.
    found = False
    for p in PODS:
        if p["id"] == update.id:
            p["x"] = update.x
            p["y"] = update.y
            found = True
            break
            
    for t in TARGET_PODS:
        if t["id"] == update.id:
            t["x"] = update.x
            t["y"] = update.y
            break
            
    if found:
        # Force immediate update push?
        # The stream loop will pick it up, but we could trigger it.
        pass
        
    return {"status": "updated", "id": update.id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
