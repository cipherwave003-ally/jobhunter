"""
Resume Parser — extracts text from PDF or DOCX.
"""

import re
from pathlib import Path


def parse_resume(path: str) -> str:
    """Return plain text from a PDF or DOCX resume."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")

    suffix = p.suffix.lower()
    if suffix == ".pdf":
        return _parse_pdf(p)
    elif suffix in (".docx", ".doc"):
        return _parse_docx(p)
    else:
        raise ValueError(f"Unsupported format: {suffix}. Use PDF or DOCX.")


def _parse_pdf(path: Path) -> str:
    from pdfminer.high_level import extract_text
    text = extract_text(str(path))
    return _clean(text)


def _parse_docx(path: Path) -> str:
    from docx import Document
    doc = Document(str(path))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return _clean("\n".join(paragraphs))


def _clean(text: str) -> str:
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()


def extract_skills(resume_text: str, known_skills: list) -> list:
    """Cross-check resume text against a skills list."""
    found = []
    lower = resume_text.lower()
    for skill in known_skills:
        if skill.lower() in lower:
            found.append(skill)
    return found


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 resume_parser.py <path/to/resume.pdf>")
        sys.exit(1)
    text = parse_resume(sys.argv[1])
    print(text[:2000])
    print(f"\n--- {len(text)} characters extracted ---")
