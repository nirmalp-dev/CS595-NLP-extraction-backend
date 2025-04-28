import requests
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def summarize_text_with_openai(text, model="gpt-4o-mini", max_tokens=300, temperature=0.7):
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key not found in environment variables")
        
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Define the JSON structure we want OpenAI to return
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
                    "items": {
                        "type": "string"
                    },
                    "description": "List of medical conditions detected in the report"
                },
                "severity": {
                    "type": "string",
                    "description": "Overall severity of the conditions detected (e.g., mild, moderate, severe)"
                }
            },
            "required": ["summary", "conditions", "severity"]
        }
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "system", 
             "content": "You are a healthcare expert that analyzes medical reports. Extract the key information and provide it in a structured format."},
            {"role": "user", "content": f"Analyze the following medical text and extract the key information:\n\n{text}"}
        ],
        "functions": [function_schema],
        "function_call": {"name": "health_report_analyzer"},
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        # Extract and parse the function arguments as JSON
        function_args = response.json()["choices"][0]["message"]["function_call"]["arguments"]
        result = json.loads(function_args)
        
        return result
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        raise
