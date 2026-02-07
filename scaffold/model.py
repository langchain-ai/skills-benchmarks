"""Model configuration for experiment evaluation.

Uses init_chat_model for flexible model initialization.
Supports format: "provider:model" (e.g., "openai:gpt-4o-mini", "anthropic:claude-3-sonnet")
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

# Load .env from project root
load_dotenv(Path(__file__).parent.parent / ".env")

# Default model for evaluation (fast, cheap)
# Format: "provider:model" or just "model" (defaults to openai)
EVAL_MODEL = os.getenv("EVAL_MODEL", "openai:gpt-4o-mini")


class EvalResult(BaseModel):
    """Structured evaluation result."""
    passed: bool = Field(description="Whether the output meets expectations")
    reason: str = Field(description="Brief explanation (max 10 words)")


def get_eval_model(model: str = None, temperature: float = 0):
    """Get the evaluation model using init_chat_model.

    Args:
        model: Model string (e.g., "openai:gpt-4o-mini"). Defaults to EVAL_MODEL.
        temperature: Model temperature

    Returns:
        Initialized chat model
    """

    model = model or EVAL_MODEL
    return init_chat_model(model, temperature=temperature)


def evaluate_with_schema(prompt: str, model: str = None) -> dict:
    """Evaluate and return structured result using with_structured_output.

    Args:
        prompt: The evaluation prompt
        model: Optional model override

    Returns:
        Dict with "pass" (bool) and "reason" (str) keys
    """
    try:
        chat_model = get_eval_model(model=model)
        structured_model = chat_model.with_structured_output(EvalResult)
        result = structured_model.invoke(prompt)
        return {"pass": result.passed, "reason": result.reason}
    except Exception as e:
        return {"pass": False, "reason": f"eval error: {str(e)[:30]}"}
