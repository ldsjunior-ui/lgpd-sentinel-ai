# Copyright 2024 LGPD Sentinel AI Contributors
# Licensed under the Apache License, Version 2.0

"""
Hybrid LLM provider factory — cascading fallback:
  1. Grok (xAI) — primary cloud provider
  2. Groq — free tier fallback (30 req/min)
  3. Ollama — local fallback (zero cost)

If the primary fails (429 rate limit, credits exhausted, timeout),
automatically tries the next provider in the chain.
"""

import logging

from src.core.config import get_settings

logger = logging.getLogger(__name__)


def _build_grok(settings, num_predict: int):
    """Build Grok (xAI) LLM client."""
    if not settings.XAI_API_KEY:
        return None
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        base_url="https://api.x.ai/v1",
        api_key=settings.XAI_API_KEY,
        model=settings.GROK_MODEL,
        temperature=settings.LLM_TEMPERATURE,
        max_tokens=num_predict,
        timeout=60,
        max_retries=1,
    )


def _build_groq(settings, num_predict: int):
    """Build Groq LLM client (free tier, OpenAI-compatible)."""
    if not settings.GROQ_API_KEY:
        return None
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=settings.GROQ_API_KEY,
        model=settings.GROQ_MODEL,
        temperature=settings.LLM_TEMPERATURE,
        max_tokens=num_predict,
        timeout=30,
        max_retries=1,
    )


def _build_ollama(settings, num_predict: int, num_ctx: int):
    """Build Ollama LLM client (local). Returns None if langchain_community not installed."""
    try:
        from langchain_community.llms import Ollama
        return Ollama(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            num_predict=num_predict,
            num_ctx=num_ctx,
        )
    except ImportError:
        logger.info("langchain_community not installed, Ollama fallback disabled")
        return None


class HybridLLM:
    """
    Cascading LLM that tries providers in order: Grok → Groq → Ollama.
    Falls through on any error (429, timeout, connection error).
    """

    def __init__(self, providers: list[tuple[str, object]]):
        self.providers = [(name, llm) for name, llm in providers if llm is not None]
        if not self.providers:
            raise RuntimeError("Nenhum LLM provider configurado. Configure XAI_API_KEY, GROQ_API_KEY, ou OLLAMA_BASE_URL no .env")

    async def ainvoke(self, prompt, **kwargs):
        """Try each provider in order. Return first successful response."""
        last_error = None
        for name, llm in self.providers:
            try:
                logger.info("Trying LLM provider: %s", name)
                result = await llm.ainvoke(prompt, **kwargs)
                # Normalize output: ChatOpenAI returns AIMessage, Ollama returns str
                if hasattr(result, "content"):
                    output = result.content
                else:
                    output = str(result)
                logger.info("LLM provider %s succeeded (%d chars)", name, len(output))
                return output
            except Exception as exc:
                last_error = exc
                logger.warning("LLM provider %s failed: %s — trying next", name, str(exc)[:200])
                continue

        raise RuntimeError(f"All LLM providers failed. Last error: {last_error}")


def get_llm(num_predict: int = 512, num_ctx: int = 2048):
    """
    Return a HybridLLM that cascades through available providers.

    The HybridLLM.ainvoke() always returns a plain string (not AIMessage),
    so callers don't need to handle .content extraction.

    Priority: Grok (xAI) → Groq (free) → Ollama (local)
    """
    settings = get_settings()

    providers = [
        ("grok", _build_grok(settings, num_predict)),
        ("groq", _build_groq(settings, num_predict)),
        ("ollama", _build_ollama(settings, num_predict, num_ctx)),
    ]

    hybrid = HybridLLM(providers)
    names = [name for name, llm in hybrid.providers]
    logger.info("HybridLLM initialized with providers: %s", " → ".join(names))
    return hybrid
