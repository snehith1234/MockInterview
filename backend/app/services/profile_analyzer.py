from typing import Dict, Any
from app.services.llm_client import chat_json, get_llm_config


def analyze_profile(resume_text: str, job_description: str, role: str) -> Dict[str, Any]:
    api_key, _ = get_llm_config()
    if not api_key:
        return {
            "candidate_level": "Mid/Senior candidate",
            "primary_skills": ["Python", "Cloud", "APIs", "System Design"],
            "secondary_skills": ["Databases", "Linux", "Troubleshooting"],
            "job_required_skills": ["Role-specific fundamentals", "Hands-on project experience", "Problem solving"],
            "matching_skills": ["Relevant project experience", "Technical fundamentals"],
            "missing_or_weak_skills": ["Add OPENAI_API_KEY for real resume/JD analysis"],
            "interview_focus_areas": ["Resume deep dive", "Core technical depth", "Scenario troubleshooting", "Behavioral examples"],
            "resume_based_question_topics": ["Most recent project", "Technical decisions", "Production challenges"]
        }

    prompt = f"""
Analyze this candidate for a mock interview.

Role: {role}

Resume:
{resume_text[:12000]}

Job Description:
{job_description[:8000]}

Return JSON with exactly these keys:
- candidate_level
- primary_skills
- secondary_skills
- job_required_skills
- matching_skills
- missing_or_weak_skills
- interview_focus_areas
- resume_based_question_topics
"""
    return chat_json(
        "You are a senior technical recruiting analyst.",
        prompt,
        temperature=0.2,
    )
