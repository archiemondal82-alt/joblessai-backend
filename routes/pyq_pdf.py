from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import io

router = APIRouter()

@router.post("/api/pyq/pdf")
def generate_pdf(data: dict):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)

    elements = []

    for q in data.get("questions", []):
        elements.append(Paragraph(q["question"]))
        elements.append(Spacer(1, 10))

    doc.build(elements)
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="application/pdf")
