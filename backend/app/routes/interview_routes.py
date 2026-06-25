from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from uuid import uuid4
from app.services.profile_analyzer import analyze_profile
from app.services.interview_planner import create_interview_plan
from app.services.interviewer import generate_first_question, generate_next_question
from app.services.evaluator import evaluate_answer
from app.services.report_generator import generate_final_report

router = APIRouter()
sessions: Dict[str, Dict[str, Any]] = {}


class StartInterviewRequest(BaseModel):
    resume_text: str = Field(..., min_length=20)
    job_description: str = Field(..., min_length=20)
    role: str = Field(..., min_length=2)
    duration_minutes: int = Field(default=30)
    difficulty: str = Field(default="mid")


class AnswerRequest(BaseModel):
    session_id: str
    answer: str = Field(..., min_length=1)


@router.post("/start")
def start_interview(request: StartInterviewRequest):
    profile = analyze_profile(request.resume_text, request.job_description, request.role)
    plan = create_interview_plan(profile, request.duration_minutes, request.role, request.difficulty)

    session_id = str(uuid4())
    session = {
        "session_id": session_id,
        "role": request.role,
        "duration_minutes": request.duration_minutes,
        "difficulty": request.difficulty,
        "profile": profile,
        "plan": plan,
        "history": [],
        "evaluations": [],
        "current_question": None,
        "status": "in_progress",
    }

    first_question = generate_first_question(session)
    session["current_question"] = first_question
    session["history"].append({"interviewer": first_question})
    sessions[session_id] = session

    return {
        "session_id": session_id,
        "profile": profile,
        "interview_plan": plan,
        "first_question": first_question,
    }


@router.post("/answer")
def submit_answer(request: AnswerRequest):
    session = sessions.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")
    if session.get("status") != "in_progress":
        raise HTTPException(status_code=400, detail="Interview session is not active.")

    current_question = session["current_question"]
    session["history"].append({"candidate": request.answer})

    evaluation = evaluate_answer(current_question, request.answer, session)
    session["evaluations"].append({
        "question": current_question,
        "answer": request.answer,
        "evaluation": evaluation,
    })

    next_question = generate_next_question(session, evaluation)
    session["current_question"] = next_question
    session["history"].append({"interviewer": next_question})

    return {
        "next_question": next_question,
        "turn_count": len(session["evaluations"]),
    }


@router.post("/end/{session_id}")
def end_interview(session_id: str):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")

    report = generate_final_report(session)
    session["status"] = "completed"
    session["report"] = report

    return {
        "session_id": session_id,
        "report": report,
        "evaluations": session.get("evaluations", []),
    }


@router.get("/session/{session_id}")
def get_session(session_id: str):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")
    return session
