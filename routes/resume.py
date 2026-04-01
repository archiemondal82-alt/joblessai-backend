from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from ai_handler import get_gemini_response
import io

router = APIRouter()

class ResumeRequest(BaseModel):
    name: str
    email: str
    phone: str
    linkedin: Optional[str] = ""
    github: Optional[str] = ""
    summary: str
    experience: str
    education: str
    skills: str
    projects: Optional[str] = ""
    certifications: Optional[str] = ""
    target_role: str
    api_key: str
    model: str = "gemini-1.5-flash"

class EnhanceRequest(BaseModel):
    section: str
    content: str
    target_role: str
    api_key: str
    model: str = "gemini-1.5-flash"

@router.post("/enhance-section")
async def enhance_section(request: EnhanceRequest):
    """AI-enhance a specific resume section."""
    prompt = f"""
    You are an expert resume writer. Enhance the following {request.section} section 
    for a {request.target_role} position. Make it ATS-optimized, impactful, and professional.
    Use strong action verbs and quantify achievements where possible.
    Return ONLY the enhanced content, no explanations.

    Original content:
    {request.content}
    """
    try:
        result = get_gemini_response(prompt, request.api_key, request.model)
        return {"enhanced": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-pdf")
async def generate_resume_pdf(request: ResumeRequest):
    """Generate a professional ATS-optimized PDF resume."""
    try:
        pdf_bytes = _build_pdf(request)
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={request.name.replace(' ', '_')}_Resume.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _build_pdf(req: ResumeRequest) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm, mm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    import io

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=1.2*cm, bottomMargin=1.2*cm)

    accent = colors.HexColor("#1a1a2e")
    light_accent = colors.HexColor("#16213e")

    styles = getSampleStyleSheet()
    name_style = ParagraphStyle("name", fontSize=22, fontName="Helvetica-Bold",
        textColor=accent, alignment=TA_LEFT, spaceAfter=2)
    contact_style = ParagraphStyle("contact", fontSize=9, fontName="Helvetica",
        textColor=colors.HexColor("#555555"), alignment=TA_LEFT, spaceAfter=8)
    section_style = ParagraphStyle("section", fontSize=11, fontName="Helvetica-Bold",
        textColor=accent, spaceBefore=10, spaceAfter=4)
    body_style = ParagraphStyle("body", fontSize=9.5, fontName="Helvetica",
        textColor=colors.HexColor("#222222"), spaceAfter=3, leading=14)
    bold_body = ParagraphStyle("boldbody", fontSize=9.5, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#222222"), spaceAfter=2)

    def section_header(title):
        return [
            Paragraph(title.upper(), section_style),
            HRFlowable(width="100%", thickness=1, color=accent, spaceAfter=4)
        ]

    story = []

    # Name
    story.append(Paragraph(req.name, name_style))

    # Contact line
    contact_parts = [req.email, req.phone]
    if req.linkedin: contact_parts.append(req.linkedin)
    if req.github: contact_parts.append(req.github)
    story.append(Paragraph(" | ".join(contact_parts), contact_style))
    story.append(HRFlowable(width="100%", thickness=2, color=accent, spaceAfter=6))

    # Summary
    if req.summary:
        story += section_header("Professional Summary")
        story.append(Paragraph(req.summary, body_style))

    # Experience
    if req.experience:
        story += section_header("Work Experience")
        for line in req.experience.strip().split("\n"):
            if line.strip():
                if line.strip().startswith("•") or line.strip().startswith("-"):
                    story.append(Paragraph(f"&nbsp;&nbsp;{line.strip()}", body_style))
                else:
                    story.append(Paragraph(line.strip(), bold_body))

    # Education
    if req.education:
        story += section_header("Education")
        for line in req.education.strip().split("\n"):
            if line.strip():
                story.append(Paragraph(line.strip(), body_style))

    # Skills
    if req.skills:
        story += section_header("Skills")
        story.append(Paragraph(req.skills, body_style))

    # Projects
    if req.projects:
        story += section_header("Projects")
        for line in req.projects.strip().split("\n"):
            if line.strip():
                if line.strip().startswith("•") or line.strip().startswith("-"):
                    story.append(Paragraph(f"&nbsp;&nbsp;{line.strip()}", body_style))
                else:
                    story.append(Paragraph(line.strip(), bold_body))

    # Certifications
    if req.certifications:
        story += section_header("Certifications")
        for line in req.certifications.strip().split("\n"):
            if line.strip():
                story.append(Paragraph(f"• {line.strip()}", body_style))

    doc.build(story)
    return buf.getvalue()
