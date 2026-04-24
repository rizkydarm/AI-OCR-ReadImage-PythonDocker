# AI OCR Backend for n8n

FastAPI backend service that extracts text from images using OCR.space API (primary) with EasyOCR fallback. Designed for seamless integration with n8n workflows.

**Workflow**: Image → FastAPI Backend → Extracted Text (JSON)

## Architecture

```
Image → FastAPI Backend → OCR.space API → Text (2.5s)
                                ↓ (if rate limited)
                        EasyOCR Fallback → Text (15-30s)
```

## API Endpoints

### `POST /ocr`
Extract text from an uploaded image.

**Request**: `multipart/form-data`
- `file`: Image file (JPG, PNG, etc.)

**Response**: `application/json`
```json
{
  "success": true,
  "text": "Extracted text content...",
  "engine": "ocrspace",
  "processing_time": 2.5
}
```

### `GET /health`
Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "engines": {
    "ocrspace": "available",
    "easyocr": "available"
  },
  "api_key_configured": true
}
```

## Quick Start

### Local Development (uv)

```bash
# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate

# Run development server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Deployment

```bash
# Build image
docker build -t ai-ocr-backend .

# Run container
docker run -p 8000:8000 ai-ocr-backend
```

## Testing with curl

```bash
# OCR endpoint
curl -X POST http://localhost:8000/ocr \
  -F "file=@test_image/test1.jpg" \
  -F "task=ocr"

# Health check
curl http://localhost:8000/health
```

## n8n Integration

Configure an **HTTP Request** node in n8n:

- **Method**: POST
- **URL**: `http://your-backend:8000/ocr`
- **Body**: Form-Data
  - `file`: Binary data (image from previous node)
  - `task`: `ocr` (or other supported task)

The response JSON will contain the extracted text in the `text` field.

## Technology Stack

- **FastAPI** - Modern async web framework
- **OCR.space API** - Cloud OCR engine (primary)
- **EasyOCR** - Local OCR engine (fallback)
- **Uvicorn** - ASGI server
- **Docker** - Containerization
- **uv** - Fast Python package manager

## OCR Engines

| Engine | Speed | Reliability | Use Case |
|--------|-------|-------------|----------|
| **OCR.space API** | ~2.5s | Requires API key & internet | Primary (fast, accurate) |
| **EasyOCR** | ~15-30s | Works offline | Fallback (no rate limits) |

## Requirements

- Python 3.12+
- OCR_SPACE_API_KEY environment variable
- 512MB+ RAM (API mode) or 2GB+ (fallback mode)
- Internet connection for primary OCR engine
