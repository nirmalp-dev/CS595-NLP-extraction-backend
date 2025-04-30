# import requests
# import os
# import json
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()

# # Get API key from environment variables
# OPENAI_API_KEY = "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"

# def summarize_text_with_openai(text, model="gpt-4o-mini", max_tokens=300, temperature=0.7):
#     if not OPENAI_API_KEY:
#         raise ValueError("OpenAI API key not found in environment variables")
        
#     url = "https://api.openai.com/v1/chat/completions"
#     headers = {
#         "Authorization": f"Bearer {OPENAI_API_KEY}",
#         "Content-Type": "application/json"
#     }
    
#     # Define the JSON structure we want OpenAI to return
#     function_schema = {
#         "name": "health_report_analyzer",
#         "description": "Analyzes medical reports and extracts key information",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "summary": {
#                     "type": "string",
#                     "description": "Report summarization in 100 words"
#                 },
#                 "conditions": {
#                     "type": "array",
#                     "items": {
#                         "type": "string"
#                     },
#                     "description": "List of medical conditions detected in the report"
#                 },
#                 "severity": {
#                     "type": "string",
#                     "description": "Overall severity of the conditions detected (e.g., mild, moderate, severe)"
#                 }
#             },
#             "required": ["summary", "conditions", "severity"]
#         }
#     }
    
#     data = {
#         "model": model,
#         "messages": [
#             {"role": "system", 
#              "content": "You are a healthcare expert that analyzes pathology reports. Your task is to extract only the patient's test results, diagnosed conditions, and the overall severity of the condition. Do not extract reference ranges or normal values. Focus only on abnormal values or values that help assess the patient's current health condition."},
#             {"role": "user", "content": f"Analyze the following medical text and extract the key information:\n\n{text}"}
#         ],
#         "functions": [function_schema],
#         "function_call": {"name": "health_report_analyzer"},
#         "max_tokens": max_tokens,
#         "temperature": temperature
#     }
    
#     try:
#         response = requests.post(url, headers=headers, json=data)
#         response.raise_for_status()
        
#         # Extract and parse the function arguments as JSON
#         function_args = response.json()["choices"][0]["message"]["function_call"]["arguments"]
#         result = json.loads(function_args)
        
#         return result
#     except Exception as e:
#         print(f"Error calling OpenAI API: {e}")
#         raise

import requests
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variables
OPENAI_API_KEY = "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"

def summarize_text_with_openai(text, model="gpt-4o-mini", max_tokens=700, temperature=0.7):
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key not found in environment variables")

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    # Detailed system prompt to guide the model
    system_prompt = (
    "You are a medical pathology expert. Your job is to analyze a pathology report and extract only the following:\n"
    "1. A concise 100-word summary suitable for the patient\n"
    "2. A list of diagnosed medical conditions (use clinical terms only)\n"
    "3. An overall severity rating (choose from: mild, moderate, severe)\n"
    "4. A list of abnormal lab test results under 'extractedElements', showing:\n"
    "   - Test Name (label)\n"
    "   - Measured Value (value)\n"
    "   - Interpretation (e.g., High, Low, Normal)\n\n"
    "Do NOT include reference ranges or normal/irrelevant tests. Only return structured, medically relevant findings."
    )

    function_schema = {
        "name": "health_report_analyzer",
        "description": "Analyzes medical reports and extracts key information",
        "parameters": {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": "Report summarization in 100 words"
                },
                "conditions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of medical conditions detected"
                },
                "severity": {
                    "type": "string",
                    "description": "Overall severity of the conditions detected (e.g., mild, moderate, severe)"
                },
                "extractedElements": {
                    "type": "array",
                    "description": "List of key lab test results extracted from the report",
                    "items": {
                        "type": "object",
                        "properties": {
                            "label": {"type": "string"},
                            "value": {"type": "string"},
                            "interpretation": {"type": "string"}
                        },
                        "required": ["label", "value", "interpretation"]
                    }
                }
            },
            "required": ["summary", "conditions", "severity", "extractedElements"]
        }
    }

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    "Analyze the following pathology report. Extract abnormal lab results (no reference ranges), "
                    "diagnosed conditions, severity, and present them as structured extractedElements.\n\n" + text
                )
            }
        ],
        "functions": [function_schema],
        "function_call": {"name": "health_report_analyzer"},
        "max_tokens": max_tokens,
        "temperature": temperature
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        response_json = response.json()
        print("\U0001f9e0 Raw OpenAI response:", json.dumps(response_json, indent=2))

        # Safely extract function_call -> arguments
        choices = response_json.get("choices", [])
        if not choices:
            raise ValueError("No choices returned by OpenAI API.")

        message = choices[0].get("message", {})
        function_call = message.get("function_call", {})
        arguments = function_call.get("arguments")

        if not arguments:
            raise ValueError("OpenAI did not return function_call.arguments.")

        result = json.loads(arguments)

        # Ensure all expected keys exist for frontend compatibility
        result.setdefault("summary", "No summary provided.")
        result.setdefault("conditions", [])
        result.setdefault("severity", "unknown")
        result.setdefault("extractedElements", [])

        # Save full result with extractedElements to a JSON file
        # with open("last_analysis_result.json", "w") as f:
        #     json.dump(result, f, indent=2)
        print(result)

        # Return only the parts meant for frontend (if needed, filter here)
        return result

    except requests.exceptions.RequestException as req_err:
        print(f"\u274c HTTP error: {req_err}")
        raise
    except json.JSONDecodeError:
        print("\u274c Failed to parse JSON from OpenAI response.")
        raise
    except Exception as e:
        print(f"\u274c Unexpected error: {e}")
        raise