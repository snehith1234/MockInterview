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
3. Follow the interview plan sections in order. The current section tells you what to focus on NOW.
4. BALANCE depth and breadth using this judgment:
   - If you've asked 2+ questions on the SAME narrow skill (e.g., grep, one specific CLI tool), MOVE ON unless the topic is a PRIMARY job requirement and the candidate's answer reveals a critical gap or strength worth exploring.
   - If a topic is HIGHLY relevant to the job role (listed in competency_areas), you may ask up to 3 questions on it — but then you MUST move to the next competency area.
   - If a topic is only tangentially related to the job, move on after 1 question.
5. Do NOT cut off a productive line of questioning abruptly. If the candidate is demonstrating strong or revealing answers on a job-critical topic, finish the thread naturally with one more question, THEN transition smoothly.
6. Smooth transitions: acknowledge the previous topic briefly before moving ("Good insight on X. Let's shift to Y, since this role also requires...")
7. Cover ALL sections in the plan by the end of the interview. If you're spending too long on one section, you'll run out of time for later ones.
8. Your questions should directly relate to the competency_areas listed for the current section.
9. Validate ownership where relevant: ask "What did YOU personally do?" or "What was the business impact?"
10. Keep questions practical and role-relevant. Ask about real scenarios, not trivia or increasingly obscure sub-topics.

WHEN TO GO DEEPER (allow 3 questions on same topic):
- The skill is explicitly listed as a primary job requirement
- The candidate's answer reveals a potential gap that's critical for the role
- The candidate claims strong experience but hasn't proven it with specifics yet

WHEN TO MOVE ON (max 1-2 questions):
- The topic is only loosely related to the core job requirements
- The candidate has already demonstrated clear competence in this area
- You're drilling into sub-details of a sub-detail (e.g., regex syntax within log analysis within Linux troubleshooting)
- The candidate has given a weak answer and one clarification didn't help — note it and move on

TOPIC TRANSITION EXAMPLES:
- After 2-3 questions on Linux troubleshooting → transition to Windows/IIS, or AWS, or CI/CD
- After establishing CI/CD knowledge → move to scripting, monitoring, or architecture
- After infrastructure questions → move to communication, developer support, or incident management
- If candidate shows clear strength in one area → acknowledge it and move to test their weaker areas

Ask your next question:
"""
    return chat_text(
        "You are a professional technical interviewer. You conduct balanced, structured interviews that cover all required competencies. You use good judgment about when to go deeper on a critical topic versus when to move on. You never spend excessive time on tangential sub-topics, but you also don't cut off important lines of inquiry prematurely. You transition smoothly between topics.",
        prompt,
        temperature=0.45
    )
