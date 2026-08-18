"""简历清洗与结构化字段抽取（规则路径，确定性）。"""
import re

from .models import ResumeIssue, StructuredResume

# 脱敏残留：长 base64 串（>=25 个字母数字，可能带 ~ 结尾）
_RESIDUAL_RE = re.compile(r"[A-Za-z0-9]{25,}~*")

_DEGREE_LEVELS = {
    "博士": 4, "硕士": 3, "研究生": 3, "本科": 2,
    "大专": 1, "专科": 1, "中专": 1, "高中": 1,
}

_DEGREE_ORDER = ["博士", "硕士", "研究生", "本科", "大专", "专科", "中专", "高中"]


def clean_text(text: str) -> str:
    """去除脱敏残留 token，规整空白。"""
    t = _RESIDUAL_RE.sub(" ", text)
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n[ \t]*\n+", "\n", t)
    lines = [ln.strip() for ln in t.splitlines()]
    return "\n".join(ln for ln in lines if ln).strip()


def extract_degree(text: str) -> str | None:
    # 优先 "学历: xxx" 显式声明
    m = re.search(r"学历\s*[:：]?\s*(博士|硕士|研究生|本科|大专|专科|中专|高中)", text)
    if m:
        return m.group(1)
    # 否则取全文出现的最靠前的学历关键词
    for d in _DEGREE_ORDER:
        if d in text:
            return d
    return None


def extract_experience_years(text: str) -> float | None:
    # 1) "工作年限: 3年"
    m = re.search(r"工作年限\s*[:：]?\s*(\d+(?:\.\d+)?)\s*年?", text)
    if m:
        return float(m.group(1))
    # 2) "X年(以上)?(工作)?经验"
    m = re.search(r"(\d+(?:\.\d+)?)\s*年\s*(?:以上)?\s*(?:工作)?经验", text)
    if m:
        return float(m.group(1))
    # 3) 从最近一段工作经历的年份跨度推算
    ranges = re.findall(r"(20\d{2})[.年/]\s*\d{1,2}\s*[.月]?\s*[-—~至]\s*(20\d{2}|至今|现在|今)", text)
    if ranges:
        start, end = ranges[0]
        end_year = int(start) if end in ("至今", "现在", "今") else int(end)
        return float(end_year - int(start))
    return None


def extract_role(text: str) -> str | None:
    m = re.search(r"(?:求职意向|期望职位|目标岗位|期望岗位)\s*[:：]?\s*(.{1,40}?)(?:\n|$)", text)
    if m:
        role = m.group(1).strip("：:，,。；; ")
        return role or None
    return None


def _degree_level(degree: str) -> int:
    return _DEGREE_LEVELS.get(degree, 0)


def parse_resume(text: str) -> tuple[StructuredResume, list[ResumeIssue]]:
    """清洗 + 抽取结构化字段，返回 (结构化简历, 简历问题列表)。"""
    cleaned = clean_text(text)
    sr = StructuredResume(
        degree=extract_degree(cleaned),
        experience_years=extract_experience_years(cleaned),
        role=extract_role(cleaned),
        summary=cleaned[:300],
    )
    issues: list[ResumeIssue] = []
    if len(cleaned) < 50:
        issues.append(ResumeIssue(field="resume", severity="error", message="简历文本过短，可能未完整提交"))
    if sr.degree is None:
        issues.append(ResumeIssue(field="degree", severity="warn", message="未识别到学历信息，建议补充"))
    if sr.experience_years is None:
        issues.append(ResumeIssue(field="experience", severity="warn", message="未识别到工作年限，建议补充"))
    if sr.role is None:
        issues.append(ResumeIssue(field="role", severity="info", message="未识别到求职意向"))
    return sr, issues
