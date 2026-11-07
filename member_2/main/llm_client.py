"""
llm_client.py
-------------
Single place where the Groq API key and model name are read from the
.env file, so no module needs a hard-coded model or a client created
at import time.

.env must contain:
    GROQ_API_KEY=your_api_key
    GROQ_MODEL=openai/gpt-oss-20b
"""

import os

from dotenv import load_dotenv, find_dotenv
from groq import Groq

load_dotenv(find_dotenv())

_client = None


def get_model_name():
    """Return the model name configured in .env (GROQ_MODEL)."""

    model = os.getenv("GROQ_MODEL")

    if not model:
        raise ValueError("GROQ_MODEL is missing from your .env file.")

    return model


def get_client():
    """Return a shared Groq client built from GROQ_API_KEY in .env."""

    global _client

    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY is missing from your .env file.")

        _client = Groq(api_key=api_key)

    return _client
