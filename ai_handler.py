from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_ai_response(prompt: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        temperature=0.3,
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def extract_pdf_text(pdf_bytes: bytes) -> str:
    import pdfplumber, io
    text = ""
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    return text.strip()
