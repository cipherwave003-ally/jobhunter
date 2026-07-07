"""
Cover Letter Generator
Uses your base cover letter from data/profile.json, personalised per job.
Run setup.py first to save your cover letter.
"""

import json
from pathlib import Path

AI_MODE = False  # Set True after adding ANTHROPIC_API_KEY to .env

PROFILE_PATH = Path(__file__).parent.parent / "data" / "profile.json"


def _load_profile() -> dict:
    if PROFILE_PATH.exists():
        return json.loads(PROFILE_PATH.read_text())
    return {}


def _company_line(company: str, job_title: str) -> str:
    company = (company or "").strip()
    if company and company.lower() not in ["see listing", ""]:
        return f"The {job_title} role at {company} stood out as exactly that kind of opportunity."
    return f"This {job_title} role stood out given the strong alignment with my background."


def generate(job: dict) -> str:
    if AI_MODE:
        return _generate_ai(job)
    return _generate_offline(job)


def _generate_offline(job: dict) -> str:
    profile   = _load_profile()
    base      = profile.get("cover_letter_base", "")
    name      = profile.get("name", "")
    email     = profile.get("email", "")
    phone     = profile.get("phone", "")
    company   = job.get("company", "") or ""
    job_title = job.get("title", "this role")

    if not base:
        return (
            f"Dear Hiring Manager,\n\n"
            f"I am writing to express my interest in the {job_title} position"
            f"{chr(32) + chr(97) + chr(116) + chr(32) + company if company else ''}.\n\n"
            f"Please find my resume attached for your consideration.\n\n"
            f"Best Regards,\n{name}\n{email}\n{phone}"
        )

    letter = base.replace("{{company}}", company or "your organisation")
    letter = letter.replace("{{job_title}}", job_title)
    letter = letter.replace("{{company_line}}", _company_line(company, job_title))
    return letter


def _generate_ai(job: dict) -> str:
    try:
        import anthropic, os
        env = Path(__file__).parent.parent / ".env"
        if env.exists():
            for line in env.read_text().splitlines():
                if "ANTHROPIC_API_KEY" in line:
                    _, v = line.split("=", 1)
                    os.environ.setdefault("ANTHROPIC_API_KEY", v.strip().strip(chr(34)))

        profile = _load_profile()
        client  = anthropic.Anthropic()
        prompt  = f"""Tailor this cover letter for the job below.
Keep the same voice and structure. Only personalise the closing paragraph
to reference the specific company and role. Return the full letter only.

Base letter:
{profile.get("cover_letter_base", "")}

Job: {job.get("title")} at {job.get("company", "the company")}
Key requirements: {job.get("description", "")[:800]}"""

        resp = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.content[0].text.strip()

    except Exception as e:
        print(f"  AI cover letter failed, using base: {e}")
        return _generate_offline(job)


def batch_generate(jobs: list) -> list:
    print(f"  Generating {len(jobs)} cover letters...")
    for job in jobs:
        job["cover_letter"] = generate(job)
    return jobs
