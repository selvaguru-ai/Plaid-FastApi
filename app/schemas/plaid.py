from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class LinkTokenRequest(BaseModel):
    user_id: str
    client_name: Optional[str] = "FastAPI Plaid Integration"


class LinkTokenResponse(BaseModel):
    link_token: str
    expiration: str


class ExchangeTokenRequest(BaseModel):
    public_token: str


class ExchangeTokenResponse(BaseModel):
    access_token: str
    item_id: str


class AccountBalance(BaseModel):
    available: Optional[float] = None
    current: Optional[float] = None
    limit: Optional[float] = None
    iso_currency_code: Optional[str] = None
    unofficial_currency_code: Optional[str] = None


class Account(BaseModel):
    account_id: str
    name: str
    official_name: Optional[str] = None
    type: str
    subtype: Optional[str] = None
    balances: AccountBalance


class Card(BaseModel):
    account_id: str
    name: str
    official_name: Optional[str] = None
    type: str
    subtype: Optional[str] = None
    balances: AccountBalance


class AccountsResponse(BaseModel):
    accounts: List[Account]
    cards: List[Card] = []


class TransactionLocation(BaseModel):
    address: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None


class Transaction(BaseModel):
    transaction_id: str
    account_id: str
    amount: float
    date: date
    name: str
    merchant_name: Optional[str] = None
    category: Optional[List[str]] = None
    location: Optional[TransactionLocation] = None
    payment_channel: str
    pending: bool


class TransactionsResponse(BaseModel):
    transactions: List[Transaction]
    total_transactions: int


