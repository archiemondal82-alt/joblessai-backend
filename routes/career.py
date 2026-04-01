@router.post("/analyze-pdf")
async def analyze_pdf(file: UploadFile = File(...)):
    try:
        contents = await file.read()

        # ✅ 10MB LIMIT
        if len(contents) > 10 * 1024 * 1024:
            return {"error": "File too large (max 10MB)"}

        resume_text = extract_text(contents)

        prompt = f"""You are an expert AI career advisor.

IMPORTANT:
- Return EXACTLY 10 career paths
- match_score between 50–95
- No duplicates

Resume:
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
}}"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            temperature=0.3,
            max_tokens=1200,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}],
        )

        data = json.loads(response.choices[0].message.content)

        if not isinstance(data.get("careers"), list):
            data["careers"] = []

        return normalize(data)

    except Exception as e:
        return {"error": str(e)}
