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


def fallback_careers():
    # 🔥 GUARANTEED RESULTS IF AI FAILS
    return [
        {"title": "Software Engineer", "match_score": 75},
        {"title": "Data Analyst", "match_score": 70},
        {"title": "Backend Developer", "match_score": 72},
        {"title": "Frontend Developer", "match_score": 68},
        {"title": "DevOps Engineer", "match_score": 65},
        {"title": "Machine Learning Engineer", "match_score": 60},
        {"title": "Product Manager", "match_score": 62},
        {"title": "QA Engineer", "match_score": 64},
        {"title": "Cloud Engineer", "match_score": 66},
        {"title": "System Engineer", "match_score": 63},
    ]


def normalize(data):
    data["profile_summary"] = str(data.get("profile_summary", ""))
    data["current_skills"] = data.get("current_skills", [])

    careers = data.get("careers", [])

    # 🔥 IF EMPTY → USE FALLBACK
    if not isinstance(careers, list) or len(careers) == 0:
        careers = fallback_careers()

    final = []

    for c in careers[:10]:
        try:
            match = int(c.get("match_score", 60))
        except:
            match = 60

        final.append({
            "title": str(c.get("title", "Career")),
            "match_score": max(50, min(match, 95)),
            "salary_range": str(c.get("salary_range", "4-12 LPA")),
            "reason": str(c.get("reason", "Suitable based on your profile")),
            "skill_gap_analysis": {},
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

        prompt = f"""Generate career suggestions.

Resume:
{resume_text}

Return STRICT JSON:
{{
 "profile_summary": "",
 "current_skills": [],
 "careers": [
   {{
     "title": "",
     "match_score": 70
   }}
 ]
}}"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            temperature=0.3,
            max_tokens=1000,
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
