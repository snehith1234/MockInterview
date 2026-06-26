from typing import Dict, Any, Optional
from datetime import datetime, timezone
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

# Maximum overtime allowed beyond scheduled duration (in minutes)
MAX_OVERTIME_MINUTES = 15


class StartInterviewRequest(BaseModel):
    resume_text: str = Field(..., min_length=20)
    job_description: str = Field(..., min_length=20)
    role: str = Field(..., min_length=2)
    company: Optional[str] = Field(default=None)
    duration_minutes: int = Field(default=30)
    difficulty: str = Field(default="mid")


class AnswerRequest(BaseModel):
    session_id: str
    answer: str = Field(..., min_length=1)


def _get_elapsed_minutes(session: Dict[str, Any]) -> float:
    """Calculate elapsed minutes since interview started."""
    start_time = session.get("start_time")
    if not start_time:
        return 0
    now = datetime.now(timezone.utc)
    elapsed = (now - start_time).total_seconds() / 60.0
    return round(elapsed, 1)


def _get_time_status(session: Dict[str, Any]) -> Dict[str, Any]:
    """Get time-related status for the interview."""
    elapsed = _get_elapsed_minutes(session)
    duration = session.get("duration_minutes", 30)
    hard_limit = duration + MAX_OVERTIME_MINUTES
    remaining = max(0, duration - elapsed)
    overtime = max(0, elapsed - duration)
    is_overtime = elapsed > duration
    is_hard_limit = elapsed >= hard_limit

    return {
        "elapsed_minutes": elapsed,
        "scheduled_duration": duration,
        "remaining_minutes": remaining,
        "overtime_minutes": overtime,
        "is_overtime": is_overtime,
        "is_hard_limit_reached": is_hard_limit,
        "hard_limit_minutes": hard_limit,
    }


def _count_consecutive_weak_answers(session: Dict[str, Any]) -> int:
    """Count how many consecutive weak answers (score < 4) at the end."""
    evaluations = session.get("evaluations", [])
    count = 0
    for ev in reversed(evaluations):
        score = ev.get("evaluation", {}).get("score", 5)
        if score < 4:
            count += 1
        else:
            break
    return count


@router.post("/start")
def start_interview(request: StartInterviewRequest):
    profile = analyze_profile(request.resume_text, request.job_description, request.role, request.company)
    plan = create_interview_plan(profile, request.duration_minutes, request.role, request.difficulty)

    session_id = str(uuid4())
    session = {
        "session_id": session_id,
        "role": request.role,
        "company": request.company,
        "duration_minutes": request.duration_minutes,
        "difficulty": request.difficulty,
        "profile": profile,
        "plan": plan,
        "history": [],
        "evaluations": [],
        "current_question": None,
        "status": "in_progress",
        "start_time": datetime.now(timezone.utc),
        "end_reason": None,
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

    # Evaluate the answer
    evaluation = evaluate_answer(current_question, request.answer, session)
    session["evaluations"].append({
        "question": current_question,
        "answer": request.answer,
        "evaluation": evaluation,
    })

    # Get time status
    time_status = _get_time_status(session)
    consecutive_weak = _count_consecutive_weak_answers(session)

    # Decision: Should the interview end?
    should_end = False
    end_reason = None

    # Hard time limit reached — must end
    if time_status["is_hard_limit_reached"]:
        should_end = True
        end_reason = "time_limit"

    # Candidate unable to answer 4+ consecutive questions — politely end
    elif consecutive_weak >= 4:
        should_end = True
        end_reason = "candidate_struggling"

    # If interview should end, generate a closing statement instead of next question
    if should_end:
        session["end_reason"] = end_reason
        closing = _generate_closing_statement(session, end_reason)
        session["history"].append({"interviewer": closing})
        session["status"] = "ending"

        # Auto-generate report
        report = generate_final_report(session)
        session["status"] = "completed"
        session["report"] = report

        return {
            "next_question": closing,
            "turn_count": len(session["evaluations"]),
            "interview_ended": True,
            "end_reason": end_reason,
            "report": report,
            "evaluations": session.get("evaluations", []),
        }

    # Generate next question with time awareness
    next_question = generate_next_question(session, evaluation, time_status)
    session["current_question"] = next_question
    session["history"].append({"interviewer": next_question})

    return {
        "next_question": next_question,
        "turn_count": len(session["evaluations"]),
        "interview_ended": False,
        "time_status": {
            "elapsed": time_status["elapsed_minutes"],
            "remaining": time_status["remaining_minutes"],
            "is_overtime": time_status["is_overtime"],
        },
    }


def _generate_closing_statement(session: Dict[str, Any], reason: str) -> str:
    """Generate a professional closing statement."""
    from app.services.llm_client import get_llm_config, chat_text

    api_key, _ = get_llm_config()

    if not api_key:
        if reason == "candidate_struggling":
            return (
                "I appreciate you taking the time to speak with us today. "
                "I can see that some of these areas might not align with your current experience, "
                "and that's completely okay. We'll review everything internally and follow up with next steps. "
                "If you have any questions about the role or the process, feel free to reach out via email. "
                "Thank you again for your time, and I wish you the best."
            )
        return (
            "We've covered a lot of ground today, and I want to be respectful of your time. "
            "Thank you for your thoughtful answers throughout this interview. "
            "We'll review everything and follow up with you on next steps. "
            "If you have any questions about the role or anything we discussed, "
            "please don't hesitate to reach out via email. Thank you again!"
        )

    prompt = f"""
The interview is ending. Generate a professional, warm closing statement.

Role: {session['role']}
Reason for ending: {reason}
Questions asked: {len(session.get('evaluations', []))}
Duration: {session.get('duration_minutes')} minutes planned

{"The candidate struggled with multiple consecutive questions. Be kind and encouraging — do NOT say they failed or performed poorly. Simply wrap up professionally." if reason == "candidate_struggling" else "The scheduled time has been reached. Wrap up naturally."}

RULES:
- Thank the candidate for their time
- Say the team will review and follow up with next steps
- Invite them to reach out via email if they have any questions
- Keep it warm, professional, and concise (3-4 sentences max)
- Do NOT reveal scores or evaluations
- Do NOT say "you didn't do well" or anything negative
- End on a positive, encouraging note
"""
    return chat_text(
        "You are a professional interviewer wrapping up an interview gracefully.",
        prompt,
        temperature=0.4
    )


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
