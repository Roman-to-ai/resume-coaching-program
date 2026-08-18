"""技能归一化：别名 -> 规范名。规则路径为主，LLM 路径可选。"""
import re

from . import llm

# 规范名 -> 别名列表（小写）。覆盖 Java 后端求职主流技术栈。
SKILL_ALIASES: dict[str, list[str]] = {
    "Java": ["java", "jdk", "j2ee", "jvm", "java开发"],
    "Spring": ["spring", "spring framework"],
    "Spring Boot": ["springboot", "spring boot", "spring-boot", "springboot框架"],
    "Spring Cloud": ["springcloud", "spring cloud", "spring-cloud", "springcloudalibaba", "spring cloud alibaba"],
    "Spring Security": ["spring security", "springsecurity"],
    "MyBatis": ["mybatis"],
    "MyBatis-Plus": ["mybatis-plus", "mybatis plus", "mybatisplus"],
    "MySQL": ["mysql", "mysq", "sql"],
    "PostgreSQL": ["postgresql", "postgres", "pg"],
    "Oracle": ["oracle"],
    "SQL Server": ["sqlserver", "sql server"],
    "Redis": ["redis"],
    "RabbitMQ": ["rabbitmq", "rabbit mq", "rabbitmq消息队列"],
    "Kafka": ["kafka"],
    "RocketMQ": ["rocketmq", "rocket mq"],
    "MongoDB": ["mongodb", "mongo"],
    "Elasticsearch": ["elasticsearch", "elastic search", "es"],
    "Nacos": ["nacos"],
    "Gateway": ["gateway", "spring cloud gateway"],
    "Feign": ["feign", "openfeign", "open feign"],
    "Sentinel": ["sentinel"],
    "Seata": ["seata"],
    "Dubbo": ["dubbo"],
    "ZooKeeper": ["zookeeper", "zk"],
    "Docker": ["docker"],
    "Kubernetes": ["kubernetes", "k8s"],
    "Jenkins": ["jenkins"],
    "Git": ["git"],
    "Maven": ["maven"],
    "Gradle": ["gradle"],
    "Linux": ["linux"],
    "Nginx": ["nginx"],
    "Tomcat": ["tomcat"],
    "Vue": ["vue", "vue2", "vue3", "vue.js"],
    "React": ["react", "react.js"],
    "JavaScript": ["javascript", "js", "ajax"],
    "TypeScript": ["typescript", "ts"],
    "HTML/CSS": ["html", "css", "html5", "css3"],
    "Element UI": ["element ui", "elementui", "element plus", "element-plus", "elementplus"],
    "Node.js": ["node.js", "nodejs", "node"],
    "Python": ["python"],
    "Go": ["golang", "go语言", "go 语言"],
    "C++": ["c++", "cpp"],
    "C#": ["c#", "csharp"],
    "JWT": ["jwt"],
    "Shiro": ["shiro"],
    "Quartz": ["quartz"],
    "WebSocket": ["websocket"],
    "RESTful": ["restful", "rest"],
    "大数据": ["大数据", "hadoop", "spark", "flink", "hive", "hbase", "kafka"],
    "AI/大模型": ["大模型", "llm", "rag", "ai应用", "智能客服", "智能问答", "openai", "langchain", "coze", "人工智能"],
    "微服务": ["微服务"],
    "分布式": ["分布式"],
    "高并发": ["高并发"],
    "CI/CD": ["ci/cd", "cicd", "持续集成", "持续部署", "devops"],
}

# 别名（小写）-> 规范名，长别名优先（避免 "spring" 先于 "spring boot" 命中）
_ALIAS_TO_CANON: dict[str, str] = {}
for _canon, _aliases in SKILL_ALIASES.items():
    for _a in _aliases:
        _ALIAS_TO_CANON[_a.lower()] = _canon

_SORTED_ALIASES = sorted(_ALIAS_TO_CANON.keys(), key=len, reverse=True)


def _pattern_for(alias: str) -> re.Pattern:
    """ASCII 纯字母数字的短别名用词边界，其余用子串，避免误命中。"""
    escaped = re.escape(alias)
    if alias.isascii() and alias.isalnum():
        return re.compile(rf"\b{escaped}\b", re.IGNORECASE)
    return re.compile(escaped, re.IGNORECASE)


_PATTERNS = [(alias, _pattern_for(alias)) for alias in _SORTED_ALIASES]


def normalize(skill: str) -> str | None:
    """把单个技能名归一化到规范名；未识别返回 None。"""
    key = skill.strip().lower()
    if key in _ALIAS_TO_CANON:
        return _ALIAS_TO_CANON[key]
    # 尝试子串归一化（如 "java开发工程师" -> Java）
    for alias, pat in _PATTERNS:
        if pat.search(key):
            return _ALIAS_TO_CANON[alias]
    return None


def extract_skills_rules(text: str) -> list[str]:
    """规则路径：扫描简历文本，返回去重后的规范技能列表（保持出现顺序）。"""
    found: list[str] = []
    seen: set[str] = set()
    lower = text.lower()
    for alias, pat in _PATTERNS:
        if pat.search(lower):
            canon = _ALIAS_TO_CANON[alias]
            if canon not in seen:
                seen.add(canon)
                found.append(canon)
    return found


def extract_skills(text: str) -> tuple[list[str], bool]:
    """提取简历技能。返回 (技能列表, 是否使用了 LLM)。LLM 失败降级规则。"""
    if llm.available():
        llm_skills = llm.extract_skills(text)
        if llm_skills:
            return (llm_skills, True)
    return (extract_skills_rules(text), False)


def split_jd_skills(skills_str: str) -> list[str]:
    """把 JD 的逗号分隔技能串拆成规范技能列表（去重保序）。"""
    result: list[str] = []
    seen: set[str] = set()
    for raw in re.split(r"[,，、;；/]+", skills_str or ""):
        s = raw.strip()
        if not s:
            continue
        canon = normalize(s)
        if canon is None:
            canon = s  # 未识别也保留原文，保证 JD 技能不丢
        if canon not in seen:
            seen.add(canon)
            result.append(canon)
    return result
