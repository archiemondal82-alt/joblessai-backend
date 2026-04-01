from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ai_handler import get_gemini_response

router = APIRouter()

class PYQRequest(BaseModel):
    domain: str
    company: str = "general"
    year_range: str = "2020-2024"
    num_questions: int = 15
    api_key: str
    model: str = "gemini-1.5-flash"

@router.post("/get-questions")
async def get_pyq(request: PYQRequest):
    prompt = f"""
    You are a database of previous year interview questions. Generate {request.num_questions} 
    realistic previous year interview questions for {request.domain} roles 
    {"at " + request.company if request.company != "general" else "at top tech companies"} 
    from {request.year_range}.

    For each question include:
    - The actual question asked
    - Year and company (approximate)
    - Topic/concept being tested
    - Difficulty level
    - Brief solution approach

    Format as JSON:
    [
      {{
        "question": "...",
        "year": "2023",
        "company": "...",
        "topic": "...",
        "difficulty": "Medium",
        "approach": "..."
      }}
    ]

    Return ONLY valid JSON array.
    """
    try:
        result = get_gemini_response(prompt, request.api_key, request.model)
        result = result.strip()
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]
        import json
        questions = json.loads(result.strip())
        return {"questions": questions, "domain": request.domain}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


DOMAINS = [
    "Software Engineering", "Data Science", "Machine Learning",
    "Frontend Development", "Backend Development", "DevOps",
    "Product Management", "System Design", "Android Development",
    "Electrical Engineering", "VLSI", "Embedded Systems",
    "Power Electronics", "Signal Processing", "Mechanical Engineering",
    "Civil Engineering", "Finance", "Marketing", "HR", "Operations"
]

@router.get("/domains")
def get_domains():
    return {"domains": DOMAINS}
