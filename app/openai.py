import requests
OPENAI_API_KEY = "<key goes here>"

def summarize_text_with_openai(text, model="gpt-4o-mini", max_tokens=150, temperature=0.7):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [
            {"role": "system",
             "content": "You are a healthcare expert. Your main task is to analyze the report and provide a structured output containing 3 sections. 1. summary: Report summarization in 100 words 2. conditions: List of conditions detected in the report 3. severity: severity of the conditions detected in the report"},
            {"role": "user", "content": f"Summarize the following text:\n\n{text}"}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()
