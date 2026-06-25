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

IMPORTANT: Extract ALL specific technical skills, tools, platforms, and competency areas mentioned in the job description. These will be used to build the interview plan and ensure complete coverage.

Return JSON with exactly these keys:
- candidate_level (string: junior/mid/senior assessment)
- primary_skills (list: candidate's strongest skills from resume)
- secondary_skills (list: candidate's secondary skills)
- job_required_skills (list: ALL skills/tools/platforms explicitly mentioned in the job description)
- job_required_competencies (list: broader competency areas the JD requires, e.g. "Windows/IIS administration", "CI/CD pipeline management", "Cloud infrastructure", "Scripting/automation", "Incident management", "Developer support")
- matching_skills (list: skills the candidate has that match the JD)
- missing_or_weak_skills (list: JD requirements the candidate may lack or hasn't demonstrated)
- interview_focus_areas (list: the most important areas to test, prioritizing gaps and critical JD requirements)
- resume_based_question_topics (list: specific resume claims that should be validated)
- must_test_competencies (list: the top 6-8 distinct competency areas that MUST each get at least one question)
"""
    return chat_json(
        "You are a senior technical recruiting analyst.",
        prompt,
        temperature=0.2,
    )
