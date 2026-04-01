from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ai_handler import get_gemini_response

router = APIRouter()

class CompareRequest(BaseModel):
    path1: str
    path2: str
    background: str = ""
    api_key: str
    model: str = "gemini-1.5-flash"

@router.post("/compare-paths")
async def compare_paths(request: CompareRequest):
    prompt = f"""
    You are an expert career advisor. Compare these two career paths in detail:

    Path A: {request.path1}
    Path B: {request.path2}
    {"Candidate background: " + request.background if request.background else ""}

    Provide a comprehensive comparison:

    ## 💰 Salary Comparison (INR)
    | Level | {request.path1} | {request.path2} |
    |-------|---------|---------|
    | Entry | X LPA | X LPA |
    | Mid | X LPA | X LPA |
    | Senior | X LPA | X LPA |

    ## 📈 Growth Trajectory
    - Path A growth outlook
    - Path B growth outlook

    ## 🛠️ Skills Required
    **{request.path1}:** key skills
    **{request.path2}:** key skills

    ## ⚖️ Pros & Cons
    **{request.path1}:**
    Pros: ...
    Cons: ...

    **{request.path2}:**
    Pros: ...
    Cons: ...

    ## 🎯 Who Should Choose Which
    - Choose {request.path1} if...
    - Choose {request.path2} if...

    ## 🏆 Final Recommendation
    {"Based on the candidate's background, " if request.background else ""}Which path is better and why.
    """
    try:
        result = get_gemini_response(prompt, request.api_key, request.model)
        return {"comparison": result, "path1": request.path1, "path2": request.path2}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
