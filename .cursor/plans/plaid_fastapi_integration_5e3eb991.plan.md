---
name: Plaid FastAPI Integration
overview: Create a FastAPI backend with Plaid integration endpoints for link token creation, token exchange, fetching transactions, and fetching accounts/cards. All endpoints will be accessible via Swagger UI for testing.
todos:
  - id: add-dependencies
    content: Add plaid-python to requirements.txt
    status: completed
  - id: create-config
    content: Create config utility and .env.example for Plaid credentials
    status: completed
  - id: create-plaid-client
    content: Create Plaid client utility with singleton pattern
    status: completed
  - id: create-schemas
    content: Create Pydantic schemas for request/response models
    status: completed
  - id: create-router
    content: Create plaid router with all 4 endpoints (link-token, exchange-token, transactions, accounts)
    status: completed
  - id: update-main
    content: Update main.py to include router and configure Swagger UI
    status: completed
---

# Plaid FastAPI Integration Backend

## Overview

Implement a FastAPI backend with Plaid integration endpoints. The backend will support link token creation, public token exchange, transaction fetching, and account/card retrieval.

## Implementation Details

### 1. Dependencies

- Add `plaid-python` to `requirements.txt`
- Existing dependencies (fastapi, pydantic, python-dotenv, uvicorn) are sufficient

### 2. Configuration

- Create `.env.example` file with Plaid credentials template:
  - `PLAID_CLIENT_ID`
  - `PLAID_SECRET`
  - `PLAID_ENVIRONMENT` (sandbox)
- Create config utility in `app/utils/config.py` to load environment variables

### 3. Plaid Client Utility

- Create `app/utils/plaid_client.py`:
  - Initialize Plaid client with credentials from config
  - Singleton pattern for client instance

### 4. Pydantic Schemas

Create request/response models in `app/schemas/plaid.py`:

- `LinkTokenRequest` - user_id for link token creation
- `LinkTokenResponse` - link_token
- `ExchangeTokenRequest` - public_token
- `ExchangeTokenResponse` - access_token, item_id
- `TransactionsResponse` - transactions list with metadata
- `AccountsResponse` - accounts and cards list

### 5. API Router

Create `app/routers/plaid.py` with endpoints:

- `POST /api/plaid/link-token` - Create link token for Plaid Link initialization
- `POST /api/plaid/exchange-token` - Exchange public token for access token
- `GET /api/plaid/transactions` - Fetch transactions (requires access_token query param, optional date range)
- `GET /api/plaid/accounts` - Fetch accounts and cards (requires access_token query param)

### 6. Error Handling

- Add proper exception handling for Plaid API errors
- Return appropriate HTTP status codes and error messages
- Use FastAPI's HTTPException for error responses

### 7. Main Application

- Update `app/main.py`:
  - Include plaid router
  - Add title and description for Swagger UI
  - Configure CORS if needed (optional for now)

## File Structure

```
app/
├── main.py (updated)
├── routers/
│   └── plaid.py (new)
├── schemas/
│   └── plaid.py (new)
└── utils/
    ├── config.py (new)
    └── plaid_client.py (new)
requirements.txt (updated)
.env.example (new)
```

## Testing

All endpoints will be accessible via Swagger UI at `/docs` for manual testing. Endpoints will accept proper request bodies and query parameters as defined in the schemas.