from pydantic import BaseModel
from typing import Optional, Any, Dict


class ReviewRequest(BaseModel):
    code: str
    language: str


class RewriteRequest(BaseModel):
    code: str
    language: str
    original_score: Optional[float]


class AIReviewResult(BaseModel):
    overall_score: float
    readability: float
    performance: float
    security: float
    maintainability: float
    time_complexity: str
    space_complexity: str
    issues: Dict[str, Any]
    improvement_suggestion: str
    rewritten_code: str
