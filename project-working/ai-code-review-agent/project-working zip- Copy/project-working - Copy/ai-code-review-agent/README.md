# AI Code Review & Rewrite Agent (Advanced Version)

This project provides a simple FastAPI backend and a static frontend to perform AI-based code reviews and rewrites. The backend uses the Groq API when a key is provided; otherwise it runs a deterministic stub useful for local testing.

Project structure:

ai-code-review-agent/
│
├── backend/
│   ├── main.py              # FastAPI application with /review and /rewrite endpoints
│   ├── groq_client.py       # Groq API caller with stub fallback
│   ├── schemas.py          # Pydantic request/response models
│   ├── utils.py            # JSON parsing and improvement calculation helpers
│   ├── requirements.txt    # Python dependencies
│   └── .env                # Environment variables (GROQ_API_KEY)
│
├── frontend/
│   ├── index.html          # Frontend UI (Tailwind, highlight.js, marked.js)
│   ├── script.js           # Frontend JS to call backend and render results
│   └── style.css           # Minor styling additions
│
└── README.md


FILES DETAILS

- File: backend/main.py
  - FastAPI app; CORS enabled; POST `/review` and `/rewrite` endpoints.
  - Uses `groq_client.call_groq_system` to fetch model outputs.
  - Uses `safe_parse_json` to ensure the model returned valid JSON.

- File: backend/groq_client.py
  - Calls the Groq API using `requests` if `GROQ_API_KEY` is set.
  - If no key is available, returns a deterministic JSON stub for local testing.

- File: backend/schemas.py
  - Contains Pydantic models: `ReviewRequest`, `RewriteRequest`, `AIReviewResult`.

- File: backend/utils.py
  - Includes `safe_parse_json` to safely parse model outputs.
  - Includes `calculate_improvement_percentage` to compute improvement.

- File: backend/requirements.txt
  - Required Python packages.

- File: backend/.env
  - Put your `GROQ_API_KEY` here. If left empty, the backend uses stub responses.

- File: frontend/index.html
  - UI with textarea, language select, Review/Rewrite buttons, score cards, and comparison panels.

- File: frontend/script.js
  - Sends requests to `/review` and `/rewrite`, renders responses, highlights code.

- File: frontend/style.css
  - Minor custom styles.


RUN INSTRUCTIONS

1) Create a Python virtual environment and install dependencies

```powershell
cd ai-code-review-agent/backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Compatibility note:
- This project is tested with Python 3.11 and 3.12. FastAPI and Pydantic v1 can be
  incompatible with very new Python releases (e.g., Python 3.13+). If you are
  running Python 3.13 or newer, create a virtual environment using Python 3.11 or
  3.12. On Windows you can use the `py` launcher to create a 3.11 venv:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```


2) Add your Groq API key (optional)

Edit `backend/.env` and set:

```
GROQ_API_KEY=sk-xxx
GROQ_API_URL=https://api.groq.cloud/v1
GROQ_MODEL=llama-3.3-70b
```

If you do not set a key, the backend will run with a deterministic stub response for testing.

3) Run the backend

```powershell
cd ai-code-review-agent/backend
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

4) Open the frontend

Open `ai-code-review-agent/frontend/index.html` in your browser (double-click or use VS Code Live Server).

Notes:
- The Groq API request format may differ; if you have an official Groq SDK, replace the `call_groq_system` implementation appropriately.
- The system prompts enforce JSON-only output; the backend uses `safe_parse_json` to extract JSON if necessary.
