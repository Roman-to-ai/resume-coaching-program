"""请求/响应 DTO，与 contracts/openapi.yaml 的 MatchResult 对齐。"""
from typing import List, Optional

from pydantic import BaseModel, Field


class JobInput(BaseModel):
    """Java 后端下发给 AI 服务的岗位信息（已从 DB 取出）。"""

    job_id: Optional[str] = None
    title: Optional[str] = None
    skills: str = ""          # 逗号分隔技能串
    description: str = ""     # 岗位描述（HTML 或纯文本）
    experience: str = ""      # 经验档位，如 1-3年
    degree: str = ""          # 学历要求，如 大专


class AnalyzeRequest(BaseModel):
    resume_text: str = Field(..., min_length=1)
    job: JobInput


class HitItem(BaseModel):
    skill: str
    matched_skill: str
    source: str = "技能列表"


class GapItem(BaseModel):
    skill: str
    importance: str = "medium"   # high / medium / low
    suggestion: str = ""


class StructuredResume(BaseModel):
    skills: List[str] = []
    experience_years: Optional[float] = None
    degree: Optional[str] = None
    role: Optional[str] = None
    summary: Optional[str] = None


class ResumeIssue(BaseModel):
    field: str
    severity: str = "warn"       # error / warn / info
    message: str


class MatchResult(BaseModel):
    match_score: int
    level: str                   # high / medium / low
    hits: List[HitItem] = []
    gaps: List[GapItem] = []
    degree_match: bool
    experience_match: bool
    structured_resume: StructuredResume
    issues: List[ResumeIssue] = []
