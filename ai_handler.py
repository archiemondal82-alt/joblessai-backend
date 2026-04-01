"""
AI Handler — wraps Gemini API (same logic as your Streamlit app)
"""

import os
import google.generativeai as genai
from typing import Optional

def get_gemini_response(prompt: str, api_key: str, model: str = "gemini-1.5-flash") -> str:
    """Call Gemini API and return text response."""
    genai.configure(api_key=api_key)
    model_instance = genai.GenerativeModel(model)
    response = model_instance.generate_content(prompt)
    return response.text

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
