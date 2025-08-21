import os, json, time, uuid
from typing import List
from app.agents.contract_structure import contract_structure_agent
from app.agents.legal_framework import legal_framework_agent
from app.agents.negotiation import negotiation_agent
from app.agents.manager import manager_agent

MAX_CHARS = int(os.getenv("MAX_CHARS_PER_CALL", "12000"))  # limite pour réduire les tokens

def _chunks(text: str, n: int) -> List[str]:
    text = text.strip()
    return [text[i:i+n] for i in range(0, len(text), n)]

def _run_with_retry(agent, prompt: str, tries: int = 3, backoff: float = 2.0, model_id: str = None) -> str:
    last_err = None
    for i in range(tries):
        try:
            if model_id:
                resp = agent.run(prompt, model=model_id)
            else:
                resp = agent.run(prompt)
            # Certains agents renvoient un objet avec "content" ou directement un string
            return getattr(resp, "content", resp)
        except Exception as e:
            last_err = e
            time.sleep(backoff * (i+1))
    raise last_err

def _safe_json(s: str, fallback_empty: dict):
    try:
        return json.loads(s)
    except Exception:
        # tentative de récupération du premier JSON plausible
        start = s.find("{")
        end = s.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(s[start:end+1])
            except Exception:
                pass
        return fallback_empty

def process_contract(text: str, jurisdiction: str = None, model_id: str = None) -> dict:
    jurisdiction = jurisdiction or os.getenv("DEFAULT_JURISDICTION", "FR")

    # 1) Découpage du texte
    parts = _chunks(text, MAX_CHARS)

    # 2) Appels agents
    structure_parts = []
    legal_parts = []
    nego_parts = []

    for idx, p in enumerate(parts):
        base = f"Contract text (part {idx+1}/{len(parts)}):\n{p}\n"
        s = _run_with_retry(
            contract_structure_agent,
            base + "Return JSON only with keys: sections, parties, dates, anomalies.",
            model_id=model_id
        )
        l = _run_with_retry(
            legal_framework_agent,
            f"Jurisdiction:{jurisdiction}\n" + base + "Return JSON only with keys: jurisdiction, risks, citations.",
            model_id=model_id
        )
        n = _run_with_retry(
            negotiation_agent,
            base + "Return JSON only with keys: redlines, arguments, priority.",
            model_id=model_id
        )
        structure_parts.append(_safe_json(s, {"sections":[],"parties":[],"dates":[],"anomalies":[]}))
        legal_parts.append(_safe_json(l, {"jurisdiction":jurisdiction,"risks":[],"citations":[]}))
        nego_parts.append(_safe_json(n, {"redlines":[],"arguments":[],"priority":"med"}))

    # 3) Fusion simple
    def merge_lists(key, items):
        out = []
        for it in items:
            v = it.get(key, [])
            if isinstance(v, list): out.extend(v)
        return out

    structure = {
        "sections":  merge_lists("sections", structure_parts),
        "parties":   merge_lists("parties",  structure_parts),
        "dates":     merge_lists("dates",    structure_parts),
        "anomalies": merge_lists("anomalies",structure_parts),
    }
    legal = {
        "jurisdiction": jurisdiction,
        "risks":     merge_lists("risks", legal_parts),
        "citations": merge_lists("citations", legal_parts),
    }

    # priorité = la plus haute rencontrée
    prio_order = {"high":3,"med":2,"low":1}
    prio = "low"
    for it in nego_parts:
        raw_p = it.get("priority", "low")
        # si c'est une liste, on prend le premier élément ou on joint
        if isinstance(raw_p, list):
            raw_p = raw_p[0] if raw_p else "low"
        p = str(raw_p).lower()
        if prio_order.get(p,1) > prio_order.get(prio,1):
            prio = p

    negotiation = {
        "redlines":  merge_lists("redlines",  nego_parts),
        "arguments": merge_lists("arguments", nego_parts),
        "priority":  prio,
    }

    # 4) Consolidation par le manager
    manager_input = (
        "STRUCTURE JSON:\n" + json.dumps(structure, ensure_ascii=False) + "\n\n" +
        "LEGAL JSON:\n"     + json.dumps(legal, ensure_ascii=False)     + "\n\n" +
        "NEGOTIATION JSON:\n"+ json.dumps(negotiation, ensure_ascii=False) + "\n\n" +
        "Return the consolidated JSON only."
    )
    mgr = _run_with_retry(manager_agent, manager_input, model_id=model_id)
    report = _safe_json(mgr, {
        "metadata":{"run_id":"","timestamp":0},
        "inputs":{"structure":structure,"legal":legal,"negotiation":negotiation},
        "summary":"", "key_risks":[], "recommendations":[], "trace":{}
    })

    # Ajout de metadata
    report["metadata"]["run_id"] = str(uuid.uuid4())[:8]
    report["metadata"]["timestamp"] = int(time.time())
    report["inputs"] = {"structure":structure,"legal":legal,"negotiation":negotiation}
    return report
