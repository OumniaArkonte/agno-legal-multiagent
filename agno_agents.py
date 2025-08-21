# agno_agents.py
import uuid
import time
from typing import Dict, Any

def contract_structure_agent(contract_text: str) -> Dict[str, Any]:
    """
    Analyse la structure du contrat : sections, parties, dates, anomalies.
    """
    # Exemple simplifié de détection
    sections = []
    if "Scope of Services" in contract_text:
        sections.append("Scope of Services")
    if "Time of Commencement" in contract_text:
        sections.append("Time of Commencement and Completion")
    if "Early Termination" in contract_text:
        sections.append("Early Termination")
    if "Suspension" in contract_text:
        sections.append("Suspension")
    if "Compensation" in contract_text:
        sections.append("Compensation")

    parties = []
    if "Principal" in contract_text:
        parties.append("Principal")
    if "Contractor" in contract_text:
        parties.append("Contractor")

    dates = []
    if "Commencement" in contract_text:
        dates.append("Commencement")
    if "Completion" in contract_text:
        dates.append("Completion")

    anomalies = []
    if "__" in contract_text or "____________________" in contract_text:
        anomalies.append("Missing dates")
        anomalies.append("Placeholder names")

    return {
        "sections": sections,
        "parties": parties,
        "dates": dates,
        "anomalies": anomalies
    }

def legal_framework_agent(contract_text: str) -> Dict[str, Any]:
    """
    Analyse les risques légaux dans le contrat.
    """
    risks = []
    if "terminate this Agreement at any time without cause" in contract_text:
        risks.append({
            "Clause": "Termination without cause",
            "Issue": "Unilateral, risky for contractor"
        })
    if "indemnify" in contract_text.lower():
        risks.append({
            "Clause": "Indemnification",
            "Issue": "Very broad, favors Principal"
        })

    citations = ["Regulation (EU) No 910/2014"]

    return {
        "jurisdiction": "EU",
        "risks": risks,
        "citations": citations
    }

def negotiation_agent(contract_text: str) -> Dict[str, Any]:
    """
    Propose des stratégies de négociation pour clauses sensibles.
    """
    redlines = []
    if "Early Termination" in contract_text:
        redlines.append({
            "clause": "Early Termination",
            "strategy": "Request 30 days notice or termination fee"
        })
    if "Suspension" in contract_text:
        redlines.append({
            "clause": "Suspension",
            "strategy": "Request 7 days notice and compensation for costs"
        })

    summary = "Rapport consolidé des 3 agents"
    key_risks = ["Unilateral, risky for contractor", "Very broad, favors Principal"]
    recommendations = [
        "Request 30 days notice or termination fee",
        "Request 7 days notice and compensation for costs"
    ]

    return {
        "redlines": redlines,
        "summary": summary,
        "key_risks": key_risks,
        "recommendations": recommendations
    }

def run_multi_agent_system(contract_text: str) -> Dict[str, Any]:
    """
    Exécute tous les agents et consolide les résultats.
    """
    structure = contract_structure_agent(contract_text)
    legal = legal_framework_agent(contract_text)
    negotiation = negotiation_agent(contract_text)

    result = {
        "metadata": {
            "run_id": str(uuid.uuid4()),
            "timestamp": int(time.time())
        },
        "inputs": {
            "structure": structure
        },
        "legal": legal,
        "negotiation": negotiation,
        "trace": {
            "sections": "structure",
            "risks": "legal",
            "redlines": "negotiation"
        }
    }

    return result
