
from pathlib import Path

# Repository root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Shared directories
ASSETS_DIR = PROJECT_ROOT / "assets"
LEVELS_DIR = PROJECT_ROOT / "levels"
CONTENT_DIR = PROJECT_ROOT / "content"

# Game-specific resources
GAME_DIR = PROJECT_ROOT / "game"
GAME_MUSIC_DIR = GAME_DIR / "Music"

# Editor resources
EDITOR_DIR = PROJECT_ROOT / "editor"

# Project configuration
REQUIREMENTS_FILE = PROJECT_ROOT / "requirements.txt"
