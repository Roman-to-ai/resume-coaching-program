"""CareerLens AI 服务（清洗 / 归一化 / 匹配 / PDF 提取）。"""
import io

from fastapi import FastAPI, HTTPException, UploadFile

from .matcher import match
from .models import AnalyzeRequest, MatchResult

app = FastAPI(title="CareerLens AI Service", version="1.0.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/v1/analyze", response_model=MatchResult)
def analyze(req: AnalyzeRequest) -> MatchResult:
    return match(req.resume_text, req.job)


@app.post("/api/v1/extract-pdf")
async def extract_pdf(file: UploadFile) -> dict:
    """从上传的 PDF 中提取纯文本，供前端「粘贴文本 / 上传 PDF」两种输入使用。"""
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="仅支持 PDF 文件")

    from pypdf import PdfReader

    data = await file.read()
    reader = PdfReader(io.BytesIO(data))
    text = "\n".join((page.extract_text() or "") for page in reader.pages)
    return {"text": text}
