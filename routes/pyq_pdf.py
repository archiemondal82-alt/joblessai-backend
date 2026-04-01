from fastapi import APIRouter
from fastapi.responses import FileResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import os

router = APIRouter()

@router.post("/generate-pdf")
def generate_pdf(data: dict):
    file_path = "pyq_output.pdf"

    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph("JobLess AI — PYQ Pack", styles["Title"]))
    content.append(Spacer(1, 20))

    questions = data.get("questions", [])

    for i, q in enumerate(questions, 1):
        content.append(Paragraph(f"<b>Q{i}. {q.get('question','')}</b>", styles["Normal"]))
        content.append(Spacer(1, 8))

        content.append(Paragraph(f"<i>Approach:</i> {q.get('approach','')}", styles["Normal"]))
        content.append(Spacer(1, 16))

    doc.build(content)

    return FileResponse(file_path, filename="PYQ.pdf")
