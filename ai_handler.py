"""
AI Handler — Groq (primary) + Cohere (fallback).
Keys are stored as Render environment variables.
"""

import os
from groq import Groq
import cohere

GROQ_API_KEY   = os.environ.get("GROQ_API_KEY", "")
COHERE_API_KEY = os.environ.get("COHERE_API_KEY", "")

GROQ_MODEL   = "llama-3.3-70b-versatile"
COHERE_MODEL = "command-r-plus"


def get_ai_response(prompt: str) -> str:
    """Call Groq first; fall back to Cohere if Groq fails."""
    if GROQ_API_KEY:
        try:
            client = Groq(api_key=GROQ_API_KEY)
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4096,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as groq_err:
            print(f"Groq failed: {groq_err} — trying Cohere")

    if COHERE_API_KEY:
        try:
            co = cohere.ClientV2(api_key=COHERE_API_KEY)
            response = co.chat(
                model=COHERE_MODEL,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.message.content[0].text
        except Exception as cohere_err:
            raise RuntimeError(f"Both providers failed. Cohere error: {cohere_err}")

    raise RuntimeError("No AI provider configured. Set GROQ_API_KEY or COHERE_API_KEY on Render.")


def extract_pdf_text(pdf_bytes: bytes) -> str:
    """Extract text from PDF bytes using pdfplumber."""
    import pdfplumber
    import io
    text = ""
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()
