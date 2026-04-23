#!/usr/bin/env python3
"""OCR timing test - loads model once, tests both images (30s timeout per image)"""

import time
import signal
from PIL import Image
import torch
from transformers import AutoProcessor, AutoModelForImageTextToText

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("OCR processing exceeded 30s limit")

# Set 30s timeout
signal.signal(signal.SIGALRM, timeout_handler)

# Load model once
print("Loading PaddleOCR-VL model...")
start_load = time.time()
model_path = "PaddlePaddle/PaddleOCR-VL-1.5"
device = "cpu"
model = AutoModelForImageTextToText.from_pretrained(
    model_path,
    torch_dtype=torch.bfloat16
).to(device).eval()
processor = AutoProcessor.from_pretrained(model_path)
load_time = time.time() - start_load
print(f"Model loaded in {load_time:.1f}s\n")

def test_ocr(image_path: str) -> dict:
    """Run OCR on an image with 30s timeout."""
    print(f"Testing: {image_path}")
    print("-" * 40)
    
    signal.alarm(30)  # Set 30s timeout
    start = time.time()
    
    try:
        # Load image
        image = Image.open(image_path).convert("RGB")
        
        # Prepare inputs
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": "OCR:"},
                ]
            }
        ]
        
        min_pixels, max_pixels = 28 * 28, 1280 * 28 * 28
        inputs = processor.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
            images_kwargs={"size": {"shortest_edge": min_pixels, "longest_edge": max_pixels}},
        ).to(model.device)
        
        # Inference
        outputs = model.generate(**inputs, max_new_tokens=512)
        result = processor.decode(outputs[0][inputs["input_ids"].shape[-1]:-1])
        
        elapsed = time.time() - start
        signal.alarm(0)  # Cancel timeout
        
        # Show result preview (first 200 chars)
        preview = result[:200].replace('\n', ' ') if result else "(none)"
        print(f"Time: {elapsed:.1f}s | Preview: {preview}...")
        
        return {
            "success": bool(result.strip()),
            "text": result,
            "time": elapsed
        }
        
    except TimeoutError as e:
        signal.alarm(0)
        print(f"TIMEOUT: {e}")
        return {"success": False, "error": "timeout", "time": 30}
    except Exception as e:
        signal.alarm(0)
        print(f"ERROR: {e}")
        return {"success": False, "error": str(e), "time": 0}
    finally:
        signal.alarm(0)

# Test both images
print("=" * 50)
print("OCR TIMING TEST - CPU Only")
print("=" * 50)

test_images = ["test_image/test1.jpg", "test_image/test2.jpg"]
results = []

for img in test_images:
    try:
        res = test_ocr(img)
        results.append((img, res))
    except Exception as e:
        print(f"ERROR: {e}")
        results.append((img, {"success": False, "error": str(e), "time": 0}))

# Summary
print("\n" + "=" * 50)
print("SUMMARY")
print("=" * 50)
print(f"Model load time: {load_time:.1f}s")
for img, res in results:
    status = "✓" if res.get("success") else "✗"
    print(f"{status} {img}: {res.get('time', 0):.1f}s")
