# backend/main.py
import os, json
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai

from .utils import extract_text_from_pdf_bytes, chunk_text, SimpleRAG

# Load .env values (API key, model, temperature)
load_dotenv()
API_KEY = "AIzaSyActA625CPEaMTv5f8yVRy-NCpCv5nngOA"
MODEL_NAME = "gemini-2.0-flash"
TEMP = 0.2

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing in .env")
genai.configure(api_key=API_KEY)

app = FastAPI(title="AI Interview Prep Assistant")

# ---- In-memory (for MVP). Later you can persist to MongoDB.
RAG = SimpleRAG()
LAST_QUESTIONS: List[str] = []  # store latest batch for feedback UI

class QuestionRequest(BaseModel):
    role: str
    experience: str
    topics: Optional[List[str]] = None
    n_questions: int = 5

class FeedbackRequest(BaseModel):
    question: str
    answer: str
    role: Optional[str] = None
    experience: Optional[str] = None

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Receive a PDF, extract text, chunk it, and build a TF-IDF index (RAG).
    """
    try:
        pdf_bytes = await file.read()
        text = extract_text_from_pdf_bytes(pdf_bytes)
        chunks = chunk_text(text, max_chars=1000, overlap=120)
        if not chunks:
            raise ValueError("No text could be extracted from the PDF.")
        RAG.build(chunks)
        return {"chunks": len(chunks)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/generate_questions")
async def generate_questions(req: QuestionRequest):
    """
    Use RAG context + Gemini to generate interview questions.
    """
    topics_line = ", ".join(req.topics) if req.topics else "core fundamentals"
    query = f"{req.experience} {req.role} {topics_line}"
    context = RAG.context_for(query, k=6, max_chars=1600) if RAG.chunks else "(no JD context)"

    system_style = (
        "You are a Chief Interviewer at a top MNC. Be rigorous but fair, "
        "prefer practical scenarios, and keep wording concise."
    )

    prompt = f"""
{system_style}

Generate {req.n_questions} technical interview questions for a {req.experience} {req.role}.
Focus on {topics_line}. Vary difficulty (easy/medium/hard).
If the context is relevant, use it to make questions job-specific.

Context (optional):
{context}

Return the questions as a numbered list. Do not include answers.
"""

    model = genai.GenerativeModel(MODEL_NAME)
    resp = model.generate_content(prompt, generation_config={"temperature": TEMP})
    text = resp.text.strip()

    # Basic cleanup → store questions so the UI can request feedback later
    lines = [ln.strip(" -") for ln in text.splitlines() if ln.strip()]
    # Filter only lines that look like questions
    questions = [ln for ln in lines if ln[0].isdigit() or ln.endswith("?") or ln.lower().startswith("q")]
    if not questions:
        questions = lines
    global LAST_QUESTIONS
    LAST_QUESTIONS = questions[: req.n_questions]
    return {"questions": LAST_QUESTIONS}

@app.post("/feedback")
async def feedback(body: FeedbackRequest):
    """
    Grade a candidate's answer with a short rubric and score (0–10).
    """
    context = RAG.context_for(body.question, k=5, max_chars=1200) if RAG.chunks else "(no JD context)"
    system_style = (
        "You are a Chief Interviewer at a top MNC. Grade answers strictly but fairly. "
        "Be specific and actionable in feedback."
    )

    grading_prompt = f"""
{system_style}

Question:
{body.question}

Candidate Answer:
\"\"\"{body.answer}\"\"\"

Optional Context (JD or topics):
{context}

Return STRICT JSON with the following keys:
{{
  "score": <integer 0-10>,
  "verdict": "<one-sentence summary>",
  "strengths": ["<bullet>", "..."],
  "improvements": ["<bullet>", "..."],
  "suggested_answer": "<a strong model answer (concise)>"
}}
Only output JSON. No extra text.
"""

    model = genai.GenerativeModel(MODEL_NAME)
    resp = model.generate_content(grading_prompt, generation_config={"temperature": TEMP})

    raw = resp.text.strip()
    # Make a best-effort to parse JSON even if the model wraps it with code fences
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:].strip()
    try:
        data = json.loads(raw)
    except Exception:
        data = {
            "score": 0,
            "verdict": "Could not parse model JSON.",
            "strengths": [],
            "improvements": ["Please retry."],
            "suggested_answer": ""
        }
    # Clip/normalize score
    try:
        data["score"] = max(0, min(10, int(data.get("score", 0))))
    except Exception:
        data["score"] = 0
    return data
