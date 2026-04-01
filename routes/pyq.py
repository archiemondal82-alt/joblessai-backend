from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ai_handler import get_ai_response
import json

router = APIRouter()

class PYQRequest(BaseModel):
    domain: str
    company: str = "general"
    year_range: str = "2020-2024"
    num_questions: int = 15


@router.post("/get-questions")
async def get_pyq(request: PYQRequest):
    prompt = f"""Generate {request.num_questions} interview questions.

Domain: {request.domain}
Company: {request.company}
Years: {request.year_range}

Return STRICT JSON:
{{
  "questions": [
    {{
      "question": "",
      "approach": ""
    }}
  ]
}}"""

    try:
        result = get_ai_response(prompt)
        result = result.strip()

        # 🔥 CLEAN MARKDOWN IF ANY
        if "```" in result:
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]

        # 🔥 SAFE PARSE
        try:
            data = json.loads(result)
        except:
            return {"questions": []}

        # 🔥 FORCE STRUCTURE
        if isinstance(data, list):
            return {"questions": data}

        if not isinstance(data, dict):
            return {"questions": []}

        questions = data.get("questions", [])

        if not isinstance(questions, list):
            questions = []

        return {"questions": questions}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
