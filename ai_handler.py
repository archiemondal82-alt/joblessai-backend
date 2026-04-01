"""
AI Handler — Cohere primary, Groq as backup via direct HTTP.
"""

import os
import cohere

COHERE_API_KEY = os.environ.get("COHERE_API_KEY", "")
GROQ_API_KEY   = os.environ.get("GROQ_API_KEY", "")

def get_ai_response(prompt: str) -> str:
    if COHERE_API_KEY:
        try:
            co = cohere.ClientV2(api_key=COHERE_API_KEY)
            response = co.chat(
                model="command-r-plus",
                messages=[{"role": "user", "content": prompt}],
            )
            return response.message.content[0].text
        except Exception as e:
            print(f"Cohere failed: {e}")

    if GROQ_API_KEY:
        try:
            import httpx
            r = httpx.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "max_tokens": 4096},
                timeout=60
            )
            return r.json()["choices"][0]["message"]["content"]
        except Exception as e:
            raise RuntimeError(f"Both failed. Groq error: {e}")

    raise RuntimeError("No API keys configured.")


def extract_pdf_text(pdf_bytes: bytes) -> str:
    import pdfplumber, io
    text = ""
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    return text.strip()
