"""Claude API call: per-task insights plus an overall summary, in one request."""

import json
import logging
import os

import anthropic
from pydantic import BaseModel

logger = logging.getLogger(__name__)

MODEL = os.getenv("CLAUDE_MODEL", "claude-opus-5-5")
TIMEOUT_SECONDS = 30

SYSTEM_PROMPT = """You write short, plain-English insights for a business owner \
who is considering automating some of their recurring tasks.

You will receive a list of tasks with their annual time and cost figures, plus totals.
Return:
- task_insights: one insight per task, in the same order as the input. \
1-2 sentences each: what makes this task a good (or tricky) automation candidate \
and what the time saved could be used for.
- summary: 2-3 sentences tying the tasks together into an overall picture.

Rules:
- Only use the figures provided. Do not invent new numbers, percentages, or tools.
- No markdown, no bullet points, no headings. Plain sentences only.
- Confident and concrete, not salesy."""


class Narrative(BaseModel):
    task_insights: list[str]
    summary: str


def generate_narrative(tasks: list[dict], totals: dict, client=None) -> dict | None:
    """Return {"task_insights": [...], "summary": "..."}, or None if anything fails.

    `tasks` is a list of dicts with the task description and its calculated figures.
    Any failure (network, timeout, refusal, bad output) returns None so the
    caller can still show the numbers.
    """
    if client is None:
        client = anthropic.Anthropic(timeout=TIMEOUT_SECONDS, max_retries=0)

    payload = json.dumps({"tasks": tasks, "totals": totals}, indent=2)

    try:
        response = client.beta.messages.parse(
            model=MODEL,
            max_tokens=16000,
            output_config={"effort": "low"},
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": payload}],
            output_format=Narrative,
            # If a safety classifier declines, retry on Anthropic's recommended fallback model.
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
    except Exception as error:
        # Deliberately broad: a missing API key raises TypeError, not an API error,
        # and the calculator must keep working whatever goes wrong here.
        logger.warning("Claude call failed: %s", error)
        return None

    narrative = response.parsed_output
    if response.stop_reason == "refusal" or narrative is None:
        logger.warning("Claude returned no usable output (stop_reason=%s)", response.stop_reason)
        return None
    if len(narrative.task_insights) != len(tasks):
        logger.warning("Claude returned %d insights for %d tasks", len(narrative.task_insights), len(tasks))
        return None

    return narrative.model_dump()
