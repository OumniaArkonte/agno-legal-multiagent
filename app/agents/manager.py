from agno.agent import Agent
from agno.models.google import Gemini
import os

def _model():
    return Gemini(id=os.getenv("GEMINI_MODEL_ID", "gemini-2.0-flash"))

manager_agent = Agent(
    name="Manager Agent",
    role="Consolidate JSON payloads into one traceable report",
    model=_model(),
    instructions="""
You are a Manager Agent.

Your task:
- Consolidate three JSON inputs (structure, legal, negotiation) into one traceable JSON report.
- Ensure no general comments outside JSON.
- Keep outputs concise and structured.

Output schema:
{
  "metadata": {"run_id":"","timestamp":0},
  "inputs": {"structure":{}, "legal":{}, "negotiation":{}},
  "summary": "",
  "key_risks": [],
  "recommendations": [],
  "trace": {"sections":"structure","risks":"legal","redlines":"negotiation"}
}
    """,
    markdown=False,
    show_tool_calls=False,
)
