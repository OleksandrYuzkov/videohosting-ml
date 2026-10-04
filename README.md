# Video Hosting ML Service

Machine learning service providing semantic video search, steerable recommendations, and audience analytics.

---

## Quickstart (Docker)

Run the containerized service:

```bash
docker run -d -p 8000:8000 --name ml-service ghcr.io/oleksandryuzkov/videohosting-ml:latest
```

Or add it to your `docker-compose.yml`:

```yaml
services:
  ml-service:
    image: ghcr.io/oleksandryuzkov/videohosting-ml:latest
    ports:
      - "8000:8000"
    restart: unless-stopped
```

Interactive API documentation and schema specifications are available at:  
`http://localhost:8000/docs`

---

## Local Development

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Run linters and tests:
   ```bash
   uv run ruff check .
   uv run pytest
   ```

3. Start development server:
   ```bash
   uv run uvicorn src.api.main:app --reload
   ```

---

## Tech Stack

- Python 3.12, FastAPI, Uvicorn, Pydantic v2
- PyTorch (CUDA 12.4), Scikit-Learn
- uv, Docker, GitHub Actions CI/CD
