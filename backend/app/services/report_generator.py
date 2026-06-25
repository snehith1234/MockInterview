from typing import Dict, Any
from app.services.llm_client import chat_text, get_llm_config


def generate_final_report(session: Dict[str, Any]) -> str:
    api_key, _ = get_llm_config()
    if not api_key:
        evaluations = session.get("evaluations", [])
        if evaluations:
            avg = sum(e["evaluation"].get("score", 0) for e in evaluations) / len(evaluations)
        else:
            avg = 0
        return f"""# Mock Interview Report\n\nRole: {session['role']}\nOverall Score: {avg:.1f}/10\n\n## Strengths\n- You completed the mock interview flow.\n- Your answers can now be evaluated question by question.\n\n## Improvement Areas\n- Add OPENAI_API_KEY in backend/.env for detailed LLM-based feedback.\n- Use concrete examples, commands, tradeoffs, and production stories.\n\n## Practice Plan\n1. Prepare a strong project walkthrough.\n2. Practice role-specific troubleshooting scenarios.\n3. Use STAR format for behavioral answers.\n"""

    prompt = f"""
Generate a final interview report.

Session:
{session}

Return markdown with:
- Overall score
- Technical score
- Communication score
- Problem-solving score
- Strengths
- Weaknesses
- Missed concepts
- Role readiness
- 7-day improvement plan
- Recommended practice questions
"""
    return chat_text("You are a senior technical interview coach.", prompt, temperature=0.3)
