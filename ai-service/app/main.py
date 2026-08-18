"""CareerLens AI 服务（清洗 / 归一化 / 匹配）。"""
from fastapi import FastAPI

from .matcher import match
from .models import AnalyzeRequest, MatchResult

app = FastAPI(title="CareerLens AI Service", version="1.0.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/v1/analyze", response_model=MatchResult)
def analyze(req: AnalyzeRequest) -> MatchResult:
    return match(req.resume_text, req.job)
