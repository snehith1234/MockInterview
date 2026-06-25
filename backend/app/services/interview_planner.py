from typing import Dict, Any
from app.services.llm_client import chat_json, get_llm_config


def create_interview_plan(profile: Dict[str, Any], duration_minutes: int, role: str, difficulty: str = "mid") -> Dict[str, Any]:
    if duration_minutes not in (30, 60):
        duration_minutes = 30

    api_key, _ = get_llm_config()
    if not api_key:
        sections = [
            {"name": "Introduction", "time_minutes": 3 if duration_minutes == 30 else 5, "goal": "Warm-up and background", "sample_questions": ["Can you briefly introduce yourself and your recent work?"]},
            {"name": "Resume Deep Dive", "time_minutes": 7 if duration_minutes == 30 else 10, "goal": "Validate resume experience", "sample_questions": ["Walk me through one relevant project from your resume."]},
            {"name": "Technical Core", "time_minutes": 10 if duration_minutes == 30 else 20, "goal": "Assess core technical depth", "sample_questions": ["Explain a key concept required for this role."]},
            {"name": "Scenario/System Design", "time_minutes": 7 if duration_minutes == 30 else 15, "goal": "Assess practical problem solving", "sample_questions": ["How would you troubleshoot a production issue in this role?"]},
            {"name": "Behavioral + Wrap-up", "time_minutes": 3 if duration_minutes == 30 else 10, "goal": "Assess communication and ownership", "sample_questions": ["Tell me about a difficult technical problem you handled."]},
        ]
        return {"duration_minutes": duration_minutes, "difficulty": difficulty, "sections": sections}

    prompt = f"""
Create a realistic {duration_minutes}-minute interview plan.

Role: {role}
Difficulty: {difficulty}
Candidate Profile: {profile}

Rules:
- Time allocation must add up exactly to {duration_minutes}.
- Include introduction, resume deep dive, technical core, scenario/system design, behavioral, and wrap-up.
- Each section needs name, time_minutes, goal, and sample_questions.

Return JSON:
{{"duration_minutes": {duration_minutes}, "difficulty": "{difficulty}", "sections": []}}
"""
    return chat_json("You are a senior technical interviewer and interview designer.", prompt, temperature=0.25)
