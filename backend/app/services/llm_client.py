import json
import re
from typing import Any, Dict, Optional
from openai import OpenAI

# Per-request LLM settings
_current_api_key: Optional[str] = None
_current_model: Optional[str] = None

# Models that don't support temperature parameter
NO_TEMPERATURE_MODELS = {"gpt-5.5", "gpt-5", "gpt-5-mini"}


RESPONSES_API_MODELS = {"gpt-5.5", "gpt-5.4-mini", "gpt-5.4", "gpt-5.4-nano", "gpt-5-mini", "gpt-5"}


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


def _uses_responses_api(model: str) -> bool:
    """Check if the model uses the newer Responses API."""
    return model in RESPONSES_API_MODELS


def _extract_json(text: str) -> Dict[str, Any]:
    try:
        return json.loads(text)
    except Exception:
        pass

    # Try to find a JSON object in the text
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object found in LLM response: {text[:300]}")

    json_str = match.group(0)

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        pass

    # Fix invalid escape sequences (e.g., \S, \d, \w from regex in LLM output)
    # Replace invalid escapes with double backslash
    fixed = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', json_str)
    try:
        return json.loads(fixed)
    except json.JSONDecodeError:
        pass

    # Last resort: try to parse with strict=False
    try:
        return json.loads(json_str, strict=False)
    except json.JSONDecodeError:
        pass

    try:
        return json.loads(fixed, strict=False)
    except json.JSONDecodeError as e:
        raise ValueError(f"Could not parse JSON from LLM response: {str(e)}\nContent: {text[:500]}")


def chat_text(system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
    client = _get_client()
    if not client:
        return "MOCK_LLM_ENABLED"

    _, model = get_llm_config()

    try:
        if _uses_responses_api(model):
            # GPT-5 family — use Responses API
            kwargs = {
                "model": model,
                "instructions": system_prompt,
                "input": user_prompt,
            }
            if model not in NO_TEMPERATURE_MODELS:
                kwargs["temperature"] = temperature
            response = client.responses.create(**kwargs)
            return response.output_text or ""
        else:
            # GPT-4 and older — use Chat Completions API
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
            )
            return response.choices[0].message.content or ""
    except Exception as e:
        # If Responses API fails, try Chat Completions as fallback
        if _uses_responses_api(model):
            try:
                fallback_kwargs = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                }
                if model not in NO_TEMPERATURE_MODELS:
                    fallback_kwargs["temperature"] = temperature
                response = client.chat.completions.create(**fallback_kwargs)
                return response.choices[0].message.content or ""
            except Exception:
                pass
        raise Exception(f"LLM call failed for model '{model}': {str(e)}")


def chat_json(system_prompt: str, user_prompt: str, temperature: float = 0.2) -> Dict[str, Any]:
    client = _get_client()
    if not client:
        return {}

    _, model = get_llm_config()

    try:
        if _uses_responses_api(model):
            # GPT-5 family — use Responses API
            kwargs = {
                "model": model,
                "instructions": system_prompt + "\nReturn valid JSON only.",
                "input": user_prompt,
            }
            if model not in NO_TEMPERATURE_MODELS:
                kwargs["temperature"] = temperature
            response = client.responses.create(**kwargs)
            content = response.output_text or "{}"
        else:
            # GPT-4 and older — use Chat Completions API
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt + "\nReturn valid JSON only."},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
            )
            content = response.choices[0].message.content or "{}"
    except Exception as e:
        # If Responses API fails, try Chat Completions as fallback
        if _uses_responses_api(model):
            try:
                fallback_kwargs = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt + "\nReturn valid JSON only."},
                        {"role": "user", "content": user_prompt},
                    ],
                }
                if model not in NO_TEMPERATURE_MODELS:
                    fallback_kwargs["temperature"] = temperature
                response = client.chat.completions.create(**fallback_kwargs)
                content = response.choices[0].message.content or "{}"
            except Exception:
                raise Exception(f"LLM call failed for model '{model}': {str(e)}")
        else:
            raise Exception(f"LLM call failed for model '{model}': {str(e)}")

    return _extract_json(content)
