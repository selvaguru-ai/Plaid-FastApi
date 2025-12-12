import plaid
from plaid.api import plaid_api
from app.utils.config import settings


class PlaidClient:
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PlaidClient, cls).__new__(cls)
            cls._instance._initialize_client()
        return cls._instance

    def _initialize_client(self):
        # Validate settings before initializing client
        settings.validate()
        
        # Map environment string to Plaid Environment enum (only Sandbox/Production supported in plaid 28)
        env_map = {
            "sandbox": plaid.Environment.Sandbox,
            "production": plaid.Environment.Production,
        }

        environment = env_map.get(
            settings.PLAID_ENVIRONMENT.lower(), plaid.Environment.Sandbox
        )
        
        configuration = plaid.Configuration(
            host=environment,
            api_key={
                "clientId": settings.PLAID_CLIENT_ID,
                "secret": settings.PLAID_SECRET,
            }
        )

        api_client = plaid.ApiClient(configuration)
        self._client = plaid_api.PlaidApi(api_client)

    @property
    def client(self):
        return self._client


def get_plaid_client() -> plaid_api.PlaidApi:
    """Get the singleton Plaid client instance."""
    plaid_client = PlaidClient()
    return plaid_client.client
