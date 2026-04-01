"""
JobLess AI — FastAPI Backend
Exposes all Streamlit tab logic as REST endpoints.
Deploy on Render — set GROQ_API_KEY as env var.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import routers
from routes import career, resume, interview, pyq, compare

app = FastAPI(title="JobLess AI API", version="1.0.0")

# CORS (keep as is)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers (keep EXACTLY like this)
app.include_router(career.router,    prefix="/api/career",    tags=["Career"])
app.include_router(resume.router,    prefix="/api/resume",    tags=["Resume"])
app.include_router(interview.router, prefix="/api/interview", tags=["Interview"])
app.include_router(pyq.router,       prefix="/api/pyq",       tags=["PYQ"])
app.include_router(compare.router,   prefix="/api/compare",   tags=["Compare"])

# Health check
@app.get("/")
def root():
    return {"status": "JobLess AI API is running"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
