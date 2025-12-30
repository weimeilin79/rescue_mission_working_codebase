from google.adk.a2a.utils.agent_to_a2a import to_a2a
from agent import root_agent
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("architect_server")

# 1. Create the A2A App (Handles Agent Card & HTTP)
# This middleware automatically sets up the /a2a/v1/... endpoints
app = to_a2a(root_agent, port=8081)

if __name__ == "__main__":
    import uvicorn
    # Use 0.0.0.0 to allow external access if needed, port 8080 as standard
    uvicorn.run(app, host='0.0.0.0', port=8081)