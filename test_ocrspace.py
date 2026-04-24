#!/usr/bin/env python3
"""OCR.space API test script for cloud-based OCR inference.

API: https://api.ocr.space/parse/image
Documentation: https://ocr.space/OCRAPI

Best practices:
- Use environment variable for API key
- Handle rate limits (free tier: 500 req/month)
- Support both file upload and URL input
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TypedDict
import time

from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()


class OCRResult(TypedDict):
    """OCR result structure."""

    success: bool
    text: str
    processing_time: float
    error: str | None
    engine: str | None


class OCRSpaceClient:
    """OCR.space API client."""

    API_ENDPOINT = "https://api.ocr.space/parse/image"

    def __init__(
        self,
        api_key: str | None = None,
        language: str = "eng",
        ocr_engine: int = 2,
    ) -> None:
        """Initialize OCR.space client.

        Args:
            api_key: OCR.space API key (default: from OCR_SPACE_API_KEY env var)
            language: OCR language code (default: eng)
            ocr_engine: OCR engine (1, 2, or 3) - 2 recommended for accuracy
        """
        self.api_key = api_key or os.getenv("OCR_SPACE_API_KEY", "K81670139088957")
        self.language = language
        self.ocr_engine = ocr_engine

    def ocr_file(self, image_path: Path | str) -> OCRResult:
        """Perform OCR on a local image file.

        Args:
            image_path: Path to image file

        Returns:
            OCRResult with extracted text
        """
        image_path = Path(image_path)

        if not image_path.exists():
            return {
                "success": False,
                "text": "",
                "processing_time": 0.0,
                "error": f"File not found: {image_path}",
                "engine": None,
            }

        print(f"Uploading: {image_path.name}")
        start = time.time()

        try:
            with image_path.open("rb") as f:
                response = requests.post(
                    self.API_ENDPOINT,
                    files={"file": f},
                    data={
                        "apikey": self.api_key,
                        "language": self.language,
                        "OCREngine": self.ocr_engine,
                        "isOverlayRequired": False,
                        "detectOrientation": True,
                    },
                    timeout=60,
                )

            elapsed = time.time() - start

            if response.status_code != 200:
                return {
                    "success": False,
                    "text": "",
                    "processing_time": elapsed,
                    "error": f"HTTP {response.status_code}: {response.text[:200]}",
                    "engine": None,
                }

            data = response.json()

            # Check for API-level errors
            if data.get("OCRExitCode") != 1:
                error_msg = data.get("ErrorMessage", ["Unknown error"])
                return {
                    "success": False,
                    "text": "",
                    "processing_time": elapsed,
                    "error": f"API error: {error_msg}",
                    "engine": None,
                }

            # Extract text from results
            parsed_results = data.get("ParsedResults", [])
            if not parsed_results:
                return {
                    "success": False,
                    "text": "",
                    "processing_time": elapsed,
                    "error": "No text found in image",
                    "engine": None,
                }

            # Combine all text lines
            all_text: list[str] = []
            for result in parsed_results:
                text_overlay = result.get("TextOverlay", {})
                lines = text_overlay.get("Lines", [])
                for line in lines:
                    line_text = line.get("LineText", "").strip()
                    if line_text:
                        all_text.append(line_text)

            # Also get the full parsed text
            full_text = "\n".join(all_text) if all_text else ""

            print(f"  Time: {elapsed:.2f}s")
            print(f"  Engine: OCR Engine {self.ocr_engine}")
            print(f"  Extracted text ({len(all_text)} lines):")
            print("  " + "-" * 40)
            for line in all_text:
                print(f"    {line}")
            print("  " + "-" * 40)

            return {
                "success": bool(full_text),
                "text": full_text,
                "processing_time": elapsed,
                "error": None,
                "engine": f"Engine {self.ocr_engine}",
            }

        except requests.exceptions.Timeout:
            elapsed = time.time() - start
            return {
                "success": False,
                "text": "",
                "processing_time": elapsed,
                "error": "Request timeout (60s)",
                "engine": None,
            }
        except Exception as e:
            elapsed = time.time() - start
            return {
                "success": False,
                "text": "",
                "processing_time": elapsed,
                "error": str(e),
                "engine": None,
            }


def main() -> None:
    """Run OCR.space API tests on test images."""
    test_images = [
        Path("test_image/test1.jpg"),
        Path("test_image/test2.jpg"),
    ]

    print("=" * 50)
    print("OCR.space API Test - Cloud OCR")
    print("=" * 50)

    # Check for API key
    api_key = os.getenv("OCR_SPACE_API_KEY", "helloworld")
    if api_key == "helloworld":
        print("\n⚠️  Using demo API key (helloworld)")
        print("   For production use, set OCR_SPACE_API_KEY env variable")
        print("   Get free API key at: https://ocr.space/OCRAPI\n")

    # Initialize client
    client = OCRSpaceClient(
        api_key=api_key,
        language="eng",
        ocr_engine=2,  # Engine 2: best accuracy
    )

    # Test each image
    results: list[tuple[Path, OCRResult]] = []
    for img_path in test_images:
        if img_path.exists():
            result = client.ocr_file(img_path)
            results.append((img_path, result))
            print()
        else:
            print(f"⚠️  Skipping {img_path} (file not found)\n")
            results.append((img_path, {
                "success": False,
                "text": "",
                "processing_time": 0,
                "error": "File not found",
                "engine": None,
            }))

    # Summary
    print("=" * 50)
    print("SUMMARY")
    print("=" * 50)

    for img_path, result in results:
        status = "✓" if result["success"] else "✗"
        time_str = f"{result['processing_time']:.2f}s"
        engine = result.get("engine", "N/A")
        print(f"{status} {img_path.name}: {time_str} ({engine})")

    # Total timing
    total_time = sum(r["processing_time"] for _, r in results)
    avg_time = total_time / len(results) if results else 0
    print(f"\nTotal processing: {total_time:.2f}s")
    print(f"Average per image: {avg_time:.2f}s")


if __name__ == "__main__":
    main()
