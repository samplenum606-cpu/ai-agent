# Autonomous EDA Agent Backend

This backend implements the Autonomous Data Science Agent core in Python using FastAPI.
It provides a sandboxed agent interface, Pydantic schemas, and a simple memory cache for data profiling.

## Available commands

- `python -m pip install -r requirements.txt` to install Python dependencies
- `uvicorn main:app --reload --host 0.0.0.0 --port 5000` to run the backend locally
- `docker build -t ai-agent-backend .` to build the Docker image
- `docker run -p 5000:5000 ai-agent-backend` to start the backend from Docker

## Recommended Python version

- Use Python **3.12.x** for local development.
- If you install Python locally, enable the `python` command on PATH.
- Docker users can rely on the provided `python:3.12-slim` image.

## API endpoints

- `GET /api/health` - health check
- `POST /api/agent` - run the EDA agent
- `GET /api/evaluate` - run evaluation on multiple benchmark datasets

## Design notes

- The backend uses `schemas.py` for Pydantic request and response models.
- The agent lifecycle is implemented in `agent_engine.py`.
- `datasets/sample.csv` is the default dataset for development and testing.
- The Dockerfile builds a contained Python environment for safe execution.
