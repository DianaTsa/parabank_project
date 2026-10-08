import allure
import pytest
from src.ui.pages.home_page import HomePage
from src.ui.pages.registration_page import RegistrationPage


@pytest.mark.ui
@pytest.mark.smoke
@pytest.mark.positive
@allure.epic("ParaBank UI")
@allure.feature("Registration")
@allure.story("Registration page")
@allure.title("Открытие страницы регистрации")
def test_registration_page_is_opened(driver):
    registration_page = RegistrationPage(driver)

    registration_page.open()

    with allure.step("Проверить отображение формы регистрации"):
        assert registration_page.is_opened(), (
            "Страница регистрации не открылась. "
            f"Текущий URL: {driver.current_url}"
        )


@pytest.mark.ui
@pytest.mark.smoke
@pytest.mark.positive
@allure.epic("ParaBank UI")
@allure.feature("Registration")
@allure.story("Registration navigation")
@allure.title("Переход на регистрацию с главной страницы")
def test_open_registration_from_home_page(driver):
    home_page = HomePage(driver)
    registration_page = RegistrationPage(driver)

    home_page.open()

    with allure.step("Проверить открытие главной страницы"):
        assert home_page.is_opened(), (
            "Главная страница не открылась. "
            f"Текущий URL: {driver.current_url}"
        )

    home_page.open_registration()

    with allure.step("Проверить открытие страницы регистрации"):
        assert registration_page.is_opened(), (
            "После нажатия Register страница "
            "регистрации не открылась. "
            f"Текущий URL: {driver.current_url}"
        )


@pytest.mark.ui
@pytest.mark.smoke
@pytest.mark.positive
@allure.epic("ParaBank UI")
@allure.feature("Registration")
@allure.story("Successful registration")
@allure.title("Успешная регистрация нового пользователя")
def test_successful_registration(
    driver,
    user_data,
):
    registration_page = RegistrationPage(driver)

    allure.dynamic.parameter(
        "username",
        user_data["username"],
    )

    registration_page.open()
    registration_page.register(user_data)

    with allure.step("Проверить успешную регистрацию"):
        message = registration_page.get_page_message()

        assert user_data["username"] in message, (
            "Username отсутствует на странице после регистрации. "
            f"Ожидался: {user_data['username']!r}. "
            f"Текст страницы: {message!r}"
        )

        assert "Your account was created successfully" in message, (
            "ParaBank не подтвердил успешную регистрацию. "
            f"Текст страницы: {message!r}"
        )


@pytest.mark.ui
@pytest.mark.regression
@pytest.mark.negative
@allure.epic("ParaBank UI")
@allure.feature("Registration")
@allure.story("Registration validation")
@allure.title("Отправка пустой формы регистрации")
def test_registration_with_empty_form(driver):
    registration_page = RegistrationPage(driver)

    registration_page.open()
    registration_page.submit()

    with allure.step("Проверить сообщения об ошибках"):
        errors = registration_page.get_error_messages()

        expected_errors = [
            "First name is required.",
            "Last name is required.",
            "Username is required.",
            "Password is required.",
            "Password confirmation is required.",
        ]

        for expected_error in expected_errors:
            assert expected_error in errors, (
                f"Не найдена ошибка: {expected_error!r}. "
                f"Фактические ошибки: {errors}"
            )


@pytest.mark.ui
@pytest.mark.regression
@pytest.mark.negative
@allure.epic("ParaBank UI")
@allure.feature("Registration")
@allure.story("Required fields validation")
@pytest.mark.parametrize(
    ("missing_field", "expected_error"),
    [
        pytest.param(
            "first_name",
            "First name is required.",
            id="without-first-name",
        ),
        pytest.param(
            "last_name",
            "Last name is required.",
            id="without-last-name",
        ),
        pytest.param(
            "username",
            "Username is required.",
            id="without-username",
        ),
        pytest.param(
            "password",
            "Password is required.",
            id="without-password",
        ),
        pytest.param(
            "repeated_password",
            "Password confirmation is required.",
            id="without-password-confirmation",
        ),
    ],
)
def test_registration_without_required_field(
    driver,
    user_data,
    missing_field,
    expected_error,
):
    allure.dynamic.title(
        f"Регистрация без обязательного поля: {missing_field}"
    )
    allure.dynamic.parameter(
        "missing_field",
        missing_field,
    )

    registration_page = RegistrationPage(driver)

    invalid_user_data = user_data.copy()
    invalid_user_data[missing_field] = ""

    registration_page.open()
    registration_page.register(invalid_user_data)

    with allure.step("Проверить сообщение валидации"):
        errors = registration_page.get_error_messages()

        assert expected_error in errors, (
            f"Не найдена ошибка: {expected_error!r}. "
            f"Фактические ошибки: {errors}"
        )