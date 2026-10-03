import allure

from selenium.webdriver.common.by import By

from src.ui.pages.base_page import BasePage

class HomePage(BasePage):
    REGISTER_LINK = (By.LINK_TEXT, "Register",)
    PRODUCTS_LINK = (By.LINK_TEXT, "Products")
    LOGIN_PANEL = (By.ID, "loginPanel")

    @allure.step("Открыть главную страницу ParaBank")
    def open(self):
        return super().open("/index.htm")

    def is_opened(self) -> bool:
        return (
                self.is_visible(self.LOGIN_PANEL)
                and self.is_visible(self.REGISTER_LINK)
        )

    @allure.step("Перейти к регистрации")
    def open_registration(self) -> None:
        self.click(self.REGISTER_LINK)

    def is_products_link_visible(self) -> bool:
        return self.is_visible(self.PRODUCTS_LINK)

    def get_products_href(self) -> str | None:
        return self.get_attribute(
            self.PRODUCTS_LINK,
            "href",
        )

    @allure.step("Открыть страницу Products")
    def open_products(self) -> None:
        self.click(self.PRODUCTS_LINK)

