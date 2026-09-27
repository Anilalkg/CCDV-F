import json
from pathlib import Path

# Define configuration payload with lifecycle hooks
claude_config = {
    "hooks": {
        # Triggered automatically right after Claude edits or creates a file
        "post-edit": [
            {
                "matcher": "*.py",
                "command": "ruff format {file_path}"
            }
        ]
    }
}


def setup_claude_hooks(project_root: str = ".") -> None:
    """Configures lifecycle event hooks in .claude/config.json."""
    config_dir = Path(project_root) / ".claude"
    config_dir.mkdir(exist_ok=True)

    config_file = config_dir / "config.json"

    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(claude_config, f, indent=2)

    print(f"Successfully created Claude Code hook configuration at: {config_file.resolve()}")


if __name__ == "__main__":
    setup_claude_hooks()