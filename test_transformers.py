#!/usr/bin/env python3
"""Quick OCR test using transformers-based PaddleOCR-VL"""

import time
from PIL import Image
import torch
from transformers import AutoProcessor, AutoModelForImageTextToText

def test_ocr(image_path: str) -> dict:
    """Run OCR on an image using PaddleOCR-VL via transformers."""
    print(f"\nTesting: {image_path}")
    print("-" * 50)
    
    start = time.time()
    
    # Load model and processor (cached after first run)
    model_path = "PaddlePaddle/PaddleOCR-VL-1.5"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    print(f"Loading model on {device}...")
    model = AutoModelForImageTextToText.from_pretrained(
        model_path, 
        torch_dtype=torch.bfloat16
    ).to(device).eval()
    
    processor = AutoProcessor.from_pretrained(model_path)
    
    # Load and preprocess image
    image = Image.open(image_path).convert("RGB")
    
    # Prepare prompt
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": "OCR:"},
            ]
        }
    ]
    
    # Process inputs
    max_pixels = 1280 * 28 * 28
    min_pixels = 28 * 28  # Default min
    inputs = processor.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
        images_kwargs={"size": {"shortest_edge": min_pixels, "longest_edge": max_pixels}},
    ).to(model.device)
    
    # Generate
    print("Running inference...")
    outputs = model.generate(**inputs, max_new_tokens=512)
    result = processor.decode(outputs[0][inputs["input_ids"].shape[-1]:-1])
    
    elapsed = time.time() - start
    
    print(f"Processing time: {elapsed:.2f}s")
    print(f"\nExtracted text:")
    print(result if result else "(No text detected)")
    
    return {
        "success": bool(result.strip()),
        "text": result,
        "processing_time": elapsed
    }

if __name__ == "__main__":
    test_images = [
        "test_image/test1.jpg",
        "test_image/test2.jpg"
    ]
    
    print("=" * 50)
    print("PaddleOCR-VL (Transformers) Test - Phase 1")
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
    for img, res in zip(test_images, results):
        status = "✓" if res.get("success") else "✗"
        time_str = f"{res.get('processing_time', 0):.2f}s" if res.get("success") else "N/A"
        print(f"{status} {img}: {time_str}")
