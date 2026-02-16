"""Shared fixtures for benchmark tests.

Includes noise task definitions for distractor experiments.
"""

from scaffold import NoiseTask

# =============================================================================
# NOISE TASKS
# =============================================================================

NOISE_TASKS = {
    "docker-patterns": {
        "prompt": "Create a Dockerfile for a Node.js application with multi-stage build, non-root user, and health check. Save to Dockerfile.nodejs.",
        "output": "Dockerfile.nodejs",
    },
    "react-components": {
        "prompt": "Create a React component that fetches and displays user data using hooks (useState, useEffect), with loading/error states in TypeScript. Save to UserProfile.tsx.",
        "output": "UserProfile.tsx",
    },
    "api-docs": {
        "prompt": "Create an OpenAPI spec for a simple user API with GET /users, POST /users, proper schemas, and error responses. Save to openapi.yaml.",
        "output": "openapi.yaml",
    },
}


def get_noise_task(name: str) -> NoiseTask:
    """Get a noise task by name."""
    data = NOISE_TASKS[name]
    return NoiseTask(prompt=data["prompt"], deliverables=[data["output"]])


def get_noise_tasks(names: list[str]) -> list[NoiseTask]:
    """Get multiple noise tasks by name."""
    return [get_noise_task(n) for n in names]
