from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ai_handler import get_gemini_response

router = APIRouter()

class InterviewRequest(BaseModel):
    role: str
    experience_level: str = "fresher"  # fresher, junior, mid, senior
    domain: str = "general"
    num_questions: int = 10
    api_key: str
    model: str = "gemini-1.5-flash"

class FeedbackRequest(BaseModel):
    question: str
    answer: str
    role: str
    api_key: str
    model: str = "gemini-1.5-flash"

@router.post("/generate-questions")
async def generate_questions(request: InterviewRequest):
    prompt = f"""
    You are an expert interviewer at a top tech company. Generate {request.num_questions} interview questions 
    for a {request.experience_level} {request.role} position in the {request.domain} domain.

    Include a mix of:
    - Technical questions (60%)
    - Behavioral/situational questions (25%)
    - Role-specific scenario questions (15%)

    For each question, provide:
    1. The question
    2. Category (Technical/Behavioral/Scenario)
    3. Difficulty (Easy/Medium/Hard)
    4. Key points to cover in the answer (2-3 bullet points)

    Format as JSON array like:
    [
      {{
        "question": "...",
        "category": "Technical",
        "difficulty": "Medium",
        "key_points": ["point1", "point2", "point3"]
      }}
    ]

    Return ONLY the JSON array, no other text.
    """
    try:
        result = get_gemini_response(prompt, request.api_key, request.model)
        # Clean JSON
        result = result.strip()
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]
        import json
        questions = json.loads(result.strip())
        return {"questions": questions, "role": request.role, "level": request.experience_level}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/evaluate-answer")
async def evaluate_answer(request: FeedbackRequest):
    prompt = f"""
    You are an expert interviewer evaluating a candidate's answer for a {request.role} position.

    Question: {request.question}

    Candidate's Answer: {request.answer}

    Provide structured feedback:

    ## Score: X/10
    
    ## Strengths
    - What they did well

    ## Areas to Improve
    - What was missing or could be better

    ## Model Answer Outline
    - Key points they should have covered

    ## Tips
    - Specific advice to improve this type of answer
    """
    try:
        result = get_gemini_response(prompt, request.api_key, request.model)
        return {"feedback": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
