import allure

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.settings import settings


class BasePage:
    def __init__(
        self,
        driver,
        base_url: str | None = None,
    ):
        self.driver = driver
        self.base_url = (
            base_url or settings.base_ui_url
        ).rstrip("/")

    def _wait(
        self,
        timeout: float | None = None,
    ):
        actual_timeout = (
            timeout
            if timeout is not None
            else settings.ui_timeout
        )

        return WebDriverWait(
            self.driver,
            actual_timeout,
        )

    @allure.step("Открыть страницу {path}")
    def open(self, path: str = ""):
        normalized_path = path.lstrip("/")

        if normalized_path:
            url = f"{self.base_url}/{normalized_path}"
        else:
            url = self.base_url

        self.driver.get(url)

        return self

    def wait_visible(
        self,
        locator,
        timeout: float | None = None,
    ):
        return self._wait(timeout).until(
            EC.visibility_of_element_located(
                locator
            )
        )

    def wait_all_visible(
        self,
        locator,
        timeout: float | None = None,
    ):
        return self._wait(timeout).until(
            EC.visibility_of_all_elements_located(
                locator
            )
        )

    def wait_clickable(
        self,
        locator,
        timeout: float | None = None,
    ):
        return self._wait(timeout).until(
            EC.element_to_be_clickable(
                locator
            )
        )

    @allure.step("Клик по элементу {locator}")
    def click(self, locator):
        self.wait_clickable(locator).click()

    @allure.step("Ввод текста в элемент {locator}")
    def input_text(
        self,
        locator,
        text,
    ):
        element = self.wait_visible(locator)
        element.clear()
        element.send_keys(str(text))

    def get_text(
        self,
        locator,
        timeout: float | None = None,
    ) -> str:
        element = self.wait_visible(
            locator,
            timeout,
        )

        return element.text.strip()

    def is_visible(
        self,
        locator,
        timeout: int = 10,
    ) -> bool:
        try:
            self.wait_visible(
                locator,
                timeout,
            )
            return True
        except TimeoutException:
            return False

    @property
    def current_url(self) -> str:
        return self.driver.current_url

    @property
    def title(self) -> str:
        return self.driver.title

    def get_attribute(
            self,
            locator,
            attribute: str,
            timeout: float | None = None,) -> str | None:
            element = self.wait_visible(
                locator,
                timeout,
        )
            return element.get_attribute(attribute)