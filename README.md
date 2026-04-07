# Limit API (FastAPI)

REST API version of the mock card-limit MCP server.

## Endpoints

- `GET /accounts` → Get all accounts/cards with current and temporary limits
- `GET /cards/default/limits` → Get limits for default card (`CARD-001`)
- `GET /cards/{card_id}/limits` → Get limits for a specific card
- `PATCH /cards/{card_id}/limits/{limit_type}` → Change a permanent limit (`pos`, `atm`, `ecom`)
- `POST /cards/{card_id}/temporary-limits/{limit_type}` → Create temporary limit (`pos`, `atm`, `ecom`)

## Run locally

```bash
cd /home/milad/Projects/limit-api
uv sync
uv run uvicorn main:app --reload --host 0.0.0.0 --port 2010
```

Open Swagger UI:

- `http://127.0.0.1:2010/docs`

## Example requests

```bash
curl http://127.0.0.1:2010/accounts

curl http://127.0.0.1:2010/cards/default/limits

curl -X PATCH http://127.0.0.1:2010/cards/CARD-001/limits/pos \
  -H "Content-Type: application/json" \
  -d '{"limit":1500}'

curl -X POST http://127.0.0.1:2010/cards/CARD-001/temporary-limits/atm \
  -H "Content-Type: application/json" \
  -d '{"limit":1200,"startDate":"2026-03-02","endDate":"2026-03-07"}'
```
