from fastapi import FastAPI
from app.routers import plaid

app = FastAPI(
    title="Plaid Integration API",
    description="FastAPI backend for Plaid integration - exchange tokens, fetch transactions, and fetch accounts/cards",
    version="1.0.0",
)

app.include_router(plaid.router)


@app.get("/")
def read_root():
    return {"message": "FastAPI Plaid Integration API is running!"}