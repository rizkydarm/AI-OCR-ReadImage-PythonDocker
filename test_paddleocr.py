#!/usr/bin/env python3
"""Quick OCR test using standard PaddleOCR (faster than PaddleOCR-VL)"""

import time
from paddleocr import PaddleOCR

def test_ocr(image_path: str) -> dict:
    """Run OCR on an image and return results."""
    print(f"\nTesting: {image_path}")
    print("-" * 50)
    
    start = time.time()
    
    # Initialize OCR with minimal config
    ocr = PaddleOCR(lang='en')
    
    # Run OCR
    result = ocr.predict(image_path)
    
    elapsed = time.time() - start
    
    # Extract text
    texts = []
    if result and result[0]:
        for line in result[0]:
            text = line[1][0]
            confidence = line[1][1]
            texts.append(f"[{confidence:.2f}] {text}")
    
    full_text = "\n".join(texts)
    
    print(f"Processing time: {elapsed:.2f}s")
    print(f"Lines detected: {len(texts)}")
    print("\nExtracted text:")
    print(full_text if full_text else "(No text detected)")
    
    return {
        "success": len(texts) > 0,
        "text": full_text,
        "lines": len(texts),
        "processing_time": elapsed
    }

if __name__ == "__main__":
    import sys
    
    test_images = [
        "test_image/test1.jpg",
        "test_image/test2.jpg"
    ]
    
    print("=" * 50)
    print("PaddleOCR Test - Phase 1")
    print("=" * 50)
    
    results = []
    for img in test_images:
        try:
            result = test_ocr(img)
            results.append(result)
        except Exception as e:
            print(f"ERROR: {e}")
            results.append({"success": False, "error": str(e)})
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    for i, (img, res) in enumerate(zip(test_images, results)):
        status = "✓" if res.get("success") else "✗"
        time_str = f"{res.get('processing_time', 0):.2f}s" if res.get("success") else "N/A"
        print(f"{status} {img}: {time_str}")
