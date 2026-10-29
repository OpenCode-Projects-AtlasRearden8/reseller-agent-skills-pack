"""Tiny OpenAI-compatible chat client with no API key by default.

Defaults to a local Ollama server (http://localhost:11434/v1). Works offline
in the sense that it never calls the internet for anything except the base
URL you give it; if the endpoint is unreachable it raises a plain error.
"""

from __future__ import annotations

import json
import urllib.request
import urllib.error

DEFAULT_BASE_URL = "http://localhost:11434/v1"
DEFAULT_MODEL = "llama3.1:8b"


class LlmError(RuntimeError):
    pass


def chat(
    prompt: str,
    *,
    base_url: str = DEFAULT_BASE_URL,
    model: str = DEFAULT_MODEL,
    system: str | None = None,
    api_key: str | None = None,
    timeout: float = 60.0,
    temperature: float = 0.4,
    max_chars: int = 4000,
) -> str:
    """One-shot chat completion against an OpenAI-compatible /chat/completions."""
    if api_key:
        raise LlmError(
            "API keys are not used in this pack by design. Use a local, keyless "
            "OpenAI-compatible server (e.g. Ollama)."
        )
    url = base_url.rstrip("/") + "/chat/completions"
    messages: list[dict] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise LlmError(
            f"Could not reach the LLM endpoint at {url} ({exc.reason}). "
            "This pack works offline — every deterministic tool runs without it. "
            "For drafts, start a local server, e.g.:  ollama serve"
        ) from exc
    except TimeoutError as exc:
        raise LlmError(f"LLM endpoint timed out after {timeout}s.") from exc

    try:
        content = body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise LlmError(f"Unexpected response shape from {url}: {body}") from exc
    return str(content)[:max_chars]
