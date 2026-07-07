"""
JobHunter Setup Wizard
Run once: python3 setup.py
"""

import json
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

sys.path.insert(0, str(Path(__file__).parent))
import config as cfg
from core.resume_parser import parse_resume, extract_skills

console = Console()


def run():
    console.print(Panel.fit(
        "[bold cyan]JobHunter — First Time Setup[/bold cyan]\n"
        "[dim]Press Enter to skip any optional field.[/dim]",
        border_style="cyan"
    ))

    console.print("\n[bold]── Personal Details ──[/bold]")
    cfg.PROFILE["name"]           = Prompt.ask("Full name")
    cfg.PROFILE["email"]          = Prompt.ask("Email")
    cfg.PROFILE["phone"]          = Prompt.ask("Phone (with country code)")
    cfg.PROFILE["location"]       = Prompt.ask("Location", default=cfg.PROFILE["location"])
    cfg.PROFILE["linkedin_url"]   = Prompt.ask("LinkedIn URL [optional]", default="")
    cfg.PROFILE["github_url"]     = Prompt.ask("GitHub URL [optional]", default="")
    cfg.PROFILE["portfolio_url"]  = Prompt.ask("Portfolio URL [optional]", default="")

    console.print("\n[bold]── Experience ──[/bold]")
    cfg.PROFILE["current_title"]    = Prompt.ask("Current title", default=cfg.PROFILE["current_title"])
    cfg.PROFILE["years_experience"] = float(Prompt.ask("Years of experience", default=str(cfg.PROFILE["years_experience"])))
    cfg.PROFILE["notice_period"]    = Prompt.ask("Notice period", default=cfg.PROFILE["notice_period"])
    cfg.PROFILE["expected_salary"]  = Prompt.ask("Expected salary (e.g. 18-22 LPA) [optional]", default="")

    console.print("\n[bold]── Resume ──[/bold]")
    while True:
        resume_path = Prompt.ask("Full path to your resume (PDF or DOCX)")
        if Path(resume_path).exists():
            cfg.PROFILE["resume_path"] = resume_path
            try:
                text = parse_resume(resume_path)
                found_skills = extract_skills(text, cfg.PROFILE["skills"])
                console.print(f"[green]✓ Resume parsed — {len(text)} characters[/green]")
                if found_skills:
                    console.print(f"[green]✓ Skills detected: {', '.join(found_skills)}[/green]")
                (Path(cfg.DATA_DIR) / "resume_text.txt").write_text(text)
                console.print(f"[dim]Resume text saved to data/resume_text.txt[/dim]")
            except Exception as e:
                console.print(f"[yellow]⚠ Could not parse resume: {e}[/yellow]")
            break
        else:
            console.print("[red]File not found — try again.[/red]")

    console.print("\n[bold]── Professional Summary ──[/bold]")
    console.print("[dim]2-3 sentences about your background (used in cover letters).[/dim]")
    cfg.PROFILE["summary"] = Prompt.ask("Summary [optional]", default="")

    console.print("\n[bold]── Certifications ──[/bold]")
    console.print("[dim]Paste all certifications as a comma-separated list, e.g: CEH, OSCP, Security+[/dim]")
    certs_input = Prompt.ask("Certifications [optional]", default="")
    if certs_input.strip():
        # Split by comma or newline, clean up bullet points and whitespace
        import re
        raw = re.split(r'[,\n]', certs_input)
        certs = [re.sub(r'^[\s•\-\*]+', '', c).strip() for c in raw if c.strip()]
        cfg.PROFILE["certifications"] = certs
        console.print(f"[green]✓ {len(certs)} certifications saved[/green]")
        for c in certs:
            console.print(f"  [dim]• {c}[/dim]")

    # Save profile to data/profile.json
    profile_path = Path(cfg.DATA_DIR) / "profile.json"
    with open(profile_path, "w") as f:
        json.dump(cfg.PROFILE, f, indent=2)

    console.print(Panel.fit(
        f"[bold green]✓ Setup complete![/bold green]\n"
        f"[dim]Profile saved to {profile_path}[/dim]\n\n"
        f"Next: [bold cyan]python3 main.py[/bold cyan]",
        border_style="green"
    ))


if __name__ == "__main__":
    run()
