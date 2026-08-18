"""环境配置。留空 OPENAI_API_KEY 时 AI 服务自动降级为规则算法。"""
import os


def _get(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()


OPENAI_API_KEY = _get("OPENAI_API_KEY")
OPENAI_BASE_URL = _get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
OPENAI_MODEL = _get("OPENAI_MODEL", "gpt-4o-mini")
LLM_TIMEOUT = float(_get("LLM_TIMEOUT", "15"))
