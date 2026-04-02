#!/usr/bin/env python3
"""
Shared AI caller for Chronicler.
Supports OpenRouter and local Ollama.
Reads settings from environment (set by /settings endpoint).
"""

import os
import json
from typing import List, Dict, Optional


def get_settings() -> Dict:
    """Read current AI settings from environment."""
    return {
        "provider": os.environ.get("AI_PROVIDER", "openrouter"),
        "openrouter_api_key": os.environ.get("OPENROUTER_API_KEY", ""),
        "openrouter_model": os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
        "ollama_url": os.environ.get("OLLAMA_URL", "http://localhost:11434"),
        "ollama_model": os.environ.get("OLLAMA_MODEL", "gemma3:12b"),
    }


async def call_ai(
    messages: List[Dict],
    temperature: float = 0.7,
    max_tokens: int = 1000,
) -> str:
    """
    Call the configured AI provider with a list of messages.
    Returns the assistant's response text.
    Raises Exception on failure.
    """
    import aiohttp

    settings = get_settings()
    provider = settings["provider"]

    if provider == "ollama":
        return await _call_ollama(messages, settings, temperature, max_tokens)
    else:
        return await _call_openrouter(messages, settings, temperature, max_tokens)


async def _call_openrouter(
    messages: List[Dict],
    settings: Dict,
    temperature: float,
    max_tokens: int,
) -> str:
    import aiohttp

    api_key = settings["openrouter_api_key"]
    if not api_key:
        raise Exception(
            "No OpenRouter API key configured. Go to Settings to add your key."
        )

    model = settings["openrouter_model"]
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:3050",
                "X-Title": "Chronicler - Etheria Writing Companion",
            },
            json={
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
            timeout=aiohttp.ClientTimeout(total=120),
        ) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise Exception(f"OpenRouter error ({resp.status}): {text[:300]}")
            result = await resp.json()
            return result["choices"][0]["message"]["content"]


async def _call_ollama(
    messages: List[Dict],
    settings: Dict,
    temperature: float,
    max_tokens: int,
) -> str:
    import aiohttp

    ollama_url = settings["ollama_url"].rstrip("/")
    model = settings["ollama_model"]
    if not model:
        raise Exception("No Ollama model configured. Go to Settings to select a model.")

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{ollama_url}/api/chat",
            json={
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            },
            timeout=aiohttp.ClientTimeout(total=120),
        ) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise Exception(f"Ollama error ({resp.status}): {text[:300]}")
            result = await resp.json()
            return result["message"]["content"]


async def list_ollama_models(ollama_url: str = "http://localhost:11434") -> List[str]:
    """List available models from a running Ollama instance."""
    import aiohttp

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{ollama_url.rstrip('/')}/api/tags",
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []


async def test_provider() -> Dict:
    """Test the currently configured AI provider."""
    settings = get_settings()
    provider = settings["provider"]

    try:
        response = await call_ai(
            [{"role": "user", "content": "Say OK"}],
            max_tokens=5,
        )
        return {
            "success": True,
            "provider": provider,
            "model": settings.get(f"{provider}_model", ""),
            "message": f"{provider.title()} connection works",
        }
    except Exception as e:
        return {
            "success": False,
            "provider": provider,
            "message": str(e),
        }
