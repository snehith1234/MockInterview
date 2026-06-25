from typing import Dict, Any, Optional
from app.services.llm_client import chat_text, get_llm_config


def _get_current_section(session: Dict[str, Any]) -> Dict[str, Any]:
    """Determine which section the interview should be in based on question count."""
    plan = session.get("plan", {})
    sections = plan.get("sections", [])
    questions_asked = len(session.get("evaluations", []))

    cumulative = 0
    for section in sections:
        max_q = section.get("max_questions", 3)
        cumulative += max_q
        if questions_asked < cumulative:
            return section

    # If we've exhausted all sections, return the last one
    return sections[-1] if sections else {}


def _get_covered_topics(session: Dict[str, Any]) -> str:
    """Build a summary of topics already covered to avoid repetition."""
    evaluations = session.get("evaluations", [])
    if not evaluations:
        return "No topics covered yet."

    topics = []
    for ev in evaluations:
        q = ev.get("question", "")
        if q:
            topics.append(f"- {q[:100]}")
    return "\n".join(topics[-8:])  # Last 8 questions for context


def generate_first_question(session: Dict[str, Any]) -> str:
    api_key, _ = get_llm_config()
    if not api_key:
        return f"Thanks for joining. Let's begin this {session['duration_minutes']}-minute mock interview for the {session['role']} role. Can you briefly introduce yourself and walk me through your most relevant recent project?"

    plan = session.get("plan", {})
    sections = plan.get("sections", [])
    section_names = [s.get("name", "") for s in sections]

    prompt = f"""
Conduct a real mock interview.

Role: {session['role']}
Candidate profile: {session['profile']}
Interview plan sections: {section_names}
First section: {sections[0] if sections else 'Introduction'}

RULES:
- Start professionally with exactly ONE opening question.
- The opening should be warm but efficient — ask the candidate to introduce themselves and connect their experience to this specific role.
- Do NOT reveal the full interview plan.
- Do NOT reveal scoring.
- Keep it concise and natural.
"""
    return chat_text("You are a professional technical interviewer conducting a structured interview. You ask one question at a time.", prompt, temperature=0.4)


def generate_next_question(session: Dict[str, Any], last_evaluation: Optional[Dict[str, Any]] = None) -> str:
    api_key, _ = get_llm_config()
    if not api_key:
        action = (last_evaluation or {}).get("recommended_next_action", "move_to_next_topic")
        if action == "ask_deeper_followup":
            return "Good. Let's go deeper. What tradeoffs or failure cases would you consider in that approach?"
        if action == "simplify_question":
            return "Let's simplify it. Can you explain the basic concept first, then give one example?"
        return "Can you give a concrete example from your experience and explain what you personally did?"

    current_section = _get_current_section(session)
    covered_topics = _get_covered_topics(session)
    questions_asked = len(session.get("evaluations", []))
    plan = session.get("plan", {})
    sections = plan.get("sections", [])
    total_max_questions = sum(s.get("max_questions", 3) for s in sections)

    # Determine if we should move to next topic
    recommended_action = (last_evaluation or {}).get("recommended_next_action", "move_to_next_topic")

    prompt = f"""
You are in the middle of a structured mock interview.

Role: {session['role']}
Candidate profile: {session['profile']}

FULL INTERVIEW PLAN (you must cover ALL sections):
{sections}

CURRENT SECTION: {current_section.get('name', 'Unknown')}
Current section goal: {current_section.get('goal', '')}
Competency areas to test in this section: {current_section.get('competency_areas', [])}

Questions asked so far: {questions_asked} / ~{total_max_questions} total planned
Last evaluation recommendation: {recommended_action}

QUESTIONS ALREADY ASKED (do NOT repeat these topics):
{covered_topics}

Recent conversation (last 6 exchanges):
{session['history'][-12:]}

CRITICAL RULES:
1. Ask exactly ONE question.
2. Do NOT reveal score or feedback.
3. Do NOT stay on the same narrow topic for more than 2 consecutive questions. If you've already asked 2 questions on one skill, MOVE ON to a different competency area.
4. Follow the interview plan sections in order. The current section tells you what to focus on NOW.
5. If the last answer was strong (score >= 7), ask ONE brief follow-up then MOVE to the next topic/section.
6. If the last answer was weak (score < 5), ask ONE simpler clarification then MOVE to the next topic/section.
7. Cover BREADTH over DEPTH. It is better to test 8 different skills at moderate depth than to test 2 skills very deeply.
8. Your questions should directly relate to the competency_areas listed for the current section.
9. Do NOT ask increasingly specific sub-questions about the same tool or command. Move to a DIFFERENT skill area.
10. Keep questions practical and role-relevant. Ask about real scenarios, not trivia.
11. Validate ownership: ask "What did YOU personally do?" and "What was the impact?"

TOPIC TRANSITION EXAMPLES:
- After Linux troubleshooting → move to Windows/IIS, or AWS, or CI/CD
- After one CI/CD question → move to scripting, or monitoring, or architecture
- After infrastructure → move to communication, developer support, or incident management

Ask your next question:
"""
    return chat_text(
        "You are a professional technical interviewer. You conduct balanced, structured interviews that assess ALL required competencies. You NEVER spend more than 2-3 questions on one narrow topic. You smoothly transition between different skill areas.",
        prompt,
        temperature=0.45
    )
