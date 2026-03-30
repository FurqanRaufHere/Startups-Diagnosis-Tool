import json
import re
import logging
from typing import Type, TypeVar
from groq import Groq
from pydantic import BaseModel, ValidationError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from db import settings

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

client = Groq(api_key=settings.groq_api_key)

MODEL = "llama-3.3-70b-versatile"


def _extract_json(text: str) -> str:
    # Strip markdown fences Llama loves to add
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    # Find first { to last } — handles leading prose
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError(f"No JSON object found in response: {text[:200]}")
    return text[start:end]


def call_llm(system_prompt: str, user_prompt: str, schema: Type[T], max_tokens: int = 2048) -> T:
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ValueError, ValidationError)),
        reraise=True,
    )
    def _call_with_retry(error_context: str = "") -> T:
        full_system = (
            f"{system_prompt}\n\n"
            f"CRITICAL: Respond ONLY with a valid JSON object matching this schema:\n"
            f"{json.dumps(schema.model_json_schema(), indent=2)}\n"
            f"No markdown, no explanation, no text before or after the JSON."
        )

        messages = [{"role": "user", "content": user_prompt}]
        if error_context:
            messages.append({
                "role": "user",
                "content": f"Your previous response failed validation: {error_context}. Try again with valid JSON only."
            })

        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": full_system}, *messages],
            max_tokens=max_tokens,
            temperature=0.1,  # Low temp for structured output
        )

        raw = response.choices[0].message.content
        logger.debug(f"Raw LLM response: {raw[:500]}")

        cleaned = _extract_json(raw)
        parsed = json.loads(cleaned)
        return schema.model_validate(parsed)

    return _call_with_retry()