import os
import sys
import traceback

# Compatibility guard: FastAPI and pydantic v1 are not guaranteed
# to work on very new Python versions (e.g., 3.13+). Provide a
# clear error message if user runs an unsupported Python.
if sys.version_info >= (3, 13):
    raise RuntimeError(
        "Detected Python 3.13+. This project is tested with Python 3.11/3.12. "
        "Please use Python 3.11 or 3.12 (create a virtualenv with that Python) and reinstall dependencies."
    )

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
except Exception as e:
    raise RuntimeError(
        "Failed to import FastAPI or its dependencies. This often means incompatible Python/pydantic versions. "
        "Use Python 3.11 or 3.12 and install requirements. Original error: " + repr(e)
    )

from dotenv import load_dotenv
from typing import Dict, Any

from schemas import ReviewRequest, RewriteRequest, AIReviewResult
from groq_client import call_groq_system
from utils import safe_parse_json, calculate_improvement_percentage

load_dotenv()

app = FastAPI(title="AI Code Review & Rewrite Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


SYSTEM_PROMPT_REVIEW = (
    "You are an expert senior software engineer and security auditor. "
    "Given the user's code, return ONLY a single valid JSON object (no surrounding text, no markdown) that conforms exactly to the schema:"
    "{\n  \"overall_score\": number (0-100),\n  \"readability\": number (0-10),\n  \"performance\": number (0-10),\n  \"security\": number (0-10),\n  \"maintainability\": number (0-10),\n  \"time_complexity\": \"O(...)\",\n  \"space_complexity\": \"O(...)\",\n  \"issues\": {\n      \"critical\": [],\n      \"high\": [],\n      \"medium\": [],\n      \"low\": []\n  },\n  \"improvement_suggestion\": \"...\",\n  \"rewritten_code\": \"...\"\n}"
)


SYSTEM_PROMPT_REWRITE = (
    "You are a senior software architect and refactoring expert. "
    "Given the user's code and review, produce a refactored, optimized, documented, production-ready version. "
    "Return ONLY a single valid JSON object (no surrounding text) with the same schema as above. "
)


@app.post("/review")
async def review_code(payload: ReviewRequest) -> Dict[str, Any]:
    try:
        user_prompt = (
            f"Language: {payload.language}\n\n"
            f"Code:\n" + payload.code + "\n\n"
            "Tasks:\n"
            "1) Analyze the code for bugs, security issues, and performance problems.\n"
            "2) Classify issues into critical/high/medium/low with line numbers and suggestions.\n"
            "3) Estimate time and space complexity with reasoning (brief).\n"
            "4) Provide an overall code quality score (0-100) and sub-scores.\n"
            "5) Provide a short improvement suggestion and a rewritten optimized version.\n"
            "IMPORTANT: Return only valid JSON that matches the schema exactly."
        )

        raw = call_groq_system(SYSTEM_PROMPT_REVIEW, user_prompt)
        try:
            parsed = safe_parse_json(raw)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Failed to parse model JSON: {e}\nRaw output:\n{raw}")

        return parsed
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rewrite")
async def rewrite_code(payload: RewriteRequest) -> Dict[str, Any]:
    try:
        user_prompt = (
            f"Language: {payload.language}\n\n"
            f"Original Code:\n{payload.code}\n\n"
            "You must produce a refactored, secure, and optimized version. "
            "Also provide new scores consistent with the review schema. "
            "IMPORTANT: Return only valid JSON that matches the schema exactly."
        )

        raw = call_groq_system(SYSTEM_PROMPT_REWRITE, user_prompt)

        try:
            parsed = safe_parse_json(raw)
        except Exception as e:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to parse model JSON: {e}\nRaw output:\n{raw}"
            )

        orig = payload.original_score or parsed.get("overall_score", 0)
        new = parsed.get("overall_score", 0)
        improvement = calculate_improvement_percentage(orig, new)
        parsed["improvement_percentage"] = improvement

        return parsed

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))