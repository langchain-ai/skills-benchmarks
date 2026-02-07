"""Model configuration for experiment evaluation.

Uses init_chat_model for flexible model initialization.
Supports format: "provider:model" (e.g., "openai:gpt-4o-mini", "anthropic:claude-3-sonnet")
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

# Load .env from project root
load_dotenv(Path(__file__).parent.parent / ".env")

# Default model for evaluation (fast, cheap)
# Format: "provider:model" or just "model" (defaults to openai)
EVAL_MODEL = os.getenv("EVAL_MODEL", "openai:gpt-4o-mini")


def get_eval_model(model: str = None, temperature: float = 0, max_tokens: int = 150):
    """Get the evaluation model using init_chat_model.

    Args:
        model: Model string (e.g., "openai:gpt-4o-mini"). Defaults to EVAL_MODEL.
        temperature: Model temperature
        max_tokens: Max tokens in response

    Returns:
        Initialized chat model
    """

    model = model or EVAL_MODEL
    return init_chat_model(model, temperature=temperature)


def evaluate_output(prompt: str, model: str = None) -> str:
    """Evaluate output using configured model.

    Args:
        prompt: The evaluation prompt
        max_tokens: Maximum tokens in response
        model: Optional model override

    Returns:
        Model response text
    """
    chat_model = get_eval_model(model=model)
    response = chat_model.invoke(prompt)
    return response.content


def evaluate_with_json(prompt: str, model: str = None) -> dict:
    """Evaluate and parse JSON response.

    Args:
        prompt: The evaluation prompt (should ask for JSON response)
        model: Optional model override

    Returns:
        Parsed JSON dict, or {"pass": False, "reason": "error"} on failure
    """
    import json

    try:
        text = evaluate_output(prompt, model=model)
        # Extract JSON from response
        if "{" in text and "}" in text:
            json_str = text[text.index("{"):text.rindex("}")+1]
            return json.loads(json_str)
        return {"pass": False, "reason": "no JSON in response"}
    except Exception as e:
        return {"pass": False, "reason": f"eval error: {str(e)[:30]}"}
