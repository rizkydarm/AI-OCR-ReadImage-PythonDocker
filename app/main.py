"""FastAPI OCR backend for n8n integration."""

import time
from contextlib import asynccontextmanager
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse

from app.ocr import OCREngine

# Track startup time for health check
START_TIME = time.time()


def get_engine() -> OCREngine:
    """Get or create the singleton OCR engine."""
    return OCREngine()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load OCR model at startup."""
    engine = get_engine()
    engine.load()
    yield


app = FastAPI(
    title="AI OCR Backend",
    description="FastAPI microservice for OCR via PaddleOCR",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check() -> dict[str, Any]:
    """Return health status and model load state."""
    engine = get_engine()
    uptime = time.time() - START_TIME

    status = "healthy" if engine.is_loaded else "initializing"
    if not engine.is_loaded:
        status = "error"

    return {
        "status": status,
        "model_loaded": engine.is_loaded,
        "uptime": round(uptime, 2),
    }


@app.post("/ocr")
async def ocr_endpoint(
    file: UploadFile = File(...),
    task: str = Form("ocr"),
) -> JSONResponse:
    """Process uploaded image with OCR."""
    engine = get_engine()

    if not engine.is_loaded:
        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "text": "",
                "task": task,
                "processing_time": 0.0,
                "error": "OCR engine not initialized",
            },
        )

    temp_path: Path | None = None
    try:
        suffix = Path(file.filename or "image.jpg").suffix
        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            temp_path = Path(tmp.name)

        result = engine.process(str(temp_path), task=task)
        return JSONResponse(content=result)

    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "text": "",
                "task": task,
                "processing_time": 0.0,
                "error": str(e),
            },
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "text": "",
                "task": task,
                "processing_time": 0.0,
                "error": str(e),
            },
        )

    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()
