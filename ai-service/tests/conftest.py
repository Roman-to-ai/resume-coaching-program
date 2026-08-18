import os

import pytest

from app.models import JobInput


def _fixture_path(name: str) -> str:
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # ai-service/
    candidates = [
        os.path.join(base, "..", "data", "fixtures", "resumes", name),
        os.path.join(base, "data", "fixtures", "resumes", name),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    raise FileNotFoundError(name)


@pytest.fixture
def resume_text() -> str:
    with open(_fixture_path("resume_01.txt"), encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def sample_job() -> JobInput:
    return JobInput(
        job_id="test-job",
        title="Java开发工程师",
        skills="Java, Spring Boot, Spring Cloud, MySQL, Redis, RabbitMQ, Docker",
        experience="1-3年",
        degree="大专",
    )
