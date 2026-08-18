"""岗位匹配与打分（确定性、可解释）。"""
import re

from . import cleaner, normalizer
from .models import (
    GapItem,
    HitItem,
    JobInput,
    MatchResult,
    ResumeIssue,
    StructuredResume,
)

# 学历等级：0 = 不限/未知
DEGREE_LEVEL = {"博士": 4, "硕士": 3, "研究生": 3, "本科": 2, "大专": 1, "专科": 1, "中专": 1, "高中": 1}


def _degree_level(deg: str) -> int:
    if not deg:
        return 0
    for k, v in DEGREE_LEVEL.items():
        if k in deg:
            return v
    return 0


def parse_experience_band(exp: str) -> tuple[float, float]:
    """把 JD 经验档位解析为 (min, max) 年限区间。"""
    s = (exp or "").strip()
    if not s or "不限" in s:
        return (0.0, 99.0)
    if "应届" in s or "在校" in s or "1年以内" in s:
        return (0.0, 1.0)
    m = re.search(r"(\d+)\s*[-~到至]\s*(\d+)", s)
    if m:
        return (float(m.group(1)), float(m.group(2)))
    m = re.search(r"(\d+)\s*年\s*以上", s)
    if m:
        return (float(m.group(1)), 99.0)
    m = re.search(r"(\d+)", s)
    if m:
        return (float(m.group(1)), float(m.group(1)))
    return (0.0, 99.0)


def _gap_suggestion(skill: str) -> str:
    return f"建议通过项目实践或系统学习补齐「{skill}」，并在简历中体现相关经历"


def match(resume_text: str, job: JobInput) -> MatchResult:
    # 1. 清洗 + 结构化字段
    sr: StructuredResume
    issues: list[ResumeIssue]
    sr, issues = cleaner.parse_resume(resume_text)

    # 2. 技能提取（LLM 优先，规则兜底）
    resume_skills, _used_llm = normalizer.extract_skills(resume_text)
    sr.skills = resume_skills
    if len(resume_skills) < 3:
        issues.append(ResumeIssue(
            field="skills", severity="warn",
            message=f"识别到的技能较少（{len(resume_skills)} 项），建议补充专业技能",
        ))

    # 3. JD 技能（归一化，保留未识别原文）
    jd_skills = normalizer.split_jd_skills(job.skills)
    resume_set = set(resume_skills)

    # 4. 命中项 / 缺口（可解释）
    hits: list[HitItem] = []
    gaps: list[GapItem] = []
    for i, js in enumerate(jd_skills):
        if js in resume_set:
            hits.append(HitItem(skill=js, matched_skill=js))
        else:
            gaps.append(GapItem(
                skill=js,
                importance="high" if i < 3 else "medium",
                suggestion=_gap_suggestion(js),
            ))

    # 5. 学历 / 经验匹配
    jd_deg = _degree_level(job.degree)
    resume_deg = _degree_level(sr.degree or "")
    degree_match = jd_deg == 0 or (sr.degree is not None and resume_deg >= jd_deg)
    band_min, _ = parse_experience_band(job.experience)
    experience_match = sr.experience_years is not None and sr.experience_years >= band_min

    # 6. 打分：技能 60 + 经验 25 + 学历 15
    n = max(len(jd_skills), 1)
    skill_score = 60 * len(hits) / n
    exp_score = 25 if experience_match else 0
    deg_score = 15 if degree_match else 0
    score = round(skill_score + exp_score + deg_score)
    level = "high" if score >= 70 else ("medium" if score >= 40 else "low")

    return MatchResult(
        match_score=score,
        level=level,
        hits=hits,
        gaps=gaps,
        degree_match=degree_match,
        experience_match=experience_match,
        structured_resume=sr,
        issues=issues,
    )
