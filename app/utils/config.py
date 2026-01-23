import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    PLAID_CLIENT_ID: str = os.getenv("PLAID_CLIENT_ID", "")
    PLAID_SECRET: str = os.getenv("PLAID_SECRET", "")
    PLAID_ENVIRONMENT: str = os.getenv("PLAID_ENVIRONMENT", "sandbox")

    def validate(self):
        """Validate that required settings are present."""
        if not self.PLAID_CLIENT_ID or not self.PLAID_SECRET:
            raise ValueError(
                "PLAID_CLIENT_ID and PLAID_SECRET must be set in environment variables. "
                "Create a .env file based on .env.example"
            )


settings = Settings()


