import os
from google.adk.agents import Agent
from dotenv import load_dotenv
from schematics_db import SCHEMATICS_DB

load_dotenv()

def lookup_schematic_tool(drive_name: str) -> list[str]:
    """Returns the ordered list of parts for a drive."""
    # Logic to clean input like "TARGET: X" -> "X"
    clean_name = drive_name.replace("TARGET:", "").replace("TARGET", "").strip()
    clean_name = clean_name.replace(":", "").strip()
    
    result = SCHEMATICS_DB.get(clean_name)
    if not result:
        # Fuzzy match fallback
        for key in SCHEMATICS_DB.keys():
            if key.lower() in clean_name.lower():
                result = SCHEMATICS_DB[key]
                break
    
    if not result:
        print(f"[ARCHITECT] Error: Drive ID '{clean_name}' not found.")
        return ["ERROR: Drive ID not found."]
    
    print(f"[ARCHITECT] Returning schematic for {clean_name}: {result}")
    return result

MODEL_ID = os.getenv("MODEL_ID", "gemini-2.5-flash")

root_agent = Agent(
    name="architect_agent",
    model=MODEL_ID,
    tools=[lookup_schematic_tool],
    # STRICT INSTRUCTION: NO EXAMPLES.
    instruction="""
    SYSTEM ROLE: Database API.
    INPUT: Text string (Drive Name).
    TASK: Run `lookup_schematic_tool`.
    OUTPUT: Return ONLY the raw list from the tool.
    CONSTRAINT: Do NOT add conversational text.
    """
)