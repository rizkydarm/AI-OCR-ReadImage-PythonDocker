# AI OCR Backend for n8n: Product Requirements Document

## 🎯 Project Overview
**Status**: Planned  
**Type**: Backend Microservice  
**Integration Target**: n8n Workflow Automation Platform  

### Executive Summary
Self-hostable FastAPI OCR microservice optimized for n8n workflows. Uses PaddleOCR-VL 1.5 for text extraction from images, tables, charts, formulas, and seals. Designed for zero-configuration deployment with a simple HTTP interface.

---

## ✅ Core Requirements

### Functional Requirements
| ID | Requirement | Priority |
|----|-------------|----------|
| FR1 | Accept `multipart/form-data` image uploads via POST `/ocr` | MUST |
| FR2 | Support 6 distinct OCR task modes: `ocr`, `table`, `chart`, `formula`, `spotting`, `seal` | MUST |
| FR3 | Return consistent JSON response with extracted text, task type, success flag and processing time | MUST |
| FR4 | Provide health check endpoint at GET `/health` that indicates model load status | MUST |
| FR5 | Fallback gracefully to CPU inference when CUDA is not available | MUST |
| FR6 | Support all common image formats: JPG, PNG, GIF, BMP, TIFF | SHOULD |

### Non-Functional Requirements
| ID | Requirement | Target |
|----|-------------|--------|
| NFR1 | Cold start time (first request) | < 10 seconds |
| NFR2 | Average OCR processing time per page | < 3 seconds on CPU, < 0.8s on GPU |
| NFR3 | Minimum RAM requirement | 2GB |
| NFR4 | Container image size | < 3GB |
| NFR5 | API uptime SLO | 99.5% |
| NFR6 | Parallel request handling | Minimum 4 concurrent requests |

---

## 🔌 API Specification

### POST `/ocr`
- **Headers**: `Content-Type: multipart/form-data`
- **Request Fields**:
  | Field | Type | Required | Description |
  |-------|------|----------|-------------|
  | `file` | Binary | ✅ | Image file |
  | `task` | String | ❌ | OCR mode (default: `ocr`) |

- **Response Schema**:
  ```json
  {
    "success": "boolean",
    "text": "string",
    "task": "string",
    "processing_time": "float (seconds)",
    "error": "string (only on failure)"
  }
  ```

### GET `/health`
Always returns HTTP 200:
```json
{
  "status": "healthy / initializing / error",
  "model_loaded": "boolean",
  "uptime": "float (seconds)"
}
```

---

## 🧪 Acceptance Criteria

### Deployment
- [ ] `uv sync` installs all dependencies without errors
- [ ] `uv run uvicorn app.main:app` starts server on port 8000
- [ ] Docker image builds successfully
- [ ] Container runs without privileged permissions
- [ ] Health endpoint returns `model_loaded: true` within 15 seconds

### Functionality
- [ ] Text is correctly extracted from standard test images
- [ ] All 6 task modes return valid responses
- [ ] Invalid files return proper error messages without crashing
- [ ] Large images (> 10MB) are processed correctly
- [ ] Concurrent requests are handled without deadlocks

### n8n Integration
- [ ] Works natively with n8n `HTTP Request` node
- [ ] Binary image data is accepted without preprocessing
- [ ] Response format is compatible with n8n JSON parsing
- [ ] No additional headers or authentication required by default

---

## 🚢 Deployment Targets
1. **Local Development**: `uv` virtual environment
2. **Self-hosted**: Docker / Docker Compose
3. **Cloud**: Kubernetes, Fly.io, Render, Railway
4. **n8n Embedded**: Optional bundled deployment

---

## 🚀 Out of Scope (v1.0)
- Authentication / API keys
- Rate limiting
- Batch processing
- Image preprocessing options
- Persistent storage / queueing
- Multi-language model selection
- Webhook callbacks

---

## 📅 Release Milestones
| Phase | Description | Target |
|-------|-------------|--------|
| M1 | Working FastAPI server with health endpoint | Week 1 |
| M2 | Basic OCR functionality implemented | Week 1 |
| M3 | All 6 task modes supported | Week 2 |
| M4 | Docker container optimized | Week 2 |
| M5 | n8n workflow template published | Week 3 |

---

## 💡 Success Metrics
- 90%+ accuracy on standard document OCR
- < 500ms average response time under load
- Zero crashes during 72 hour continuous operation
- Works with 10+ common n8n input nodes

---
