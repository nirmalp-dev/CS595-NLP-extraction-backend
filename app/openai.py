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
             "content": "You are a helpful assistant for text summarization of medical report like lab reports, clinical notes, radiology reports, pathology reports, etc."},
            {"role": "user", "content": f"Summarize the following text:\n\n{text}"}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()