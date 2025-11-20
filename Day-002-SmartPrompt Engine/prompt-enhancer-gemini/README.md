# Prompt Enhancer — Gemini + Heuristics

Prompt Enhancer is a small Streamlit app that helps you improve and format prompts for large language models. It uses a local heuristic enhancer as a reliable fallback and Google Gemini (via the `google-generativeai` SDK) when an API key and quota are available.

Key goals:
- Make prompts clearer, more specific, and better-structured for downstream LLM use
- Support file uploads (text, PDF, Word, images) to extract prompt content
- Handle Gemini API quota and response quirks gracefully (retry, model rotation, heuristic fallback)

**Repository layout**
- `app.py` — Streamlit front-end and main app logic
- `enhancer/prompt_enhancer.py` — Heuristic prompt analysis & suggestions (works offline)
- `utils/gemini_client.py` — Gemini API wrapper with retries, model rotation, and robust response extraction
- `scripts/` — Utility scripts (`list_gemini_models.py`, `inspect_response.py`, `test_response_extraction.py`)

## Features
- Enhance prompts in different modes: Basic, Detailed, Creative, Technical
- Upload `.txt`, `.pdf`, `.docx`, and image files to extract text for enhancement
- Configurable temperature and `max_tokens` (defaults to 1,000,000 but adjustable)
- Automatic handling for common Gemini failures (404 model not found, 429 quota). Falls back to local heuristics if needed.

## Requirements
- Python 3.10+ (a virtualenv is recommended)
- Install dependencies from `requirements.txt`

## Quickstart (Windows PowerShell)
Clone the repo and create a virtual environment:

```powershell
git clone <repo-url> prompt-enhancer-gemini
cd "prompt-enhancer-gemini"
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a `.env` file in the project root or set the environment variables. Minimal `.env` example:

```
GEMINI_API_KEY=YOUR_API_KEY_HERE
GEMINI_MODEL_NAME=models/gemini-2.5-flash
```

You can also set the env var for the current PowerShell session:

```powershell
$env:GEMINI_API_KEY = 'YOUR_API_KEY_HERE'
```

Run the app:

```powershell
python -m streamlit run prompt-enhancer-gemini/app.py
# or (from repo root)
python -m streamlit run app.py
```

Then open: http://localhost:8501

## Usage
- Paste or type a prompt into the main text area or upload a file to pre-fill it.
- Choose an enhancement mode from the sidebar (Basic, Detailed, Creative, Technical).
- Adjust `Temperature` and `Max tokens` as needed.
- Click `Enhance` to send the prompt to Gemini (if configured) or to run the local heuristic enhancer.

The app stores recent enhancements in session history during the browser session.

## Configuration and Notes
- `GEMINI_API_KEY`: required to call Gemini. Without it, the app uses the local heuristic enhancer only.
- `GEMINI_MODEL_NAME`: defaults to `models/gemini-2.5-flash`. If that model is not available in your account, use the provided script to list models.
- `Max tokens`: the app allows very large values but be mindful of model limits and quota.

## Helpful scripts
- `scripts/list_gemini_models.py` — List models available to your account. Use it when you get a `404 model not found` error.
- `scripts/inspect_response.py` — Inspect raw SDK responses to debug parsing issues.
- `scripts/test_response_extraction.py` — Unit-style utility to validate response parsing logic in `utils/gemini_client.py`.

## Troubleshooting
- 404 model not found: run `python scripts/list_gemini_models.py` and update `GEMINI_MODEL_NAME` in `.env`.
- 429 quota / rate limit: The client implements retry-and-rotate logic. If you still see failures, wait for the quota window to reset or use a different model/key.
- `st.secrets` missing: the app gracefully falls back to `.env` and a sidebar manual key input. If you see errors, ensure `GEMINI_API_KEY` is set in one of those places.
- Unsupported Streamlit functions: older Streamlit versions may lack some UI helpers. The app targets Streamlit 1.29.0; if you see `AttributeError`, upgrade Streamlit or let me know to adjust the UI code.

## Development notes
- To tune retry/backoff or the model-rotation behavior, edit `utils/gemini_client.py` (search for `_generate_with_retries`).
- The heuristic enhancer is intentionally independent of the Gemini SDK — it provides a predictable fallback when the API is unavailable.

## Contributing
PRs welcome. Open issues for bugs or feature requests. Keep changes focused and include tests where appropriate.

## License
This project is provided as-is. Add a license file (e.g., `MIT`) if you plan to publish it on GitHub.

---
If you'd like, I can also add a short GIF or screenshot demonstrating the app, or generate a concise `CONTRIBUTING.md` and `LICENSE` for the repo.
