"""OCR logic wrapper using OCR.space API (primary) and EasyOCR (fallback)."""

import os
import time
from pathlib import Path
from typing import Any

import easyocr
import requests


class OCRResult(dict):
    """OCR result with standard fields."""

    def __init__(
        self,
        success: bool,
        text: str,
        engine: str,
        processing_time: float,
        error: str | None = None,
    ):
        super().__init__()
        self["success"] = success
        self["text"] = text
        self["engine"] = engine
        self["processing_time"] = round(processing_time, 2)
        if error:
            self["error"] = error


class OCRSpaceEngine:
    """OCR.space API client for cloud OCR."""

    API_ENDPOINT = "https://api.ocr.space/parse/image"

    def __init__(self, api_key: str | None = None) -> None:
        """Initialize with API key."""
        self.api_key = api_key or os.getenv("OCR_SPACE_API_KEY", "")
        self.available = bool(self.api_key and self.api_key != "helloworld")

    def process(self, image_path: Path | str) -> OCRResult:
        """Run OCR via OCR.space API."""
        image_path = Path(image_path)
        start = time.time()

        try:
            with image_path.open("rb") as f:
                response = requests.post(
                    self.API_ENDPOINT,
                    files={"file": f},
                    data={
                        "apikey": self.api_key,
                        "language": "eng",
                        "OCREngine": 2,
                        "isOverlayRequired": False,
                        "detectOrientation": True,
                    },
                    timeout=60,
                )

            elapsed = time.time() - start

            if response.status_code != 200:
                return OCRResult(
                    success=False,
                    text="",
                    engine="ocrspace",
                    processing_time=elapsed,
                    error=f"HTTP {response.status_code}",
                )

            data = response.json()

            if data.get("OCRExitCode") != 1:
                error_msg = data.get("ErrorMessage", ["Unknown error"])
                return OCRResult(
                    success=False,
                    text="",
                    engine="ocrspace",
                    processing_time=elapsed,
                    error=str(error_msg),
                )

            parsed_results = data.get("ParsedResults", [])
            if not parsed_results:
                return OCRResult(
                    success=False,
                    text="",
                    engine="ocrspace",
                    processing_time=elapsed,
                    error="No text found",
                )

            lines: list[str] = []
            for result in parsed_results:
                text_overlay = result.get("TextOverlay", {})
                for line in text_overlay.get("Lines", []):
                    line_text = line.get("LineText", "").strip()
                    if line_text:
                        lines.append(line_text)

            full_text = "\n".join(lines)

            return OCRResult(
                success=bool(full_text),
                text=full_text,
                engine="ocrspace",
                processing_time=elapsed,
            )

        except requests.exceptions.Timeout:
            elapsed = time.time() - start
            return OCRResult(
                success=False,
                text="",
                engine="ocrspace",
                processing_time=elapsed,
                error="Request timeout",
            )
        except Exception as e:
            elapsed = time.time() - start
            return OCRResult(
                success=False,
                text="",
                engine="ocrspace",
                processing_time=elapsed,
                error=str(e),
            )


class EasyOCREngine:
    """Local EasyOCR engine for fallback."""

    def __init__(self) -> None:
        """Initialize EasyOCR reader."""
        self._reader: easyocr.Reader | None = None
        self._initialized = False

    def load(self) -> None:
        """Load EasyOCR model (lazy loading)."""
        if not self._initialized:
            self._reader = easyocr.Reader(["en"], gpu=False)
            self._initialized = True

    @property
    def is_loaded(self) -> bool:
        return self._initialized

    def process(self, image_path: Path | str) -> OCRResult:
        """Run OCR via EasyOCR."""
        image_path = Path(image_path)
        start = time.time()

        try:
            if not self.is_loaded:
                self.load()

            result = self._reader.readtext(str(image_path), detail=0)
            elapsed = time.time() - start

            full_text = "\n".join(result) if result else ""

            return OCRResult(
                success=bool(full_text),
                text=full_text,
                engine="easyocr",
                processing_time=elapsed,
            )

        except Exception as e:
            elapsed = time.time() - start
            return OCRResult(
                success=False,
                text="",
                engine="easyocr",
                processing_time=elapsed,
                error=str(e),
            )


class DualOCREngine:
    """Dual-engine OCR: OCR.space primary, EasyOCR fallback."""

    def __init__(self) -> None:
        """Initialize both engines."""
        self.primary = OCRSpaceEngine()
        self.fallback = EasyOCREngine()

    @property
    def primary_available(self) -> bool:
        return self.primary.available

    @property
    def fallback_available(self) -> bool:
        return True  # EasyOCR always available once loaded

    def process(self, image_path: Path | str) -> OCRResult:
        """Run OCR with automatic fallback."""
        # Try primary first
        if self.primary_available:
            result = self.primary.process(image_path)
            if result["success"]:
                return result

        # Fallback to EasyOCR
        return self.fallback.process(image_path)

