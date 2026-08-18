#!/usr/bin/env python3
"""端到端冒烟测试：验证 前端 → BFF → Java → Python → MySQL 全链路。

用法：
    python scripts/smoke_test.py [BASE_URL]
默认 BASE_URL=http://localhost:3000（BFF 聚合层）。
"""
import json
import sys
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000"


def req(method, path, payload=None):
    url = BASE + path
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    r = urllib.request.urlopen(
        urllib.request.Request(url, data=data, headers=headers, method=method), timeout=30
    )
    return r.status, json.loads(r.read().decode("utf-8"))


def check(name, ok, extra=""):
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {name} {extra}")
    return ok


def main():
    # 强制 UTF-8 输出，避免 Windows GBK 控制台对 ✓/中文 的编码崩溃
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    ok = True
    print("== CareerLens 端到端冒烟测试 ==")

    try:
        s, _ = req("GET", "/health")
        ok &= check("BFF 健康检查", s == 200)
    except Exception as e:
        check("BFF 健康检查", False, str(e))
        return 1

    try:
        s, jobs = req("GET", "/api/jobs?size=3")
        ok &= check("岗位列表", s == 200 and jobs.get("total", 0) > 0,
                    f"total={jobs.get('total')}")
        job_id = jobs["items"][0]["job_id"]
    except Exception as e:
        check("岗位列表", False, str(e))
        return 1

    try:
        s, detail = req("GET", f"/api/jobs/{job_id}")
        ok &= check("岗位详情", s == 200 and bool(detail.get("description")),
                    str(detail.get("title", "")))
    except Exception as e:
        check("岗位详情", False, str(e))

    resume = "张三，本科，3年经验，Java、Spring Boot、MySQL、Redis、Docker、Git"
    try:
        s, res = req("POST", "/api/analyze", {"resume_text": resume, "job_id": job_id})
        ok &= check("匹配分析", s == 200 and "match_score" in res,
                    f"score={res.get('match_score')} level={res.get('level')}")
    except Exception as e:
        check("匹配分析", False, str(e))

    print("== 结果：", "全部通过 ✓" if ok else "存在失败 ✗", "==")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
