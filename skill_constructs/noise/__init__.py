"""Noise skills for testing context interference."""

from pathlib import Path

NOISE_SKILLS_DIR = Path(__file__).parent

# List of noise skill names
NOISE_SKILLS = [
    "docker-patterns",
    "react-components",
    "api-docs",
    "database-migrations",
    "testing-patterns",
]
