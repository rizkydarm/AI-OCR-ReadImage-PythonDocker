#!/usr/bin/env python3
"""EasyOCR test script for CPU inference timing.

Best practices:
- Initialize Reader once (expensive operation)
- Use detail=0 for text-only (faster)
- Set gpu=False explicitly for CPU mode
"""

from pathlib import Path
from typing import TypedDict
import time

import easyocr


class OCRResult(TypedDict):
    """OCR result structure."""

    success: bool
    text: str
    processing_time: float
    error: str | None


def initialize_reader(lang_list: list[str] | None = None, gpu: bool = False) -> easyocr.Reader:
    """Initialize EasyOCR reader with specified languages.

    Args:
        lang_list: List of language codes (default: ['en'])
        gpu: Enable GPU acceleration (default: False for CPU)

    Returns:
        Configured EasyOCR Reader instance
    """
    languages = lang_list or ["en"]
    print(f"Initializing EasyOCR (languages: {languages}, gpu: {gpu})...")

    start = time.time()
    reader = easyocr.Reader(languages, gpu=gpu)
    init_time = time.time() - start

    print(f"Reader initialized in {init_time:.2f}s")
    return reader


def extract_text(reader: easyocr.Reader, image_path: Path | str) -> OCRResult:
    """Extract text from image using EasyOCR.

    Args:
        reader: Initialized EasyOCR Reader
        image_path: Path to image file

    Returns:
        OCRResult with extracted text and timing
    """
    image_path = Path(image_path)

    if not image_path.exists():
        return {
            "success": False,
            "text": "",
            "processing_time": 0.0,
            "error": f"File not found: {image_path}",
        }

    print(f"Processing: {image_path.name}")
    start = time.time()

    try:
        # Use detail=0 for text-only output (faster)
        result = reader.readtext(str(image_path), detail=0)

        elapsed = time.time() - start
        full_text = "\n".join(result) if result else ""

        print(f"  Time: {elapsed:.2f}s")
        print(f"  Extracted text ({len(result)} lines):")
        print("  " + "-" * 40)
        for line in result:
            print(f"    {line}")
        print("  " + "-" * 40)

        return {
            "success": bool(full_text),
            "text": full_text,
            "processing_time": elapsed,
            "error": None,
        }

    except Exception as e:
        elapsed = time.time() - start
        return {
            "success": False,
            "text": "",
            "processing_time": elapsed,
            "error": str(e),
        }


def main() -> None:
    """Run EasyOCR tests on test images."""
    test_images = [
        Path("test_image/test1.jpg"),
        Path("test_image/test2.jpg"),
    ]

    print("=" * 50)
    print("EasyOCR Test - CPU Mode")
    print("=" * 50)

    # Initialize once
    reader = initialize_reader(lang_list=["en"], gpu=False)

    # Test each image
    results: list[tuple[Path, OCRResult]] = []
    for img_path in test_images:
        result = extract_text(reader, img_path)
        results.append((img_path, result))
        print()

    # Summary
    print("=" * 50)
    print("SUMMARY")
    print("=" * 50)

    for img_path, result in results:
        status = "✓" if result["success"] else "✗"
        time_str = f"{result['processing_time']:.2f}s"
        print(f"{status} {img_path.name}: {time_str}")

    # Total timing stats
    total_time = sum(r["processing_time"] for _, r in results)
    avg_time = total_time / len(results) if results else 0
    print(f"\nTotal processing: {total_time:.2f}s")
    print(f"Average per image: {avg_time:.2f}s")


if __name__ == "__main__":
    main()
