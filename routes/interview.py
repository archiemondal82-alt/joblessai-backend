from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ai_handler import get_ai_response
import json

router = APIRouter()

class InterviewRequest(BaseModel):
    role: str
    experience_level: str = "fresher"
    domain: str = "general"
    num_questions: int = 10

class FeedbackRequest(BaseModel):
    question: str
    answer: str
    role: str


@router.post("/generate-questions")
async def generate_questions(request: InterviewRequest):
    prompt = f"""
Generate {request.num_questions} interview questions.

Role: {request.role}
Experience: {request.experience_level}
Domain: {request.domain}

Return JSON:
[
  {{
    "question": "",
    "category": "",
    "difficulty": "",
    "key_points": ["", "", ""]
  }}
]
"""

    try:
        result = get_ai_response(prompt)
        result = result.strip()

        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]

        questions = json.loads(result)

        if not isinstance(questions, list):
            questions = []

        return {
            "questions": questions,
            "role": request.role,
            "level": request.experience_level
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/evaluate-answer")
async def evaluate_answer(request: FeedbackRequest):
    prompt = f"""
Evaluate this answer.

Question: {request.question}
Answer: {request.answer}

Give:
- Score out of 10
- Strengths
- Improvements
- Better answer outline
"""

    try:
        result = get_ai_response(prompt)
        return {"feedback": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
