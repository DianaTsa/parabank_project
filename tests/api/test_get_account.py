from decimal import Decimal
import allure
import pytest


@pytest.mark.api
@pytest.mark.smoke
@pytest.mark.positive
@allure.epic("ParaBank API")
@allure.feature("Accounts")
@allure.story("Получение счёта")
@allure.title("Получение существующего счёта по ID")
def test_get_existing_acc(
    api_client,
    source_account,
):
    account_id = source_account["id"]

    allure.dynamic.parameter("account_id", account_id)

    with allure.step(f"Получить счёт с ID {account_id}"):
        response = api_client.get_account(
            account_id=account_id,
        )

    with allure.step("Проверить HTTP-код"):
        assert response.status_code == 200, (
            "Не удалось получить счёт. "
            "Ожидался код 200, "
            f"получен {response.status_code}. "
            f"Ответ: {response.text!r}"
        )

    with allure.step("Проверить Content-Type"):
        content_type = response.headers.get(
            "Content-Type",
            "",
        ).lower()

        assert "application/json" in content_type, (
            "Ожидался JSON-ответ. "
            f"Получен Content-Type: {content_type}. "
            f"Ответ: {response.text!r}"
        )

    with allure.step("Проверить данные счёта"):
        account = response.json()

        assert isinstance(account, dict), (
            f"Ожидался объект счёта: {account!r}"
        )

        assert account["id"] == account_id, (
            "В ответе указан другой ID счёта. "
            f"Ожидался: {account_id}. "
            f"Получен: {account['id']}."
        )

        assert account["customerId"] == (
            source_account["customerId"]
        ), (
            "Счёт принадлежит другому клиенту. "
            f"Ожидался: {source_account['customerId']}. "
            f"Получен: {account['customerId']}."
        )

        assert account["type"] == source_account["type"], (
            "Тип счёта не соответствует исходным данным. "
            f"Ожидался: {source_account['type']!r}. "
            f"Получен: {account['type']!r}."
        )

        actual_balance = Decimal(
            str(account["balance"])
        )
        expected_balance = Decimal(
            str(source_account["balance"])
        )

        assert actual_balance == expected_balance, (
            "Баланс не соответствует исходным данным. "
            f"Ожидался: {expected_balance}. "
            f"Получен: {actual_balance}."
        )


@pytest.mark.api
@pytest.mark.regression
@pytest.mark.negative
@allure.epic("ParaBank API")
@allure.feature("Accounts")
@allure.story("Валидация accountId")
@pytest.mark.parametrize(
    ("invalid_account_id", "case_description"),
    [
        pytest.param(
            2147483647,
            "предположительно несуществующий accountId",
            id="nonexistent-account-id",
        ),
        pytest.param(
            "invalid",
            "строка вместо числового accountId",
            id="string-account-id",
        ),
        pytest.param(
            "1.5",
            "дробное значение вместо целого accountId",
            id="float-account-id",
        ),
        pytest.param(
            2147483648,
            "accountId выше максимального значения int32",
            id="above-int32-max",
        ),
    ],
)
def test_get_account_with_invalid_id(
    api_client,
    invalid_account_id,
    case_description,
):
    allure.dynamic.title(
        "Получение счёта с некорректным accountId: "
        f"{case_description}"
    )

    allure.dynamic.parameter(
        "account_id",
        invalid_account_id,
    )

    with allure.step(
        f"Получить счёт с accountId={invalid_account_id!r}"
    ):
        response = api_client.get_account(
            account_id=invalid_account_id,
        )

    with allure.step(
        "Проверить, что сервер вернул клиентскую ошибку"
    ):
        assert 400 <= response.status_code < 500, (
            "Для некорректного accountId ожидалась "
            "ошибка класса 4xx. "
            f"AccountId: {invalid_account_id!r}. "
            f"Описание: {case_description}. "
            f"Получен код: {response.status_code}. "
            f"URL: {response.url}. "
            f"Ответ: {response.text!r}"
        )