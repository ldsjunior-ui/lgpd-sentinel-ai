# Copyright 2024 LGPD Sentinel AI Contributors
# Licensed under the Apache License, Version 2.0

"""
LLM provider factory — supports Grok (xAI) and Ollama.
Grok uses the OpenAI-compatible xAI API; Ollama runs locally.
"""

import logging
from functools import lru_cache

from src.core.config import get_settings

logger = logging.getLogger(__name__)


def get_llm(num_predict: int = 512, num_ctx: int = 2048):
    """
    Return a LangChain LLM instance based on LLM_PROVIDER setting.

    - "grok": uses xAI API (OpenAI-compatible) — requires XAI_API_KEY
    - "ollama": uses local Ollama instance — requires OLLAMA_BASE_URL

    Both return objects supporting .ainvoke(prompt_str).
    """
    settings = get_settings()
    provider = settings.LLM_PROVIDER.lower()

    if provider == "grok":
        if not settings.XAI_API_KEY:
            raise RuntimeError(
                "XAI_API_KEY não configurada. Defina no .env para usar o Grok."
            )
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(
            base_url="https://api.x.ai/v1",
            api_key=settings.XAI_API_KEY,
            model=settings.GROK_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=num_predict,
        )
        logger.info("Using Grok (%s) via xAI API", settings.GROK_MODEL)
        return llm

    # Default: Ollama (local)
    from langchain_community.llms import Ollama

    llm = Ollama(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.OLLAMA_MODEL,
        temperature=settings.LLM_TEMPERATURE,
        num_predict=num_predict,
        num_ctx=num_ctx,
    )
    logger.info("Using Ollama (%s) at %s", settings.OLLAMA_MODEL, settings.OLLAMA_BASE_URL)
    return llm
