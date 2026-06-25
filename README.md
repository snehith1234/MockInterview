# Mock Interview Agent MVP

This is a runnable MVP scaffold for a resume-aware, job-description-aware mock interview agent.

It supports:

- Resume PDF upload and parsing
- Job description input
- Role, duration, and difficulty selection
- Profile analysis
- 30/60 minute interview planning
- Realistic one-question-at-a-time mock interview loop
- Answer evaluation
- Adaptive next question generation
- Final interview report
- Simple React frontend

The app runs in **mock mode** if `OPENAI_API_KEY` is not configured. Mock mode lets you test the full UI/backend flow without an LLM key. Add your key to get real AI behavior.

---

## Project structure

```text
mock-interview-agent/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── routes/
│   │   │   ├── resume_routes.py
│   │   │   └── interview_routes.py
│   │   └── services/
│   │       ├── resume_parser.py
│   │       ├── llm_client.py
│   │       ├── profile_analyzer.py
│   │       ├── interview_planner.py
│   │       ├── interviewer.py
│   │       ├── evaluator.py
│   │       └── report_generator.py
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── index.html
    ├── package.json
    └── src/
        ├── App.jsx
        └── style.css
```

---

## Backend setup

From the project root:

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:

```bash
OPENAI_API_KEY=your_key_here
LLM_MODEL=gpt-4.1-mini
```

Run backend:

```bash
uvicorn app.main:app --reload --port 8000
```

Open API docs:

```text
http://localhost:8000/docs
```

---

## Frontend setup

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

---

## How to use

1. Enter role, duration, and difficulty.
2. Upload a resume PDF or paste resume text.
3. Paste job description/company requirements.
4. Click **Start Interview**.
5. Answer each interviewer question.
6. Click **End Interview** to get the final report.

---

## Current MVP limitations

- Sessions are stored in memory only. Restarting backend clears sessions.
- PDF parser supports text-based PDFs. Scanned image PDFs need OCR later.
- No authentication yet.
- No PostgreSQL yet.
- No voice mode yet.
- No timer enforcement yet.

---

## Recommended next upgrades

1. Add PostgreSQL for persistent sessions.
2. Add role-specific question banks.
3. Add proper timer and section progression.
4. Add authentication.
5. Add PDF report export.
6. Add voice interview mode.
7. Add company-specific interview styles.
