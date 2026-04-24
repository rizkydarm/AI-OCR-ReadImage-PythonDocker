# AI OCR Backend for n8n: Product Requirements Document

## 🎯 Project Overview
**Status**: Planned  
**Type**: Backend Microservice  
**Integration Target**: n8n Workflow Automation Platform  

### Executive Summary
Self-hostable FastAPI OCR microservice optimized for n8n workflows. Uses OCR.space API as primary engine (fast cloud OCR) with EasyOCR as local fallback. Designed for reliable text extraction with automatic failover.

---

## ✅ Core Requirements

### Functional Requirements
| ID | Requirement | Priority |
|----|-------------|----------|
| FR1 | Accept `multipart/form-data` image uploads via POST `/ocr` | MUST |
| FR2 | Use OCR.space API as primary OCR engine | MUST |
| FR3 | Auto-fallback to EasyOCR when API unavailable/rate-limited | MUST |
| FR4 | Return JSON with extracted text, engine used, success flag, processing time | MUST |
| FR5 | Provide health check endpoint at GET `/health` with engine statuses | MUST |
| FR6 | Load API key from environment variable (OCR_SPACE_API_KEY) | MUST |

### Non-Functional Requirements
| ID | Requirement | Target |
|----|-------------|--------|
| NFR1 | OCR.space API response time | < 5 seconds |
| NFR2 | EasyOCR fallback processing time | < 60 seconds on CPU |
| NFR3 | Minimum RAM requirement | 512MB (API mode), 2GB (fallback mode) |
| NFR4 | Container image size | < 1GB |
| NFR5 | API uptime SLO | 99.5% |
| NFR6 | Parallel request handling | Minimum 4 concurrent requests |

---

## � Configuration

### Environment Variables
| Variable | Required | Description |
|----------|----------|-------------|
| `OCR_SPACE_API_KEY` | Yes | OCR.space API key (get free at https://ocr.space/OCRAPI) |

---

## � API Specification

### POST `/ocr`
- **Headers**: `Content-Type: multipart/form-data`
- **Request Fields**:
  | Field | Type | Required | Description |
  |-------|------|----------|-------------|
  | `file` | Binary | ✅ | Image file |

- **Response Schema**:
  ```json
  {
    "success": "boolean",
    "text": "string",
    "engine": "string (ocrspace | easyocr | none)",
    "processing_time": "float (seconds)",
    "error": "string (only on failure)"
  }
  ```

### GET `/health`
Always returns HTTP 200:
```json
{
  "status": "healthy / initializing / error",
  "engines": {
    "ocrspace": "available / unavailable",
    "easyocr": "available / unavailable"
  },
  "api_key_configured": "boolean",
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
- Multiple OCR task modes (table, chart, formula, etc.)
- Authentication / API keys for the backend itself
- Rate limiting
- Batch processing
- Image preprocessing options
- Persistent storage / queueing
- Multi-language selection
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
