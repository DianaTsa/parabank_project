from urllib.parse import urlparse


import allure
import pytest
from src.ui.pages.home_page import HomePage

@pytest.mark.ui
@pytest.mark.regression
@pytest.mark.positive
@allure.epic("Parabank UI")
@allure.feature("Navigation")
@allure.story("Products")
@allure.title(
    "Ccылка отображается"
)
def test_products_link_is_visible(driver):
    home_page = HomePage(driver)

    with allure.step("Открыть главную страницу"):
        home_page.open()

    with allure.step("Проверить отображение ссылки"):
        assert home_page.is_products_link_visible()

    with allure.step("Проверить адрес ссылки"):
        products_url = (home_page.get_products_href())

        assert products_url, "Ccылка не содержит href"

        parsed_url = urlparse(products_url)

        assert parsed_url.scheme in {"http", "https",}

        assert parsed_url.netloc.endswith(
            "parasoft.com"
        ), (
            "Ссылка Products ведёт на неожиданный "
            f"ресурс: {products_url}"
        )

@pytest.mark.ui
@pytest.mark.external
@pytest.mark.regression
@pytest.mark.positive
@allure.epic("ParaBank UI")
@allure.feature("Navigation")
@allure.story("Products")
@allure.title(
    "Переход по ссылке Products"
)

def test_open_products_page(driver):
    home_page = HomePage(driver)


    home_page.open()

    products_url = home_page.get_products_href()

    with allure.step(
            "Нажать на ссылку Products"
    ):
        home_page.open_products()

    with allure.step("Проверить переход на страницу Parasoft"):
        current_url = driver.current_url
        current_domain = urlparse(current_url).netloc

        assert current_domain.endswith("parasoft.com"),(
            "После нажатия Products не выполнен "
            "переход на Parasoft. "
            f"Ожидаемая ссылка: {products_url}. "
            f"Текущий URL: {current_url}."
        )
