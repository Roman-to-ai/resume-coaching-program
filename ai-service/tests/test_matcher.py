from app import matcher
from app.models import JobInput


def test_parse_experience_band():
    assert matcher.parse_experience_band("1-3年") == (1.0, 3.0)
    assert matcher.parse_experience_band("3-5年") == (3.0, 5.0)
    assert matcher.parse_experience_band("不限") == (0.0, 99.0)
    assert matcher.parse_experience_band("应届") == (0.0, 1.0)


def test_match_resume_01(resume_text, sample_job):
    result = matcher.match(resume_text, sample_job)
    assert 0 <= result.match_score <= 100
    hit_skills = {h.skill for h in result.hits}
    assert "Java" in hit_skills
    assert "MySQL" in hit_skills
    assert result.degree_match is True
    assert result.experience_match is True
    assert result.structured_resume.degree == "本科"


def test_match_gaps_when_skill_missing():
    job = JobInput(job_id="x", skills="Java, Rust", degree="不限", experience="不限")
    result = matcher.match("我熟练掌握 Java 开发，三年经验", job)
    gap_skills = {g.skill for g in result.gaps}
    assert "Rust" in gap_skills
    assert "Java" in {h.skill for h in result.hits}


def test_level_thresholds():
    assert matcher.match("无技能文本", JobInput(skills="Java, Rust", degree="不限", experience="不限")).level == "low"
