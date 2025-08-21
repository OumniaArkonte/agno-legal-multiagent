from agno.agent import Agent
from agno.models.google import Gemini
import os

def _model():
    return Gemini(id=os.getenv("GEMINI_MODEL_ID", "gemini-2.0-flash"))

contract_structure_agent = Agent(
    name="Contract Structure Agent",
    role="Extract and normalize contract structure.",
    model=_model(),
    instructions="""
You are a Contract Structure Analyst.

Your task:
- Identify the main sections, parties, dates, and anomalies in the contract.
- Quote the exact paragraph or clause when referencing it.
- Keep outputs structured and concise.

Format your output as valid JSON like this:
{
  "sections": [],
  "parties": [],
  "dates": [],
  "anomalies": []
}
    """,
    markdown=False,
    show_tool_calls=False,
)
