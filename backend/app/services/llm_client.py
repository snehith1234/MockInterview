import json
import re
from typing import Any, Dict, Optional
from openai import OpenAI

# Thread-local-like storage for per-request LLM settings
_current_api_key: Optional[str] = None
_current_model: Optional[str] = None


def set_llm_config(api_key: Optional[str], model: Optional[str]):
    """Set the LLM config for the current request."""
    global _current_api_key, _current_model
    _current_api_key = api_key
    _current_model = model


def get_llm_config():
    """Get the current LLM config (api_key, model)."""
    from app.config import OPENAI_API_KEY, LLM_MODEL
    api_key = _current_api_key or OPENAI_API_KEY
    model = _current_model or LLM_MODEL
    return api_key, model


def _get_client() -> Optional[OpenAI]:
    api_key, _ = get_llm_config()
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


def _extract_json(text: str) -> Dict[str, Any]:
    try:
        return json.loads(text)
    except Exception:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise ValueError(f"No JSON object found in LLM response: {text[:300]}")
        return json.loads(match.group(0))


def chat_text(system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
    client = _get_client()
    if not client:
        return "MOCK_LLM_ENABLED"

    _, model = get_llm_config()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
    )
    return response.choices[0].message.content or ""


def chat_json(system_prompt: str, user_prompt: str, temperature: float = 0.2) -> Dict[str, Any]:
    client = _get_client()
    if not client:
        return {}

    _, model = get_llm_config()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt + "\nReturn valid JSON only."},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
    )
    content = response.choices[0].message.content or "{}"
    return _extract_json(content)
