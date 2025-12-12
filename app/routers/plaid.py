from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta, date
from typing import Optional
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.country_code import CountryCode
from plaid.model.products import Products
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.accounts_get_request import AccountsGetRequest

from app.schemas.plaid import (
    LinkTokenRequest,
    LinkTokenResponse,
    ExchangeTokenRequest,
    ExchangeTokenResponse,
    TransactionsResponse,
    AccountsResponse,
    Transaction,
    Account,
    Card,
    AccountBalance,
    TransactionLocation,
)
from app.utils.plaid_client import get_plaid_client

router = APIRouter(prefix="/api/plaid", tags=["plaid"])


def convert_enum_to_string(value):
    """Convert Plaid enum objects to strings."""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    # Try to get the value attribute (common for enums)
    if hasattr(value, 'value'):
        return str(value.value)
    # Fallback to string conversion
    return str(value)


@router.post("/link-token", response_model=LinkTokenResponse)
async def create_link_token(request: LinkTokenRequest):
    """
    Create a link token for Plaid Link initialization.
    This token is used on the frontend to initialize Plaid Link.
    """
    try:
        client = get_plaid_client()

        link_token_request = LinkTokenCreateRequest(
            products=[Products("transactions")],
            client_name=request.client_name,
            country_codes=[CountryCode("US")],
            language="en",
            user=LinkTokenCreateRequestUser(client_user_id=request.user_id),
        )

        response = client.link_token_create(link_token_request)
        # Handle both dict and object responses
        link_token = response.get("link_token") if isinstance(response, dict) else response.link_token
        expiration = response.get("expiration") if isinstance(response, dict) else response.expiration
        
        # Convert datetime to ISO format string if it's a datetime object
        if isinstance(expiration, datetime):
            expiration = expiration.isoformat()
        elif expiration and not isinstance(expiration, str):
            expiration = str(expiration)
        
        return LinkTokenResponse(
            link_token=link_token,
            expiration=expiration,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create link token: {str(e)}")


@router.post("/exchange-token", response_model=ExchangeTokenResponse)
async def exchange_token(request: ExchangeTokenRequest):
    """
    Exchange a public token for an access token.
    The public token is received from Plaid Link after user authentication.
    """
    try:
        client = get_plaid_client()

        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=request.public_token
        )

        response = client.item_public_token_exchange(exchange_request)
        # Handle both dict and object responses
        access_token = response.get("access_token") if isinstance(response, dict) else response.access_token
        item_id = response.get("item_id") if isinstance(response, dict) else response.item_id
        return ExchangeTokenResponse(
            access_token=access_token,
            item_id=item_id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to exchange token: {str(e)}"
        )


@router.get("/transactions", response_model=TransactionsResponse)
async def get_transactions(
    access_token: str = Query(..., description="Plaid access token"),
    start_date: Optional[date] = Query(
        None, description="Start date for transactions (YYYY-MM-DD)"
    ),
    end_date: Optional[date] = Query(
        None, description="End date for transactions (YYYY-MM-DD)"
    ),
):
    """
    Fetch transactions for an account.
    If dates are not provided, defaults to last 30 days.
    """
    try:
        client = get_plaid_client()

        # Default to last 30 days if dates not provided
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).date()
        if not end_date:
            end_date = datetime.now().date()

        transactions_request = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date,
        )

        response = client.transactions_get(transactions_request)
        # Handle both dict and object responses
        transactions_data = response.get("transactions") if isinstance(response, dict) else response.transactions
        total_transactions = response.get("total_transactions") if isinstance(response, dict) else response.total_transactions

        # Convert Plaid transactions to our schema
        transactions = []
        for txn in transactions_data:
            # Handle both dict and object responses
            if isinstance(txn, dict):
                location_data = txn.get("location")
                transaction_id = txn.get("transaction_id")
                account_id = txn.get("account_id")
                amount = txn.get("amount")
                date_val = txn.get("date")
                name = txn.get("name")
                merchant_name = txn.get("merchant_name")
                category = txn.get("category")
                payment_channel = txn.get("payment_channel")
                pending = txn.get("pending")
            else:
                location_data = txn.location if hasattr(txn, "location") else None
                transaction_id = txn.transaction_id
                account_id = txn.account_id
                amount = txn.amount
                date_val = txn.date
                name = txn.name
                merchant_name = getattr(txn, "merchant_name", None)
                category = getattr(txn, "category", None)
                payment_channel = txn.payment_channel
                pending = txn.pending
            
            # Convert enum objects to strings if needed
            payment_channel = convert_enum_to_string(payment_channel)

            location = None
            if location_data:
                if isinstance(location_data, dict):
                    location = TransactionLocation(
                        address=location_data.get("address"),
                        city=location_data.get("city"),
                        region=location_data.get("region"),
                        postal_code=location_data.get("postal_code"),
                        country=location_data.get("country"),
                        lat=location_data.get("lat"),
                        lon=location_data.get("lon"),
                    )
                else:
                    location = TransactionLocation(
                        address=getattr(location_data, "address", None),
                        city=getattr(location_data, "city", None),
                        region=getattr(location_data, "region", None),
                        postal_code=getattr(location_data, "postal_code", None),
                        country=getattr(location_data, "country", None),
                        lat=getattr(location_data, "lat", None),
                        lon=getattr(location_data, "lon", None),
                    )

            transactions.append(
                Transaction(
                    transaction_id=transaction_id,
                    account_id=account_id,
                    amount=amount,
                    date=date_val,
                    name=name,
                    merchant_name=merchant_name,
                    category=category,
                    location=location,
                    payment_channel=payment_channel,
                    pending=pending,
                )
            )

        return TransactionsResponse(
            transactions=transactions,
            total_transactions=total_transactions,
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to fetch transactions: {str(e)}"
        )


@router.get("/accounts", response_model=AccountsResponse)
async def get_accounts(
    access_token: str = Query(..., description="Plaid access token"),
):
    """
    Fetch accounts and cards for an item.
    Returns both regular accounts and credit card accounts.
    """
    try:
        client = get_plaid_client()

        accounts_request = AccountsGetRequest(access_token=access_token)
        response = client.accounts_get(accounts_request)
        # Handle both dict and object responses
        accounts_data = response.get("accounts") if isinstance(response, dict) else response.accounts

        accounts = []
        cards = []

        for acc in accounts_data:
            # Handle both dict and object responses
            if isinstance(acc, dict):
                balances_data = acc.get("balances", {})
                account_id = acc.get("account_id")
                name = acc.get("name")
                official_name = acc.get("official_name")
                acc_type = acc.get("type")
                subtype = acc.get("subtype")
            else:
                balances_data = acc.balances if hasattr(acc, "balances") else {}
                account_id = acc.account_id
                name = acc.name
                official_name = getattr(acc, "official_name", None)
                acc_type = acc.type
                subtype = getattr(acc, "subtype", None)
            
            # Convert enum objects to strings if needed
            acc_type = convert_enum_to_string(acc_type)
            subtype = convert_enum_to_string(subtype)

            if isinstance(balances_data, dict):
                balance = AccountBalance(
                    available=balances_data.get("available"),
                    current=balances_data.get("current"),
                    limit=balances_data.get("limit"),
                    iso_currency_code=balances_data.get("iso_currency_code"),
                    unofficial_currency_code=balances_data.get("unofficial_currency_code"),
                )
            else:
                balance = AccountBalance(
                    available=getattr(balances_data, "available", None),
                    current=getattr(balances_data, "current", None),
                    limit=getattr(balances_data, "limit", None),
                    iso_currency_code=getattr(balances_data, "iso_currency_code", None),
                    unofficial_currency_code=getattr(balances_data, "unofficial_currency_code", None),
                )

            account_obj = Account(
                account_id=account_id,
                name=name,
                official_name=official_name,
                type=acc_type,
                subtype=subtype,
                balances=balance,
            )

            # Separate credit cards from regular accounts
            if acc_type == "credit" or (
                subtype and "credit" in subtype.lower()
            ):
                cards.append(
                    Card(
                        account_id=account_id,
                        name=name,
                        official_name=official_name,
                        type=acc_type,
                        subtype=subtype,
                        balances=balance,
                    )
                )
            else:
                accounts.append(account_obj)

        return AccountsResponse(accounts=accounts, cards=cards)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to fetch accounts: {str(e)}"
        )
