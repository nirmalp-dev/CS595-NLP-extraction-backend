import requests
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def analyze_medical_report(text, model="gpt-4o-mini", max_tokens=1000, temperature=0.3):
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key not found in environment variables")
        
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    # Define the JSON structure we want OpenAI to return
    function_schema = {
        "name": "structured_medical_report_analysis",
        "description": "Extracts structured clinical information and maps to standard medical ontologies",
        "parameters": {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": "Concise summary of the report in 100 words"
                },
                "conditions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "code": {"type": "string"},
                            "coding_system": {"type": "string"}
                        }
                    }
                },
                "labs": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "value": {"type": "string"},
                            "unit": {"type": "string"},
                            "interpretation": {"type": "string"},
                            "loinc_code": {"type": "string"}
                        }
                    }
                },
                "procedures": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "cpt_code": {"type": "string"}
                        }
                    }
                },
                "medications": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "dose": {"type": "string"},
                            "route": {"type": "string"},
                            "rxnorm_code": {"type": "string"}
                        }
                    }
                },
                "severity": {
                    "type": "string",
                    "description": "Overall severity of the report (e.g., mild, moderate, severe)"
                }
            },
            "required": ["summary", "conditions", "labs", "severity"]
        }
    }

    prompt = f"""
You are a medical expert analyzing a clinical report. Extract structured clinical data in JSON format.

1. Summarize the report in 100 words.
2. Extract all **diagnosed conditions**, and for each provide ICD-10 or SNOMED CT code.
3. Extract all **lab test results**, with value, unit, interpretation, and LOINC code.
4. Extract any **procedures** mentioned, with CPT codes.
5. Extract **medications**, including dose, route, and RxNorm code.
6. Assign an overall medical severity: mild, moderate, or severe.

Return all of this in structured JSON format based on the defined schema.
    """

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a clinical AI assistant trained in structured medical data extraction."},
            {"role": "user", "content": prompt + "\n\nClinical Report:\n\n" + text}
        ],
        "functions": [function_schema],
        "function_call": {"name": "structured_medical_report_analysis"},
        "max_tokens": max_tokens,
        "temperature": temperature
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        # Extract and parse the function arguments as JSON
        function_args = response.json()["choices"][0]["message"]["function_call"]["arguments"]
        return json.loads(function_args)

    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        raise
