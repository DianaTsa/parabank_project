import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def _is_true(value: str | None) -> bool:
    return str(value).lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def create_driver():
    options = Options()

    if _is_true(os.getenv("HEADLESS", "true")):
        options.add_argument("--headless=new")

    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    remote_url = os.getenv(
        "SELENIUM_REMOTE_URL",
        "",
    ).strip()

    if remote_url:
        return webdriver.Remote(
            command_executor=remote_url,
            options=options,
        )

    return webdriver.Chrome(options=options)