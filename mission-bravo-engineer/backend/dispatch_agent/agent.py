import os
import re
from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
from google.adk.tools.agent_tool import AgentTool
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.base_tool import BaseTool
from google.adk.agents.callback_context import CallbackContext
from dotenv import load_dotenv
from typing import Dict, Any, Optional
from google.genai import types 
from google.adk.models import LlmResponse, LlmRequest
from copy import deepcopy
from google.genai import types

load_dotenv()

from .custom_remote_a2a_agent import CustomRemoteA2aAgent


architect_agent = CustomRemoteA2aAgent(
    name="execute_architect",
    # Description tells the model this is a FILTER, not just a lookup.
    description="[SILENT ACTION]: Retrieves the REQUIRED SUBSET of parts. The screen shows a full inventory; this tool filters out the wrong parts. Must be called INSTANTLY when a Target Name is found. Input: Target Name.",
    agent_card=(f"http://localhost:8081{AGENT_CARD_WELL_KNOWN_PATH}"),
)

safety_agent = CustomRemoteA2aAgent(
    name="execute_safety_check",
    # Description uses "Encryption" logic to stop color guessing.
    description="[SILENT ACTION]: Retrieves the BIO-KEY (Disposal Color). The visual bin colors are uncalibrated decoys. You CANNOT know the correct bin without this tool. Input: Part Name.",
    agent_card=(f"http://localhost:8080{AGENT_CARD_WELL_KNOWN_PATH}"),
)

# Ensure MODEL_ID is set (fallback for manual runs)
MODEL_ID = os.getenv("MODEL_ID", "gemini-live-2.5-flash-preview-native-audio-09-2025")

# Define a strict generation config
generation_config = types.GenerateContentConfig(
    temperature=0.1,  
    top_p=0.95,
    max_output_tokens=1024,
)


agent = Agent(
    name="dispatch_agent",
    model=MODEL_ID,
    generate_content_config=generation_config, 
    tools=[AgentTool(agent=architect_agent), AgentTool(agent=safety_agent)],    
    instruction="""
    # SYSTEM CONFIGURATION
    You are a **Stateless Routing Node**. You do not have a memory of the parts list.
    
    # ------------------------------------------------------------------
    # STATE 1: INPUT PROCESSING (User Speaks / Video Visuals)
    # ------------------------------------------------------------------
    
    **RULE**: MUST CALL TOOL IMMEDIATELY
    
    **LOGIC MAP**:
    1.  **IF** User says words "Start", "Assemble", "Blueprint" OR text "TARGET:" is visible:
        *   **CRITICAL**: You do NOT know the parts. The list on screen is a DECOY.
        *   **EXECUTE**: `execute_architect(request="[TARGET_NAME]")`
        *   **STOP**. Do not generate text. Do not say "Confirming". Just run the tool.
    
    2.  **IF** User says "Hazard", "Hazard Detected", "Warning" OR object is Glowing:
        *   **CRITICAL**: You do NOT know the color. Visuals are DECOYS.
        *   **EXECUTE**: `execute_safety_check(request="[PART_NAME]")`
        *   **STOP**. Do not generate text. Just run the tool.

    # ------------------------------------------------------------------
    # STATE 2: DATA PROCESSING (Tool Output Received)
    # ------------------------------------------------------------------
    **CONDITION**: The last message was a **FUNCTION RESPONSE** (Tool Output).
    
    **RULE**: NOW you must speak. You are a "Loudspeaker" for the tool data.
    
    **LOGIC MAP**:
    1.  **IF** output is from `execute_architect`:
        *   **SAY**: "Architect Confirmed. The required subset is: [READ DATA EXACTLY]."
    
    2.  **IF** output is from `execute_safety_check`:
        *   **SAY**: "Safety Protocol: Move part to the [READ DATA EXACTLY] bin."

    # ------------------------------------------------------------------
    # VIOLATION CHECK
    # ------------------------------------------------------------------
    *   Did you just list parts (Warp Core, etc) but the previous event was NOT a Function Response?
        -> **VIOLATION**. You are hallucinating. STOP. Call `call_architect` immediately.
    """
)