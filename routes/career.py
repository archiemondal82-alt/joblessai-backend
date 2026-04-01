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
    data["profile_summary"] = str(data.get("profile_summary", ""))
    data["current_skills"] = data.get("current_skills", [])
    careers = data.get("careers", [])

    if not isinstance(careers, list) or len(careers) == 0:
        careers = []

    final = []

    for c in careers[:10]:
        try:
            match = int(c.get("match_score", 60))
        except:
            match = 60

        final.append({
            "title": str(c.get("title", "Career")),
            "match_score": max(40, min(match, 95)),
            "salary_range": str(c.get("salary_range", "")),
            "reason": str(c.get("reason", "")),
            "skill_gap_analysis": c.get("skill_gap_analysis", {}),
            "next_steps": c.get("next_steps", []),
            "learning_path": c.get("learning_path", []),
            "interview_tips": c.get("interview_tips", []),
            "job_search_keywords": str(c.get("job_search_keywords", "")),
            "top_companies": c.get("top_companies", []),
            "certifications": c.get("certifications", [])
        })

    data["careers"] = final
    return data


@router.post("/analyze-pdf")
async def analyze_pdf(file: UploadFile = File(...)):
    try:
        contents = await file.read()

        if len(contents) > 10 * 1024 * 1024:
            return {"error": "File too large (max 10MB)"}

        resume_text = extract_text(contents)

        prompt = f"""
You are a REAL-WORLD career analyst.

IMPORTANT RULES:
- Detect user's COUNTRY from resume
- Use REAL salary ranges in THAT country's currency
- Give EXACTLY 10 careers
- Score based on:
  skills match
  experience
  projects
- Scores must be realistic (50–90)

Resume:
{resume_text}

RETURN JSON:
{{
  "profile_summary": "",
  "current_skills": [],
  "careers": [
    {{
      "title": "",
      "match_score": 75,
      "salary_range": "₹6–12 LPA / $70k–120k / £40k–80k",
      "reason": "based on skills",
      "skill_gap_analysis": {{"skill": 0.4}},
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
            model="llama-3.1-8b-instant",
            temperature=0.4,
            max_tokens=1500,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}],
        )

        try:
            data = json.loads(response.choices[0].message.content)
        except:
            data = {}

        return normalize(data)

    except Exception as e:
        return {"error": str(e)}
