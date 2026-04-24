"""FastAPI OCR backend for n8n integration."""

import os
import time
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

from app.ocr import DualOCREngine

# Load environment variables
load_dotenv()

# Track startup time for health check
START_TIME = time.time()

# Initialize dual-engine OCR (EasyOCR as primary, OCR.space as fallback)
ocr_engine = DualOCREngine()


app = FastAPI(
    title="AI OCR Backend",
    description="FastAPI microservice for OCR via OCR.space API + EasyOCR fallback",
    version="0.1.0",
)


@app.get("/health")
async def health_check() -> dict[str, Any]:
    """Return health status and engine availability."""
    uptime = time.time() - START_TIME
    api_key = os.getenv("OCR_SPACE_API_KEY", "")
    api_key_configured = bool(api_key and api_key != "helloworld")

    # Determine status
    if api_key_configured or ocr_engine.fallback_available:
        status = "healthy"
    else:
        status = "error"

    return {
        "status": status,
        "engines": {
            "ocrspace": "available" if api_key_configured else "unavailable",
            "easyocr": "available",
        },
        "api_key_configured": api_key_configured,
        "uptime": round(uptime, 2),
    }


@app.post("/ocr")
async def ocr_endpoint(file: UploadFile = File(...)) -> JSONResponse:
    """Process uploaded image with OCR (auto-fallback to EasyOCR if needed)."""
    temp_path: Path | None = None

    try:
        # Save uploaded file to temp location
        suffix = Path(file.filename or "image.jpg").suffix
        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            temp_path = Path(tmp.name)

        # Run OCR with automatic fallback
        result = ocr_engine.process(temp_path)
        return JSONResponse(content=dict(result))

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "text": "",
                "engine": "none",
                "processing_time": 0.0,
                "error": str(e),
            },
        )

    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()
