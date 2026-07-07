# JobHunter
Automated cybersecurity job search tool — scrapes, scores, and applies so you don't have to.

Built in Python. Runs from your terminal. You approve or skip each job, everything else is automated.

---

## What it does

1. Scrapes 5 job platforms every morning at 9AM
2. Scores each job 0-100 against your profile (skills, experience, location)
3. Shows a desktop popup — you click Approve or Skip per job
4. Auto-fills your personalised cover letter for each application
5. Tracks everything — applied, replied, interviews, offers

---

## Platforms supported

| Source | Method | Focus |
|---|---|---|
| RemoteOK | Public API | Remote roles |
| LinkedIn | RSS feed | India + Remote |
| WeWorkRemotely | RSS feed | Remote roles |
| infosec-jobs.com | HTML scrape | Cybersec-specific |
| Hive Pro | Playwright | Cybersec company |

---

## Quickstart

### 1. Clone the repo
    git clone https://github.com/cipherwave003-ally/jobhunter.git
    cd jobhunter

### 2. Install dependencies
    pip3 install -r requirements.txt
    playwright install chromium

### 3. Set up credentials
    cp .env.example .env
    # Edit .env and fill in your values

### 4. First-time setup
    python3 setup.py

### 5. Run your first scan
    python3 scheduler.py --now

### 6. Daily auto-run at 9AM IST
    python3 scheduler.py

### 7. Check your pipeline
    python3 dashboard.py

---

## Cover letter templating

In setup.py, paste your base cover letter and use these placeholders:
- {{company}} — replaced with the company name per job
- {{job_title}} — replaced with the job title per job
- {{company_line}} — auto-generates a personalised closing line

---

## Upgrade to AI matching

Set your Anthropic API key in .env:
    ANTHROPIC_API_KEY="sk-ant-..."

Then in core/matcher.py and core/cover_letter.py, set:
    AI_MODE = True

Costs approx $0.15/day for 50 jobs scored + 15 cover letters generated.

---

## Update application status

When you hear back:
    python3 dashboard.py --update <job_url> interview
    # Status options: replied | interview | offer | rejected

---

## Security

- Credentials stored in .env — never committed to git
- .env and data/ are in .gitignore
- No data sent externally except directly to job sites
- Resume and profile stored locally in data/ only

---

## Project structure

    jobhunter/
    scheduler.py          - Entry point
    dashboard.py          - Terminal stats
    setup.py              - First-time wizard
    config.py             - Keywords and preferences
    requirements.txt
    .env.example
    scrapers/
        runner.py         - Runs all scrapers
        linkedin.py
        remoteok.py
        infosec_jobs.py
        weworkremotely.py
        hivepro.py
    core/
        matcher.py        - Job scoring
        cover_letter.py   - Letter generator
        tracker.py        - Application tracking
        resume_parser.py  - PDF/DOCX parser
    ui/
        popup.py          - Desktop approval window

---

## Roadmap

- Auto-apply for Greenhouse/Lever ATS portals
- History tab in approval popup
- Naukri scraper (currently blocked by bot detection)
- Follow-up email drafter
- Browser extension version

---

Built with Python, Playwright, BeautifulSoup, APScheduler, Tkinter, Rich
