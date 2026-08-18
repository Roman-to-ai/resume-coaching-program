"""OpenAI-compatible LLM 客户端。任何失败都返回 None，由调用方降级到规则算法。"""
import json
import logging

import httpx

from . import config

logger = logging.getLogger(__name__)


def available() -> bool:
    return bool(config.OPENAI_API_KEY)


def chat(messages: list[dict], temperature: float = 0.0) -> str | None:
    """调用 OpenAI-compatible /chat/completions，失败返回 None。"""
    if not config.OPENAI_API_KEY:
        return None
    url = f"{config.OPENAI_BASE_URL}/chat/completions"
    payload = {
        "model": config.OPENAI_MODEL,
        "messages": messages,
        "temperature": temperature,
    }
    headers = {"Authorization": f"Bearer {config.OPENAI_API_KEY}"}
    try:
        resp = httpx.post(url, json=payload, headers=headers, timeout=config.LLM_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception as exc:  # noqa: BLE001 - 任何失败都降级
        logger.warning("LLM 调用失败，降级规则算法: %s", exc)
        return None


def extract_skills(text: str) -> list[str] | None:
    """用 LLM 从简历文本提取技能（返回 JSON 数组），失败返回 None。"""
    prompt = (
        "你是简历解析助手。从下面的简历文本中提取所有专业技能/技术栈，"
        "只返回一个 JSON 数组，元素为技能规范名，例如 "
        '["Java","Spring Boot","MySQL","Redis"]。'
        "不要输出任何其它文字。若无法识别则返回 []。\n\n简历文本：\n" + text
    )
    raw = chat([{"role": "user", "content": prompt}])
    if raw is None:
        return None
    try:
        # 容错：截取首个 '[' 到最后一个 ']' 之间的内容
        start, end = raw.find("["), raw.rfind("]")
        if start == -1 or end == -1:
            return None
        parsed = json.loads(raw[start : end + 1])
        if isinstance(parsed, list):
            return [str(x).strip() for x in parsed if str(x).strip()]
    except (json.JSONDecodeError, ValueError):
        return None
    return None
