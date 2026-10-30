# AI ROI Calculator

A small, client-facing tool that shows a prospect how much time and money they could save by automating their recurring tasks.

The prospect enters 3–5 tasks (a description, hours each time, how often, hourly rate). The app:

1. Calculates annualized time and cost savings for each task and in total.
2. Makes **one** Claude API call that returns a short insight for each task plus an overall summary.
3. Shows the results on a clean page built to screenshot well, with a shareable link.

If the Claude call fails or times out, the page still shows every number, with the message *"AI insights temporarily unavailable — here are your numbers."*

## Setup

Requires Python 3.10+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then put your Anthropic API key in .env
uvicorn main:app --reload
```

Open http://localhost:8000.

Run the tests (no API key needed — the Claude calls are mocked):

```bash
pytest
```

## How it works

| File | What it does |
|---|---|
| `config.py` | The calculation assumptions. The only file you need to edit to change the math. |
| `calculator.py` | The math: hours × frequency × rate, annualized, then the share saved by automation. |
| `narrator.py` | The single Claude API call. Returns the insights and summary, or `None` on any failure. |
| `main.py` | FastAPI app. `POST /api/calculate` validates input, runs the calculator, then the narrator. Also serves the frontend. |
| `static/index.html` | The whole frontend: input form, results page, share link. No framework. |
| `tests/` | Unit tests for the calculator, the narrator (Claude is mocked), and the API's fallback behaviour. |

### Shareable links

The full results (numbers and Claude's text) are JSON-encoded, then base64url-encoded into the URL's hash fragment: `/#r=eyJ0YXNr...`

- **No database.** The link *is* the data.
- **No backend call when viewing.** Browsers never send the `#...` part to the server, and the page decodes it locally.
- **Tradeoff:** anyone who opens a link can decode it, edit the numbers, and re-encode it. Treat shared results as a presentation, not a verified record. Preventing this would need a server-side signature check, which would break the "no backend on view" design.
- Because links can be edited, all decoded text is rendered as plain text (never as HTML).

## How to make it yours

Everything the math depends on lives in **`config.py`**:

```python
AUTOMATION_EFFICIENCY = 0.70
```
The share of each task's time that automation is assumed to save. 0.70 means automating a task removes 70% of the hours spent on it. Lower it for a more conservative pitch, raise it if your service typically does better. The results page shows this assumption to the prospect.

```python
FREQUENCY_PER_YEAR = {"daily": 260, "weekly": 52, "monthly": 12}
```
How many times a year each frequency happens. "Daily" uses 260 working days (52 weeks × 5 days). Change it to 365 if your prospects' tasks run every day of the week.

Other things you may want to change:

- **Claude model:** set `CLAUDE_MODEL` in `.env` (defaults to `claude-opus-5-5`).
- **Claude timeout:** `TIMEOUT_SECONDS` in `narrator.py` (default 30). After this, the page falls back to numbers only.
- **Tone of the insights:** edit `SYSTEM_PROMPT` in `narrator.py`.
- **Look and feel:** the colours are CSS variables at the top of `static/index.html`.
