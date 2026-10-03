from decimal import Decimal
import allure
import pytest

@pytest.mark.api
@pytest.mark.smoke
@pytest.mark.positive
@allure.epic("ParaBank API")
@allure.feature("Accounts")
@allure.story("Получение счета")
@allure.title("Получение существующего счета по ID")
def test_get_existing_acc(api_client, source_account):

    account_id = source_account["id"]

    allure.dynamic.parameter("account_id", account_id)

    with allure.step(f"Получить счет с ID{account_id}"):
        response = api_client.get_account(account_id=account_id)

    with allure.step(f"Проверить HTTP код"):
        assert response.status_code == 200, ("Не удалось получить счет",
         f"Ожидался код 200, "
         f"получен {response.status_code}. "
         )

    with allure.step(f"Проверить Content-type"):
        content_type = response.headers.get("Content-Type", "",).lower()

        assert "application/json" in content_type, (
            "Ожидался Json ответ",
            f"Получен Сontent-Type {content_type}",
            f"Ответ: {response.text}")

    with allure.step("Проверить данные счёта"):
        account = response.json()

        assert account["id"] == account_id
        assert account["customerId"] == (
            source_account["customerId"]
        )
        assert account["type"] == source_account["type"]

        assert Decimal(
            str(account["balance"])
        ) == Decimal(
            str(source_account["balance"])
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
            "несуществующий accountId в диапазоне int32",
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
            f"Получить счёт с accountId="
            f"{invalid_account_id!r}"
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
            f"URL: {response.request.url}. "
            f"Ответ: {response.text!r}"
        )