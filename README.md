# ManhwaForge AI — Mobile-ready Phase 1

A mobile-first installable web app (PWA) served by FastAPI. Open its URL in Android Chrome and use **Add to Home screen** to install it like an app. It currently supports project creation, TXT/PDF/DOCX upload, and AI story analysis. Image generation and chapter-to-panel production are not implemented yet.

## Fastest way to use on Android

This app needs a publicly reachable backend because AI calls must run on a server; do not put your OpenAI key in the Android app or browser.

1. Push this project folder to a private GitHub repository.
2. Create a Render account and use **New + → Blueprint**, selecting the repository. Render reads `render.yaml`.
3. Add your OpenAI API key as the `OPENAI_API_KEY` secret when prompted. Keep the key private.
4. Deploy. Wait until `/health` returns `{"status":"ok"...}`.
5. Open the deployed service URL in Chrome on Android.
6. Chrome menu → **Add to Home screen** (or **Install app**, if shown).

The Render blueprint provisions a web service and PostgreSQL database. Confirm current Render plan pricing and database availability before deploying; paid resources may be required. For a personal test, a local SQLite database is supported, but it is not suitable for a multi-instance production deployment.

## Local development

Requirements: Python 3.11+.

```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Set OPENAI_API_KEY in .env
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open `http://127.0.0.1:8000`. API docs: `/docs`.

## API endpoints

- `POST /api/v1/projects` JSON `{ "title": "My Novel", "art_style": "korean_fantasy" }`
- `POST /api/v1/projects/{project_id}/novels` multipart field `file`
- `POST /api/v1/projects/{project_id}/analyze`
- `GET /api/v1/projects/{project_id}`
- `GET /health`

## Current limits and safety

- Phase 1 supports TXT, text-based PDF and DOCX; scanned PDFs need OCR.
- Current story analysis sends at most 100,000 characters in one request. Phase 2 must chunk long novels and build durable chapter memory.
- This is an MVP: no user authentication, payment system, multi-user isolation, rate limiting, virus scanning, object storage, or background task queue yet. Do not upload private or sensitive documents to a public deployment.
- Render container disk is ephemeral unless a persistent disk is configured. For durable uploaded novels, configure persistent storage or implement private object storage (S3/R2) before relying on it.
- Keep API credentials on the server. Never commit `.env` or API keys.
- Character illustration, scene generation, panel editing, and finished chapter exports are future phases, not part of Phase 1.
