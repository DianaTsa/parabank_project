import allure
import pytest

from src.api.account_type import AccountType
from tests.api.conftest import api_client

@pytest.mark.api
@pytest.mark.smoke
@pytest.mark.positive
@allure.epic("ParaBank API")
@allure.feature("Accounts")
@allure.story("Create account")
@allure.title("Успешное создание сберегательного счёта")
def test_create_savings_account(
    api_client,
    registered_customer,
    source_account,
created_account):
    customer_id = registered_customer["response"]["id"]
    source_account_id = source_account["id"]

    with allure.step(
        "Создать новый сберегательный счёт"
    ):
        response = api_client.create_account(
            customer_id=customer_id,
            new_account_type=AccountType.SAVINGS,
            from_account_id=source_account_id,
        )

    with allure.step("Проверить HTTP-код"):
        assert response.status_code == 200, (
            f"Ожидался код 200, "
            f"получен {response.status_code}. "
            f"Ответ: {response.text}"
        )

    with allure.step("Проверить Content-Type"):
        content_type = response.headers.get(
            "Content-Type",
            "",
        )

        assert "application/json" in content_type, (
            f"Ожидался JSON, получен {content_type}. "
            f"Ответ: {response.text}"
        )

    with allure.step("Проверить данные нового счёта"):
        created_account = response.json()

        assert created_account["id"] is not None
        assert created_account["customerId"] == customer_id

        assert created_account["id"] != source_account_id, (
            "ID нового и исходного счетов совпадают"
        )