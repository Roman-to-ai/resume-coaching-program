from app import normalizer


def test_normalize_variants():
    assert normalizer.normalize("springboot") == "Spring Boot"
    assert normalizer.normalize("Spring Boot") == "Spring Boot"
    assert normalizer.normalize("K8s") == "Kubernetes"
    assert normalizer.normalize("mysql") == "MySQL"


def test_normalize_unknown():
    assert normalizer.normalize("不存在的技术xxx") is None


def test_split_jd_skills():
    skills = normalizer.split_jd_skills("Java, Docker, MySQL, 大数据经验")
    assert "Java" in skills
    assert "Docker" in skills
    assert "MySQL" in skills
    assert "大数据" in skills


def test_extract_skills_rules():
    text = "熟练使用 Redis 缓存，掌握 SpringBoot 与 MyBatis-Plus 开发"
    skills = normalizer.extract_skills_rules(text)
    assert "Redis" in skills
    assert "Spring Boot" in skills
    assert "MyBatis-Plus" in skills
