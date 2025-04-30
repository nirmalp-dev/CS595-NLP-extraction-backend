from typing import List, Dict
from dataclasses import dataclass
from lof.services import IMONLPService

@dataclass
class TokenizationResult:
    text: str
    semantic_type: str
    codes: Dict[str, str]
    source: str
    assertion: str

def process_entity_codes(entity: Dict, source: str) -> TokenizationResult:
    codes = {}
    codemaps = entity.get("codemaps", {})

    for system, details in codemaps.items():
        if system == "imo" and source == "IMO":
            code = details.get("lexical_code")
            if code:
                codes["IMO"] = code
        elif "codes" in details and details["codes"]:
            if entity["semantic"] == "drug":
                rxnorm_code = next((c.get("rxnorm_code") for c in details["codes"] if "rxnorm_code" in c), None)
                if rxnorm_code:
                    codes["RxNORM"] = rxnorm_code
            else:
                code_val = details["codes"][0].get("code")
                if code_val:
                    codes[system.upper()] = code_val

    return TokenizationResult(
        text=entity['text'],
        semantic_type=entity['semantic'],
        codes=codes,
        source=source,
        assertion=entity.get('assertion', '')
    )

def analyze_medical_report(text: str) -> Dict:
    try:
        data = IMONLPService().tokenize_text(text=text)
        conditions = []
        labs = []
        procedures = []
        medications = []

        for entity in data.get("entities", []):
            result = process_entity_codes(entity, "IMO")
            if result.semantic_type in ["problem", "diagnosis"]:
                conditions.append({
                    "name": result.text,
                    "code": list(result.codes.values())[0] if result.codes else "",
                    "coding_system": list(result.codes.keys())[0] if result.codes else ""
                })
            elif result.semantic_type == "test":
                labs.append({
                    "name": result.text,
                    "value": "",
                    "unit": "",
                    "interpretation": "",
                    "loinc_code": result.codes.get("LOINC", "")
                })
            elif result.semantic_type in ["treatment", "imo_procedure"]:
                procedures.append({
                    "name": result.text,
                    "cpt_code": result.codes.get("CPT", "")
                })
            elif result.semantic_type == "drug":
                medications.append({
                    "name": result.text,
                    "rxnorm_code": result.codes.get("RxNORM", "")
                })

        return {
            "summary": "",  # Optional, can enhance later
            "severity": "",  # Optional, can enhance later
            "conditions": conditions,
            "labs": labs,
            "procedures": procedures,
            "medications": medications
        }

    except Exception as e:
        raise RuntimeError(f"IMO analysis failed: {e}")
