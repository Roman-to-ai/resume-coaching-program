"""抽取脱敏简历 PDF 文本，作为测试 fixture。

用法：
    python data/extract_resumes.py [输出目录]

默认输出到 data/fixtures/resumes/*.txt（UTF-8）。
PDF 文本抽取是加分项，主路径仍是简历文本粘贴。
"""
import glob
import os
import sys

from pypdf import PdfReader

SRC_DIR = "脱敏资料"
DEFAULT_OUT = "data/fixtures/resumes"


def extract(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    parts = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            parts.append(text)
    return "\n\n".join(parts)


def main() -> int:
    out_dir = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUT
    os.makedirs(out_dir, exist_ok=True)

    pdfs = sorted(glob.glob(os.path.join(SRC_DIR, "resume_*.pdf")))
    if not pdfs:
        print(f"未找到简历 PDF：{SRC_DIR}")
        return 1

    written = 0
    for pdf in pdfs:
        name = os.path.splitext(os.path.basename(pdf))[0]
        text = extract(pdf)
        if not text.strip():
            print(f"SKIP {name}: 无文本")
            continue
        out_path = os.path.join(out_dir, f"{name}.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text)
        written += 1
        print(f"OK {name}: {len(text)} chars -> {out_path}")

    print(f"\n共抽取 {written}/{len(pdfs)} 份")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
