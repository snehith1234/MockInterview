from typing import Dict, Any, Optional
from app.services.llm_client import chat_text, get_llm_config


def generate_first_question(session: Dict[str, Any]) -> str:
    api_key, _ = get_llm_config()
    if not api_key:
        return f"Thanks for joining. Let's begin this {session['duration_minutes']}-minute mock interview for the {session['role']} role. Can you briefly introduce yourself and walk me through your most relevant recent project?"

    prompt = f"""
Conduct a real mock interview.

Role: {session['role']}
Candidate profile: {session['profile']}
Interview plan: {session['plan']}

Start professionally. Ask exactly one first question.
Do not reveal scoring. Do not explain the full plan.
"""
    return chat_text("You are a professional technical interviewer. Ask one question at a time.", prompt, temperature=0.4)


def generate_next_question(session: Dict[str, Any], last_evaluation: Optional[Dict[str, Any]] = None) -> str:
    api_key, _ = get_llm_config()
    if not api_key:
        action = (last_evaluation or {}).get("recommended_next_action", "move_to_next_topic")
        if action == "ask_deeper_followup":
            return "Good. Let’s go deeper. What tradeoffs or failure cases would you consider in that approach?"
        if action == "simplify_question":
            return "Let’s simplify it. Can you explain the basic concept first, then give one example?"
        return "Can you give a concrete example from your experience and explain what you personally did?"

    prompt = f"""
You are in the middle of a mock interview.

Role: {session['role']}
Candidate profile: {session['profile']}
Interview plan: {session['plan']}
Conversation history: {session['history'][-10:]}
Last evaluation: {last_evaluation}

Rules:
- Ask exactly one question.
- Do not reveal score or feedback yet.
- If answer was strong, ask a deeper follow-up.
- If answer was weak, ask a simpler clarification.
- If topic has enough depth, move to next planned section.
- Keep it realistic and professional.
"""
    return chat_text("You are a professional technical interviewer. Ask one question at a time.", prompt, temperature=0.45)
