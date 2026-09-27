# Project Overview
FastAPI microservice for processing payment transactions.

## Build & Test Commands
- Install dependencies: `pip install -r requirements.txt`
- Run local server: `uvicorn src.main:app --reload`
- Run test suite: `pytest -v tests/`
- Run linter/type-check: `ruff check . && mypy src/`

## Architecture & Conventions
- `src/api/`: Endpoint route definitions
- `src/services/`: Core business logic
- `src/schemas/`: Pydantic models for request/response validation

## Hard Rules
- Always use explicit Pydantic response models on FastAPI endpoints.
- Never hardcode environment variables; access via `src/config.py`.
- Run pytest before finalizing any file modifications.
