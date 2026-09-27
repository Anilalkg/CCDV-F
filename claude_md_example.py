from pathlib import Path

# Define project context and conventions for Claude
CLAUDE_MD_CONTENT = """# Project Overview
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
"""


def generate_claude_md(target_dir: str = ".") -> None:
    """Generates a standard CLAUDE.md file at the repository root."""
    root_path = Path(target_dir)
    claude_file = root_path / "CLAUDE.md"

    # Write content to root CLAUDE.md
    claude_file.write_text(CLAUDE_MD_CONTENT, encoding="utf-8")
    print(f"Successfully generated project memory file at: {claude_file.resolve()}")


if __name__ == "__main__":
    generate_claude_md()