import json
import logging
from groq import AsyncGroq
from app.core.config import settings
from app.models.resume import AIAnalysis, SkillMatch

logger = logging.getLogger(__name__)

_client: AsyncGroq | None = None


def get_groq_client() -> AsyncGroq:
    global _client
    if _client is None:
        _client = AsyncGroq(api_key=settings.GROQ_API_KEY)
    return _client


ANALYSIS_SYSTEM_PROMPT = """You are an expert technical recruiter and resume analyst with 15+ years of experience.
Your task is to analyze a candidate's resume against a job description and provide a structured, objective assessment.

Always respond with ONLY valid JSON matching the exact schema provided. No markdown, no explanation outside the JSON."""

ANALYSIS_USER_PROMPT = """Analyze this resume against the job description and return a JSON object with EXACTLY this structure:

{{
  "overall_score": <float 0-100>,
  "skill_match_score": <float 0-100>,
  "experience_score": <float 0-100>,
  "education_score": <float 0-100>,
  "communication_score": <float 0-100>,
  "matched_skills": [
    {{"skill": "<name>", "matched": true, "proficiency": "<beginner|intermediate|expert>"}}
  ],
  "missing_skills": ["<skill>"],
  "bonus_skills": ["<skill>"],
  "strengths": ["<strength statement>"],
  "weaknesses": ["<weakness statement>"],
  "recommendation": "<hire|maybe|reject>",
  "recommendation_reason": "<2-3 sentence explanation>",
  "interview_questions": ["<question>"],
  "red_flags": ["<flag>"],
  "employment_gaps": <true|false>
}}

--- JOB DESCRIPTION ---
Title: {job_title}
Required Skills: {required_skills}
Preferred Skills: {preferred_skills}
Min Experience: {min_exp} years
Description: {job_description}

--- RESUME TEXT ---
{resume_text}

Scoring guide:
- overall_score = weighted average (skills 40%, experience 35%, education 15%, communication 10%)
- skill_match_score = % of required_skills matched, boosted by proficiency level
- Generate 5 targeted interview_questions based on gaps and the role
- Only flag red_flags for genuinely concerning patterns (not just missing preferred skills)
- employment_gaps = true only if unexplained gaps > 6 months exist"""


EXTRACTION_SYSTEM_PROMPT = """You are a precise resume parser. Extract structured information from resume text.
Respond ONLY with valid JSON."""

EXTRACTION_USER_PROMPT = """Extract the following from this resume text and return ONLY valid JSON:

{{
  "first_name": "<string>",
  "last_name": "<string>",
  "email": "<string or null>",
  "phone": "<string or null>",
  "location": "<string or null>",
  "linkedin_url": "<string or null>",
  "portfolio_url": "<string or null>",
  "current_title": "<string or null>",
  "years_of_experience": <float or null>,
  "summary": "<string or null>",
  "skills": ["<skill>"],
  "languages": ["<language>"],
  "experience": [
    {{
      "company": "<string>",
      "title": "<string>",
      "start_date": "<string or null>",
      "end_date": "<string or null>",
      "description": "<string or null>",
      "location": "<string or null>"
    }}
  ],
  "education": [
    {{
      "institution": "<string>",
      "degree": "<string>",
      "field": "<string or null>",
      "graduation_year": <int or null>,
      "gpa": <float or null>
    }}
  ]
}}

--- RESUME TEXT ---
{resume_text}"""


async def analyze_resume(
    resume_text: str,
    job_title: str,
    job_description: str,
    required_skills: list[str],
    preferred_skills: list[str],
    min_experience: float | None,
) -> AIAnalysis:
    """Send resume + JD to GroqCloud and parse structured analysis."""
    client = get_groq_client()

    prompt = ANALYSIS_USER_PROMPT.format(
        job_title=job_title,
        required_skills=", ".join(required_skills),
        preferred_skills=", ".join(preferred_skills),
        min_exp=min_experience or "Not specified",
        job_description=job_description[:3000],  # trim for token limit
        resume_text=resume_text[:4000],
    )

    try:
        response = await client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_tokens=settings.GROQ_MAX_TOKENS,
            temperature=0.1,  # low temp for consistent structured output
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content
        data = json.loads(raw)

        # Build AIAnalysis from the response
        analysis = AIAnalysis(
            overall_score=float(data.get("overall_score", 0)),
            skill_match_score=float(data.get("skill_match_score", 0)),
            experience_score=float(data.get("experience_score", 0)),
            education_score=float(data.get("education_score", 0)),
            communication_score=float(data.get("communication_score", 0)),
            matched_skills=[
                SkillMatch(**s) for s in data.get("matched_skills", [])
            ],
            missing_skills=data.get("missing_skills", []),
            bonus_skills=data.get("bonus_skills", []),
            strengths=data.get("strengths", []),
            weaknesses=data.get("weaknesses", []),
            recommendation=data.get("recommendation", "maybe"),
            recommendation_reason=data.get("recommendation_reason", ""),
            interview_questions=data.get("interview_questions", []),
            red_flags=data.get("red_flags", []),
            employment_gaps=data.get("employment_gaps", False),
        )
        return analysis

    except json.JSONDecodeError as e:
        logger.error(f"Groq returned invalid JSON: {e}")
        raise ValueError("AI service returned malformed response") from e
    except Exception as e:
        logger.error(f"Groq analysis failed: {e}")
        raise


async def extract_candidate_info(resume_text: str) -> dict:
    """Auto-extract candidate fields from raw resume text."""
    client = get_groq_client()

    prompt = EXTRACTION_USER_PROMPT.format(resume_text=resume_text[:5000])

    response = await client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        max_tokens=2048,
        temperature=0.0,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content
    return json.loads(raw)


async def generate_screening_email(
    candidate_name: str,
    job_title: str,
    recommendation: str,
) -> str:
    """Generate a professional screening outcome email."""
    client = get_groq_client()

    tone_map = {
        "hire": "warm and enthusiastic, inviting them to the next round",
        "maybe": "professional and encouraging, requesting additional information",
        "reject": "respectful and empathetic, thanking them for their time",
    }

    response = await client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Write a {tone_map.get(recommendation, 'professional')} recruitment email "
                    f"to {candidate_name} regarding their application for {job_title}. "
                    "Keep it under 150 words. Return only the email body text."
                ),
            }
        ],
        max_tokens=300,
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()
