from typing import Dict, Any
from app.services.llm_client import chat_json, get_llm_config


def evaluate_answer(question: str, answer: str, session: Dict[str, Any]) -> Dict[str, Any]:
    api_key, _ = get_llm_config()
    if not api_key:
        score = 6 if len(answer.split()) < 30 else 8
        return {
            "score": score,
            "technical_accuracy": score,
            "depth": max(score - 1, 1),
            "communication": min(score + 1, 10),
            "problem_solving": score,
            "strengths": ["Provided a relevant answer"],
            "weaknesses": ["Use a real LLM key for detailed scoring"],
            "missing_points": ["Specific commands/examples", "Tradeoffs", "Failure handling"],
            "ideal_answer_outline": ["State approach", "Give concrete steps", "Mention tradeoffs", "Conclude with validation"],
            "recommended_follow_up": "Can you give a concrete real-world example?",
            "recommended_next_action": "ask_deeper_followup" if score >= 8 else "ask_clarifying_followup"
        }

    prompt = f"""
Evaluate this interview answer.

Role: {session['role']}
Candidate profile: {session['profile']}
Interview plan: {session['plan']}
Questions asked so far in this interview: {len(session.get('evaluations', [])) + 1}

Question:
{question}

Candidate answer:
{answer}

Score from 1 to 10 using:
- technical_accuracy
- depth
- communication
- problem_solving
- role_relevance

IMPORTANT for recommended_next_action:
- If this is the 3rd+ question on the same narrow topic, ALWAYS recommend "move_to_next_topic"
- If the answer was strong (7+) and this topic is well-covered, recommend "move_to_next_topic"
- If the answer was strong (7+) but revealed a critical gap on a PRIMARY job requirement, recommend "ask_deeper_followup"
- If the answer was weak (< 5) and this is a critical job requirement, recommend "ask_clarifying_followup" for ONE more attempt
- If the answer was weak (< 5) on a secondary topic, recommend "move_to_next_topic"
- Only recommend "ask_deeper_followup" if the topic is a primary job requirement AND the answer warrants deeper exploration

Return JSON with:
score, technical_accuracy, depth, communication, problem_solving, role_relevance,
strengths, weaknesses, missing_points, ideal_answer_outline,
recommended_follow_up, recommended_next_action.

recommended_next_action must be one of:
- ask_deeper_followup
- ask_clarifying_followup
- move_to_next_topic
- simplify_question
"""
    return chat_json("You are a strict but helpful technical interview evaluator.", prompt, temperature=0.2)
