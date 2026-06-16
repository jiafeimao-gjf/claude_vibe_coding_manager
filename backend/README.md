# Backend

Python virtual environment is created at `backend/venv/`. Do NOT check it in.

## Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
source venv/bin/activate
uvicorn app.main:app --reload --port 9453
```

## Test

```bash
source venv/bin/activate
pytest -v
```
