from app import cleaner


def test_clean_text_removes_residual_token():
    text = "学历：本科\n1b44e1baa68b59e31HN509u6FVNTyo66VPyYWOKllvXRNxhj2A~~"
    out = cleaner.clean_text(text)
    assert "1b44e1" not in out
    assert "学历：本科" in out


def test_extract_degree_explicit():
    assert cleaner.extract_degree("姓名：张三\n学历：本科") == "本科"


def test_extract_degree_fallback():
    assert cleaner.extract_degree("我是本科毕业，计算机专业") == "本科"


def test_extract_experience_years():
    assert cleaner.extract_experience_years("工作年限：3年") == 3.0


def test_extract_experience_from_range():
    text = "2023.07-2026.07 某公司 java开发工程师"
    assert cleaner.extract_experience_years(text) == 3.0


def test_extract_role():
    assert cleaner.extract_role("求职意向：java开发工程师\n邮箱") == "java开发工程师"


def test_parse_resume_issues():
    sr, issues = cleaner.parse_resume("只有一句话的简历")
    assert len(sr.summary) > 0
    assert any(i.field == "resume" for i in issues)
