# AI OCR Backend for n8n

FastAPI backend service that extracts text from images using PaddleOCR-VL. Designed for seamless integration with n8n workflows.

**Workflow**: Image → FastAPI Backend → Extracted Text (JSON)

## Architecture

```
┌─────────┐    HTTP POST     ┌─────────────┐    PaddleOCR-VL    ┌────────┐
│   n8n   │ ───────────────→ │  FastAPI    │ ─────────────────→ │  Text  │
│         │   (image file)   │   Backend   │                    │ Output │
└─────────┘                  └─────────────┘                    └────────┘
                                    │
                                    ↓
                              JSON Response
                           { "text": "..." }
```

## Planned API Endpoints

### `POST /ocr`
Extract text from an uploaded image.

**Request**: `multipart/form-data`
- `file`: Image file (JPG, PNG, etc.)
- `task` (optional): OCR task type - `ocr` (default), `table`, `chart`, `formula`, `spotting`, `seal`

**Response**: `application/json`
```json
{
  "success": true,
  "text": "Extracted text content...",
  "task": "ocr",
  "processing_time": 1.23
}
```

### `GET /health`
Health check endpoint for monitoring.

**Response**:
```json
{
  "status": "healthy",
  "model_loaded": true
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
- **PaddleOCR-VL 1.5** - Vision-language OCR model
- **Transformers** - Hugging Face inference
- **Uvicorn** - ASGI server
- **Docker** - Containerization
- **uv** - Fast Python package manager

## Supported OCR Tasks

| Task | Description |
|------|-------------|
| `ocr` | General text recognition (default) |
| `table` | Table structure recognition |
| `chart` | Chart/graph recognition |
| `formula` | Mathematical formula recognition |
| `spotting` | Text spotting/detection |
| `seal` | Seal/stamp recognition |

## Requirements

- Python 3.12+
- 2GB+ RAM recommended for OCR model
- CUDA optional (falls back to CPU)
