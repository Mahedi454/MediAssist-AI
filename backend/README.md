# Backend

FastAPI backend for the AI Healthcare Chatbot.

## Local Development

Create a virtual environment, install dependencies, then run the app:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Swagger docs will be available at:

- `http://localhost:8000/docs`
- `http://localhost:8000/redoc`

## Development Database

After PostgreSQL is running and `.env` is configured, create the initial tables:

```bash
python scripts/create_tables.py
```
