"""OCR logic wrapper using PaddleOCR."""

import time
from typing import Any

from paddleocr import PaddleOCR

# Valid task modes per PRD
VALID_TASKS = {"ocr", "table", "chart", "formula", "spotting", "seal"}


class OCREngine:
    """Singleton OCR engine for text extraction."""

    _instance: "OCREngine | None" = None
    _initialized: bool = False

    def __new__(cls) -> "OCREngine":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if OCREngine._initialized:
            return
        self._ocr: PaddleOCR | None = None
        OCREngine._initialized = True

    def load(self) -> None:
        """Initialize PaddleOCR model (idempotent)."""
        if self._ocr is None:
            self._ocr = PaddleOCR(lang="en", show_log=False)

    @property
    def is_loaded(self) -> bool:
        return self._ocr is not None

    def process(self, image_path: str, task: str = "ocr") -> dict[str, Any]:
        """Run OCR on an image and return structured results."""
        if task not in VALID_TASKS:
            raise ValueError(f"Invalid task '{task}'. Must be one of: {VALID_TASKS}")

        if not self.is_loaded:
            self.load()

        start = time.time()

        result = self._ocr.ocr(image_path, cls=True)

        elapsed = time.time() - start

        texts = []
        if result and result[0]:
            for line in result[0]:
                text = line[1][0]
                confidence = line[1][1]
                texts.append(f"[{confidence:.2f}] {text}")

        full_text = "\n".join(texts)

        return {
            "success": len(texts) > 0,
            "text": full_text,
            "task": task,
            "processing_time": round(elapsed, 2),
        }
