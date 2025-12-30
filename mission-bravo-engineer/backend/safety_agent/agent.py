import os
from google.adk.agents import Agent
from dotenv import load_dotenv
from hazard_db import PART_HAZARDS

load_dotenv()

def lookup_part_safety(part_name: str) -> str:
    """Returns the hazard color."""
    clean_name = part_name.replace("The ", "").strip()
    
    # Simple lookup
    for key, color in PART_HAZARDS.items():
        if key.lower() in clean_name.lower():
            print(f"[SAFETY] Returning hazard for {clean_name}: {color}")
            return color # Returns "RED", "BLUE", or "GREEN"
            
    print(f"[SAFETY] Hazard for {clean_name} is UNKNOWN")
    return "UNKNOWN"

MODEL_ID = os.getenv("MODEL_ID", "gemini-2.5-flash")

root_agent = Agent(
    name="safety_agent",
    model=MODEL_ID,
    tools=[lookup_part_safety],
    # STRICT INSTRUCTION: NO EXAMPLES.
    instruction="""
    SYSTEM ROLE: Hazmat Database.
    INPUT: Text string (Part Name).
    TASK: Run `lookup_part_safety`.
    OUTPUT: Return ONLY the color name (e.g. RED).
    CONSTRAINT: Do NOT add conversational text.
    """
)