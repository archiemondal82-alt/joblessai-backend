from fastapi import APIRouter, UploadFile, File
import fitz
import os
import json
from groq import Groq

router = APIRouter()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_text(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def normalize(data):
    data["profile_summary"] = data.get("profile_summary", "")
    data["current_skills"] = data.get("current_skills", [])
    data["careers"] = data.get("careers", [])

    for c in data["careers"]:
        c["match_score"] = int(c.get("match_score", 0))
        c["salary_range"] = c.get("salary_range", "")
        c["reason"] = c.get("reason", "")
        c["skill_gap_analysis"] = {
            k: float(v) for k, v in c.get("skill_gap_analysis", {}).items()
        }
        c["next_steps"] = c.get("next_steps", [])
        c["learning_path"] = c.get("learning_path", [])
        c["interview_tips"] = c.get("interview_tips", [])
        c["job_search_keywords"] = c.get("job_search_keywords", "")
        c["top_companies"] = c.get("top_companies", [])
        c["certifications"] = c.get("certifications", [])

    return data

@router.post("/analyze-pdf")
async def analyze_pdf(file: UploadFile = File(...)):
    contents = await file.read()
    resume_text = extract_text(contents)

    prompt = f"""
Analyze this resume and return STRICT JSON:

{resume_text}

FORMAT:
{{
  "profile_summary": "",
  "current_skills": [],
  "careers": [
    {{
      "title": "",
      "match_score": 0,
      "salary_range": "",
      "reason": "",
      "skill_gap_analysis": {{}},
      "next_steps": [],
      "learning_path": [],
      "interview_tips": [],
      "job_search_keywords": "",
      "top_companies": [],
      "certifications": []
    }}
  ]
}}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}],
    )

    data = json.loads(response.choices[0].message.content)

    return normalize(data)
