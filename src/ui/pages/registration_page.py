import allure
from selenium.webdriver.common.by import By
from src.ui.pages.base_page import BasePage


class RegistrationPage(BasePage):
    FIRST_NAME = (By.ID, "customer.firstName")
    LAST_NAME = (By.ID, "customer.lastName")
    STREET = (By.ID, "customer.address.street")
    CITY = (By.ID, "customer.address.city")
    STATE = (By.ID, "customer.address.state")
    ZIP_CODE = (By.ID, "customer.address.zipCode")
    PHONE_NUMBER = (By.ID, "customer.phoneNumber")
    SSN = (By.ID, "customer.ssn")
    USERNAME = (By.ID, "customer.username")
    PASSWORD = (By.ID, "customer.password")
    REPEATED_PASSWORD = (By.ID, "repeatedPassword")

    REGISTER_BUTTON = (
        By.CSS_SELECTOR,
        "input[value='Register']",
    )

    RIGHT_PANEL = (By.ID, "rightPanel")
    ERRORS = (By.CSS_SELECTOR,"#rightPanel span.error",)

    FIELD_LOCATORS = {
        "first_name": FIRST_NAME,
        "last_name": LAST_NAME,
        "street": STREET,
        "city": CITY,
        "state": STATE,
        "zip_code": ZIP_CODE,
        "phone_number": PHONE_NUMBER,
        "ssn": SSN,
        "username": USERNAME,
        "password": PASSWORD,
        "repeated_password": REPEATED_PASSWORD,
    }

    @allure.step("Открыть страницу регистрации")
    def open(self):
        return super().open("/register.htm")

    def is_opened(self) -> bool:
        return (
            "/register.htm" in self.current_url
            and self.is_visible(self.REGISTER_BUTTON)
        )

    @allure.step("Заполнить форму регистрации")
    def fill_form(
        self,
        user_data: dict,
    ) -> None:
        for field_name, locator in self.FIELD_LOCATORS.items():
            value = user_data.get(field_name, "")

            if value != "":
                self.input_text(locator, value)

    @allure.step("Отправить форму регистрации")
    def submit(self) -> None:
        self.click(self.REGISTER_BUTTON)

    @allure.step("Зарегистрировать пользователя")
    def register(
        self,
        user_data: dict,
    ) -> None:
        self.fill_form(user_data)
        self.submit()

    def get_page_message(self) -> str:
        return self.get_text(self.RIGHT_PANEL)

    def get_error_messages(self) -> list[str]:
        return [element.text.strip() for element in self.wait_all_visible(self.ERRORS)]