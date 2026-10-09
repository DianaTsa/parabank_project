import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

def get_bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)

    if value is None:
        return default
    return value.strip().lower() in {
        "1", "true", "yes", "on",
    }

@dataclass(frozen=True)
class Settings:
    base_api_url: str = os.getenv("BASE_API_URL", "https://parabank.parasoft.com/parabank/services/bank",)
    base_ui_url: str = os.getenv(
        "BASE_UI_URL",
        "https://parabank.parasoft.com/parabank",)

    browser: str = os.getenv("BROWSER", "chrome")
    headless: bool = get_bool_env("HEADLESS", False,)
    selenium_remote_url: str = os.getenv(
        "SELENIUM_REMOTE_URL", "",
    )
    ui_timeout: float = float(
        os.getenv("UI_TIMEOUT", "10"),

    )

    api_timeout: float = float(os.getenv("API_TIMEOUT", "15"))






settings = Settings()
