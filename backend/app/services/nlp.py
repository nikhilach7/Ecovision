import asyncio
import logging
import os
import re
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from groq import APIConnectionError, APIStatusError, APITimeoutError, Groq

from app.core.config import settings

# Load backend/.env into os.environ so GROQ_API_KEY works even when only pydantic read it before.
_backend_root = Path(__file__).resolve().parents[2]
load_dotenv(_backend_root / ".env", override=False)

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an AI-powered Smart Waste Management Assistant for an IoT-based Smart Waste Segregation System.

You ONLY answer questions related to:
- Waste segregation (plastic, organic, metal, glass, e-waste)
- Smart bins and IoT monitoring
- Waste analytics and trends
- Recycling insights
- Bin fill levels
- City waste statistics
- Waste predictions and alerts

DO NOT answer unrelated queries.

Behavior rules:
- Keep answers concise and structured
- Use simple bullet points
- Use small paragraphs (2–3 lines max per section)
- Always format output clearly for UI readability
- If data is missing, generate realistic system-based insights
- Avoid long paragraphs and avoid markdown symbols like ** or ```"""

FALLBACK_MESSAGE = "SYSTEM ERROR:\n- Unable to process request\n- Please try again later"
OUT_OF_SCOPE_MESSAGE = (
    "I can only help with smart waste management topics like segregation, "
    "smart bins, analytics, recycling, and alerts."
)

# Groq deprecates model IDs periodically; keep supported IDs first (see Groq console deprecations).
GROQ_MODEL_FALLBACKS = (
    "llama-3.3-70b-versatile",
    "llama3-8b-8192",
)


def _api_key() -> str:
    return (settings.groq_api_key or os.getenv("GROQ_API_KEY", "") or "").strip()


def _sanitize_line(line: str) -> str:
    line = line.replace("•", "-")
    line = re.sub(r"[`#*_>{}\[\]]", "", line).strip()
    if not line:
        return ""
    if line.startswith("-"):
        content = line[1:].strip()
        return f"- {content}" if content else ""
    return line


def clean_text(text: str, max_chars: int = 1400) -> str:
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [_sanitize_line(line) for line in text.split("\n")]
    compact_lines: list[str] = []
    previous_blank = False
    for line in lines:
        if not line:
            if not previous_blank:
                compact_lines.append("")
            previous_blank = True
            continue
        compact_lines.append(line)
        previous_blank = False
    cleaned = "\n".join(compact_lines).strip()
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    if len(cleaned) > max_chars:
        cleaned = f"{cleaned[: max_chars - 3].rstrip()}..."
    return cleaned


class NLPService:
    def __init__(self) -> None:
        self.timeout_seconds = 45
        self._client: Groq | None = None
        self._client_key: str | None = None

    def _get_client(self) -> Groq | None:
        key = _api_key()
        if not key:
            return None
        if self._client is not None and self._client_key == key:
            return self._client
        self._client = Groq(api_key=key, timeout=self.timeout_seconds)
        self._client_key = key
        return self._client

    async def _request_completion(self, message: str, model: str) -> str:
        client = self._get_client()
        if client is None:
            raise RuntimeError("GROQ_API_KEY is not configured")

        response = await asyncio.wait_for(
            asyncio.to_thread(
                client.chat.completions.create,
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": message},
                ],
                temperature=0.4,
                max_tokens=600,
            ),
            timeout=self.timeout_seconds + 5,
        )
        if not response.choices:
            return ""
        content: Any = response.choices[0].message.content
        return content if isinstance(content, str) else str(content or "")

    async def _with_retry(self, message: str) -> str:
        last_error: Exception | None = None
        for model in GROQ_MODEL_FALLBACKS:
            for attempt in range(2):
                try:
                    return await self._request_completion(message, model)
                except (TimeoutError, asyncio.TimeoutError, APITimeoutError, APIConnectionError) as e:
                    last_error = e
                    if attempt == 0:
                        await asyncio.sleep(0.5)
                        continue
                    break
                except APIStatusError as e:
                    last_error = e
                    if e.status_code in (400, 404):
                        logger.warning("Groq model %s rejected: %s", model, e)
                        break
                    raise
                except Exception as e:
                    last_error = e
                    logger.exception("Groq request failed (model=%s)", model)
                    break
        if last_error:
            raise last_error
        raise RuntimeError("No Groq model succeeded")

    async def answer(self, db, query: str) -> tuple[str, str]:
        _ = db
        if not query or not query.strip():
            return "- Please enter a waste management related question.", "error"

        if not _api_key():
            logger.error("GROQ_API_KEY is empty; set it in backend/.env")
            return FALLBACK_MESSAGE, "error"

        try:
            raw = await self._with_retry(query.strip())
            cleaned = clean_text(raw)
            if not cleaned:
                logger.warning("Groq returned empty content after cleaning")
                return FALLBACK_MESSAGE, "error"
            if "I can only help" in cleaned:
                return OUT_OF_SCOPE_MESSAGE, "out_of_scope"
            return cleaned, "chatbot"
        except Exception as e:
            logger.exception("NLP chatbot failure: %s", e)
            return FALLBACK_MESSAGE, "error"

    async def chat(self, message: str) -> str:
        reply, _intent = await self.answer(None, message)
        return reply


nlp_service = NLPService()
