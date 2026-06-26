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
        return f"""# Mock Interview Assessment Report

## Interview Summary
- **Role:** {session['role']}
- **Difficulty:** {session.get('difficulty', 'mid')}
- **Duration:** {session.get('duration_minutes', 30)} minutes
- **Questions Asked:** {len(evaluations)}
- **Overall Score:** {avg:.1f}/10

## Strengths
- You completed the mock interview flow.
- Your answers can now be evaluated question by question.

## Improvement Areas
- Add your OpenAI API key for detailed LLM-based feedback.
- Use concrete examples, commands, tradeoffs, and production stories.

## Practice Plan
1. Prepare a strong project walkthrough using the STAR format.
2. Practice role-specific troubleshooting scenarios.
3. Use STAR format for behavioral answers.
4. Review each question below and prepare better answers.

## Question-by-Question Breakdown
"""

    evaluations = session.get("evaluations", [])
    eval_summary = []
    for i, ev in enumerate(evaluations, 1):
        eval_summary.append({
            "q_number": i,
            "question": ev.get("question", "")[:200],
            "answer_preview": ev.get("answer", "")[:200],
            "score": ev.get("evaluation", {}).get("score", 0),
            "strengths": ev.get("evaluation", {}).get("strengths", []),
            "weaknesses": ev.get("evaluation", {}).get("weaknesses", []),
            "missing_points": ev.get("evaluation", {}).get("missing_points", []),
        })

    prompt = f"""
Generate a comprehensive, detailed interview assessment report that will help the candidate improve for future interviews.

INTERVIEW DETAILS:
- Role: {session['role']}
- Difficulty: {session.get('difficulty', 'mid')}
- Duration: {session.get('duration_minutes', 30)} minutes planned
- Questions asked: {len(evaluations)}
- End reason: {session.get('end_reason', 'candidate ended')}

CANDIDATE PROFILE:
{session.get('profile', {})}

INTERVIEW PLAN:
{session.get('plan', {})}

QUESTION-BY-QUESTION EVALUATIONS:
{eval_summary}

Generate a DETAILED markdown report with ALL of the following sections:

# Mock Interview Assessment Report

## 1. Interview Summary
- Role, difficulty, duration, total questions
- Overall score (average of all question scores, out of 10)
- One-paragraph executive summary of performance

## 2. Score Breakdown
- Overall Score: X/10
- Technical Accuracy: X/10
- Depth of Knowledge: X/10
- Communication & Clarity: X/10
- Problem-Solving Approach: X/10
- Role Relevance: X/10

## 3. Key Strengths (what the candidate did well)
- List 3-5 specific strengths with examples from their answers

## 4. Areas for Improvement (where the candidate was weak)
- List 3-5 specific weaknesses with what was missing

## 5. Question-by-Question Analysis
For EACH question asked:
- Question text
- Score (X/10)
- Why this question was asked (what skill/competency the interviewer was testing)
- What was good about the answer
- What was missing or could be improved
- Ideal answer (what a strong/perfect answer would sound like — specific, practical, with tools and examples)

## 6. Skills Gap Analysis
- Skills demonstrated strongly
- Skills that need improvement
- Skills not tested but required for the role

## 7. Actionable Improvement Plan
A concrete 7-day study plan with:
- Day 1-2: Focus area and resources
- Day 3-4: Focus area and resources
- Day 5-6: Focus area and resources
- Day 7: Mock practice suggestions

## 8. Recommended Practice Questions
- 5-8 practice questions the candidate should prepare for next time
- These should target their weak areas

## 9. Interview Tips
- 3-5 specific tips for how they can improve their interview technique (not just technical knowledge)

## 10. Qualification Probability Assessment
Based on the overall interview performance, provide a realistic assessment of whether this candidate would advance to the next round. Evaluate from THREE different interviewer perspectives:

**Liberal Interviewer** (focuses on potential, communication, and general fit):
- Probability of advancing: X%
- Reasoning: what this interviewer would focus on

**Moderate Interviewer** (balanced between technical depth and overall capability):
- Probability of advancing: X%
- Reasoning: what this interviewer would weigh

**Strict Interviewer** (demands precise technical answers, specific examples, and deep expertise):
- Probability of advancing: X%
- Reasoning: what would concern this interviewer

**Overall Verdict:**
- Most likely outcome (advance / borderline / reject)
- The #1 thing that would tip the decision in the candidate's favor
- The #1 risk that could cause rejection

IMPORTANT:
- Be specific and actionable, not generic
- Reference the candidate's ACTUAL answers where possible
- The goal is to help them pass the NEXT interview
- Be encouraging but honest
- Use markdown formatting properly
"""
    return chat_text(
        "You are a senior technical interview coach who provides detailed, actionable feedback to help candidates improve. Your reports are thorough, specific, and encouraging while being honest about areas needing improvement.",
        prompt,
        temperature=0.3
    )
