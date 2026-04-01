from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from pydantic import BaseModel
from ai_handler import get_ai_response, extract_pdf_text

router = APIRouter()

class CareerRequest(BaseModel):
    resume_text: str
    analysis_depth: str = "comprehensive"
    include_learning_path: bool = True
    include_interview_prep: bool = True

@router.post("/analyze")
async def analyze_career(request: CareerRequest):
    depth_map = {
        "quick": "Provide a brief 3-5 bullet point summary.",
        "standard": "Provide a standard analysis with key sections.",
        "comprehensive": "Provide an in-depth comprehensive analysis with detailed sections.",
    }
    depth_instruction = depth_map.get(request.analysis_depth, depth_map["comprehensive"])

    learning_section = """
    ## 📚 Learning Path
    - Recommend specific courses, certifications, or skills to acquire
    - Include estimated timelines
    - Suggest YouTube channels or free resources
    """ if request.include_learning_path else ""

    interview_section = """
    ## 🎯 Interview Preparation
    - Top 5 technical questions for target roles
    - Top 3 behavioral questions
    - Key talking points from resume
    """ if request.include_interview_prep else ""

    prompt = f"""
    You are an expert career counselor and resume analyst. Analyze the following resume and provide actionable career guidance.

    {depth_instruction}

    Resume Content:
    {request.resume_text}

    Please provide:

    ## 🎯 Career Profile Summary
    - Current level and specialization
    - Key strengths identified

    ## 💼 Top Career Path Recommendations
    For each path provide: Role title, why it fits, salary range (INR), growth potential

    ## ⚡ Skills Gap Analysis
    - Strong skills (already present)
    - Missing skills for target roles
    - Quick wins to add

    ## 📄 Resume Improvement Tips
    - ATS optimization suggestions
    - Formatting recommendations
    - Content gaps

    {learning_section}
    {interview_section}

    ## 🚀 30-60-90 Day Action Plan
    - Immediate actions (next 30 days)
    - Short-term goals (60 days)
    - Medium-term milestones (90 days)
    """

    try:
        result = get_ai_response(prompt)
        return {"analysis": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-pdf")
async def analyze_career_pdf(
    file: UploadFile = File(...),
    analysis_depth: str = Form("comprehensive"),
    include_learning_path: bool = Form(True),
    include_interview_prep: bool = Form(True),
):
    pdf_bytes = await file.read()
    resume_text = extract_pdf_text(pdf_bytes)
    if not resume_text:
        raise HTTPException(status_code=400, detail="Could not extract text from PDF.")

    req = CareerRequest(
        resume_text=resume_text,
        analysis_depth=analysis_depth,
        include_learning_path=include_learning_path,
        include_interview_prep=include_interview_prep,
    )
    return await analyze_career(req)
