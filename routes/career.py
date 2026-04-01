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
    # 🔥 FIX profile_summary (force string always)
    ps = data.get("profile_summary", "")
    if isinstance(ps, dict):
        ps = " ".join([str(v) for v in ps.values()])
    elif isinstance(ps, list):
        ps = " ".join([str(v) for v in ps])
    else:
        ps = str(ps)

    data["profile_summary"] = ps
    data["current_skills"] = data.get("current_skills", [])
    data["careers"] = data.get("careers", [])

    for c in data["careers"]:

        try:
            c["match_score"] = int(c.get("match_score", 0))
        except:
            c["match_score"] = 0

        c["salary_range"] = str(c.get("salary_range", ""))
        c["reason"] = str(c.get("reason", ""))

        # 🔥 SAFE skill_gap_analysis
        safe_gap = {}
        for k, v in c.get("skill_gap_analysis", {}).items():
            try:
                if isinstance(v, list):
                    v = v[0] if len(v) > 0 else 0
                safe_gap[k] = float(v)
            except:
                safe_gap[k] = 0.0

        c["skill_gap_analysis"] = safe_gap

        # 🔥 FORCE LIST TYPES (avoid crashes in Android)
        def ensure_list(val):
            if isinstance(val, list):
                return val
            if val is None:
                return []
            return [str(val)]

        c["next_steps"] = ensure_list(c.get("next_steps", []))
        c["learning_path"] = ensure_list(c.get("learning_path", []))
        c["interview_tips"] = ensure_list(c.get("interview_tips", []))
        c["top_companies"] = ensure_list(c.get("top_companies", []))
        c["certifications"] = ensure_list(c.get("certifications", []))

        c["job_search_keywords"] = str(c.get("job_search_keywords", ""))

    return data


@router.post("/analyze-pdf")
async def analyze_pdf(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        resume_text = extract_text(contents)

     prompt = f"""
You are an expert AI career advisor.

Analyze the resume and return STRICT JSON.

IMPORTANT RULES:
- Return AT LEAST 5 career paths
- match_score must be realistic (40–95 range)
- Be logical and not overly harsh
- Include diverse roles

Resume:
{resume_text}

FORMAT:
{{
  "profile_summary": "concise summary",
  "current_skills": ["skills"],
  "careers": [
    {{
      "title": "career role",
      "match_score": 0-100,
      "salary_range": "string",
      "reason": "why suitable",
      "skill_gap_analysis": {{"skill": 0.5}},
      "next_steps": ["steps"],
      "learning_path": ["courses"],
      "interview_tips": ["tips"],
      "job_search_keywords": "keywords",
      "top_companies": ["companies"],
      "certifications": ["certs"]
    }}
  ]
}}
"""

        response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    temperature=0.3,
    max_tokens=1200,
    response_format={"type": "json_object"},
    messages=[{"role": "user", "content": prompt}],
)

        raw = response.choices[0].message.content

        try:
            data = json.loads(raw)
        except:
            return {"error": "Invalid JSON from AI", "raw": raw}

        return normalize(data)

    except Exception as e:
        return {"error": str(e)}
