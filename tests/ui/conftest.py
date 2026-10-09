from uuid import uuid4
import pytest
from faker import Faker
import allure
from src.ui.utils.driver_factory import create_driver


@pytest.fixture
def driver():
    browser = create_driver()

    yield browser

    browser.quit()

@pytest.fixture
def user_data():
    faker = Faker("en_US")
    suffix = uuid4().hex[:10]
    password = "TestPassword"

    return {
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
        "street": faker.street_address(),
        "city": faker.city(),
        "state": faker.state_abbr(),
        "zip_code": faker.postcode(),
        "phone_number": "5551234567",
        "ssn": faker.ssn(),
        "username": f"autotest_{suffix}",
        "password": password,
        "repeated_password": password,
    }

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    outcome = yield
    report = outcome.get_result()

    if report.when not in {"setup", "call"}:
        return
    if not report.failed:
        return
    driver = item.funcargs.get("driver")

    if driver is None:
        return
    try:
        allure.attach(driver.get_screenshot_as_png(), name=f"Screenshot - {item.name}",
                      attachment_type=allure.attachment_type.PNG )

        allure.attach(
            driver.page_source,
            name=f"Page source — {item.name}",
            attachment_type=(
                allure.attachment_type.HTML
            ),
        )

        allure.attach(
            driver.current_url,
            name="Current URL",
            attachment_type=(
                allure.attachment_type.TEXT
            ),
        )

    except Exception as error:
        allure.attach(
            str(error),
            name="Ошибка создания вложений",
            attachment_type=(
                allure.attachment_type.TEXT
            ),
        )