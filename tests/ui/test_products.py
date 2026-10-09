from urllib.parse import urlparse
import allure
import pytest
from selenium.webdriver.support.ui import WebDriverWait
from src.ui.pages.home_page import HomePage


PRODUCTS_HOSTS = {
    "parasoft.com",
    "www.parasoft.com",
}


@pytest.mark.ui
@pytest.mark.regression
@pytest.mark.positive
@allure.epic("ParaBank UI")
@allure.feature("Navigation")
@allure.story("Products")
@allure.title(
    "Ссылка Products отображается и содержит корректный адрес"
)
def test_products_link_is_visible(driver):
    home_page = HomePage(driver)

    home_page.open()

    with allure.step("Проверить отображение ссылки Products"):
        assert home_page.is_products_link_visible(), (
            "Ссылка Products не отображается"
        )

    with allure.step("Проверить адрес ссылки Products"):
        products_url = home_page.get_products_href()

        assert products_url, (
            "У ссылки Products отсутствует href"
        )

        parsed_url = urlparse(products_url)

        assert parsed_url.scheme in {"http", "https"}, (
            "Ссылка Products использует некорректный протокол. "
            f"URL: {products_url}"
        )

        assert parsed_url.hostname in PRODUCTS_HOSTS, (
            "Ссылка Products ведёт на неожиданный ресурс. "
            f"URL: {products_url}. "
            f"Домен: {parsed_url.hostname!r}"
        )


@pytest.mark.ui
@pytest.mark.external
@pytest.mark.regression
@pytest.mark.positive
@allure.epic("ParaBank UI")
@allure.feature("Navigation")
@allure.story("Products")
@allure.title("Переход по ссылке Products")
def test_open_products_page(driver):
    home_page = HomePage(driver)

    home_page.open()

    products_url = home_page.get_products_href()
    url_before_click = driver.current_url

    assert products_url, (
        "У ссылки Products отсутствует href"
    )

    home_page.open_products()

    with allure.step("Дождаться перехода на ресурс Parasoft"):
        WebDriverWait(driver, 10).until(
            lambda browser: (
                browser.current_url != url_before_click
                and urlparse(browser.current_url).hostname
                in PRODUCTS_HOSTS
            ),
            message=(
                "После нажатия Products не выполнен "
                "переход на ожидаемый домен Parasoft. "
                f"Адрес ссылки: {products_url}"
            ),
        )

    with allure.step("Проверить адрес после перехода"):
        current_url = driver.current_url
        parsed_url = urlparse(current_url)

        assert parsed_url.scheme in {"http", "https"}, (
            "После перехода получен некорректный протокол. "
            f"URL: {current_url}"
        )

        assert parsed_url.hostname in PRODUCTS_HOSTS, (
            "После нажатия Products открыт неожиданный ресурс. "
            f"Адрес ссылки: {products_url}. "
            f"Текущий URL: {current_url}. "
            f"Домен: {parsed_url.hostname!r}"
        )