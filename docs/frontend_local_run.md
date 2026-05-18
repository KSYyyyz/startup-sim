# Frontend Alpha 0.1 Local Runbook

## Install

From the repository root:

```bash
pip install -r requirements.txt
cd frontend
npm install
npx playwright install chromium
```

## Run Locally

Terminal 1, from the repository root:

```bash
python -m uvicorn src.api.app:app --host 127.0.0.1 --port 8000
```

Terminal 2, from `frontend/`:

```bash
npm run dev -- --port 5173
```

Open:

```text
http://127.0.0.1:5173
```

## Verify

From the repository root:

```bash
pytest tests/test_frontend_api.py
python scripts/check_docs_consistency.py
```

From `frontend/`:

```bash
npm test -- --run
npm run build
npm run test:e2e
```

The E2E suite runs both desktop and mobile viewport checks.
