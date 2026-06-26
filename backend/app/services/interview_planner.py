from typing import Dict, Any
from app.services.llm_client import chat_json, get_llm_config


def create_interview_plan(profile: Dict[str, Any], duration_minutes: int, role: str, difficulty: str = "mid") -> Dict[str, Any]:
    if duration_minutes not in (30, 60):
        duration_minutes = 30

    api_key, _ = get_llm_config()
    if not api_key:
        sections = [
            {"name": "Introduction", "time_minutes": 3 if duration_minutes == 30 else 5, "goal": "Warm-up and background", "max_questions": 2, "sample_questions": ["Can you briefly introduce yourself and your recent work?"]},
            {"name": "Resume Deep Dive", "time_minutes": 7 if duration_minutes == 30 else 10, "goal": "Validate resume experience", "max_questions": 3, "sample_questions": ["Walk me through one relevant project from your resume."]},
            {"name": "Technical Core", "time_minutes": 10 if duration_minutes == 30 else 20, "goal": "Assess core technical depth", "max_questions": 4, "sample_questions": ["Explain a key concept required for this role."]},
            {"name": "Scenario/System Design", "time_minutes": 7 if duration_minutes == 30 else 15, "goal": "Assess practical problem solving", "max_questions": 3, "sample_questions": ["How would you troubleshoot a production issue in this role?"]},
            {"name": "Behavioral + Wrap-up", "time_minutes": 3 if duration_minutes == 30 else 10, "goal": "Assess communication and ownership", "max_questions": 2, "sample_questions": ["Tell me about a difficult technical problem you handled."]},
        ]
        return {"duration_minutes": duration_minutes, "difficulty": difficulty, "sections": sections}

    prompt = f"""
Create a realistic {duration_minutes}-minute interview plan for this role.

Role: {role}
Difficulty: {difficulty}
Candidate Profile: {profile}

CRITICAL RULES:
1. Time allocation must add up exactly to {duration_minutes}.
2. You MUST create sections that cover ALL major skill areas mentioned in the job description/role requirements.
3. Each section should focus on a DIFFERENT competency area. Do NOT allow one topic to dominate.
4. Include max_questions per section to enforce time limits (typically 2-4 questions per section depending on time).
5. For a 30-minute interview, aim for 5-6 sections. For 60 minutes, aim for 7-9 sections.
6. Each section needs: name, time_minutes, goal, max_questions, competency_areas (list of skills tested), and sample_questions.
7. Sections should cover diverse areas like: core technical skills, platform/tools, troubleshooting, architecture/design, automation/scripting, collaboration/communication.
8. Do NOT create multiple sections on the same narrow topic (e.g., don't have both "Linux Troubleshooting" and "Log Analysis" as separate sections).
9. QUESTION DIFFICULTY DISTRIBUTION: Across all sections combined, enforce this ratio:
   - 20% Easy questions (warm-up, basic concepts, resume walkthrough)
   - 70% Medium questions (practical scenarios, tool usage, troubleshooting, project-based)
   - 10% Hard questions (deep architecture, complex scenarios, edge cases, system design)
   Mark each sample_question with its difficulty level: "easy", "medium", or "hard".
10. The difficulty distribution should be applied naturally — easy questions at the start, hard questions toward the middle/end.

Return JSON:
{{"duration_minutes": {duration_minutes}, "difficulty": "{difficulty}", "sections": [
  {{"name": "...", "time_minutes": N, "goal": "...", "max_questions": N, "competency_areas": ["skill1", "skill2"], "sample_questions": ["..."]}}
]}}
"""
    return chat_json("You are a senior technical interviewer and interview designer. You design balanced interviews that assess ALL required competencies, not just one or two.", prompt, temperature=0.25)
