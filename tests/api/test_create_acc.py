import allure
import pytest

from src.api.account_type import AccountType


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
):
    customer_id = registered_customer["response"]["id"]
    source_account_id = source_account["id"]

    allure.dynamic.parameter("customer_id", customer_id)
    allure.dynamic.parameter(
        "source_account_id",
        source_account_id,
    )

    with allure.step("Создать новый сберегательный счёт"):
        response = api_client.create_account(
            customer_id=customer_id,
            new_account_type=AccountType.SAVINGS,
            from_account_id=source_account_id,
        )

    with allure.step("Проверить HTTP-код"):
        assert response.status_code == 200, (
            "Не удалось создать сберегательный счёт. "
            f"Ожидался код 200, "
            f"получен {response.status_code}. "
            f"Ответ: {response.text!r}"
        )

    with allure.step("Проверить Content-Type"):
        content_type = response.headers.get(
            "Content-Type",
            "",
        ).lower()

        assert "application/json" in content_type, (
            "Ожидался JSON. "
            f"Получен Content-Type: {content_type}. "
            f"Ответ: {response.text!r}"
        )

    with allure.step("Проверить данные нового счёта"):
        new_account = response.json()

        assert isinstance(new_account, dict), (
            f"Ожидался объект счёта: {new_account!r}"
        )

        assert new_account.get("id") is not None, (
            f"В ответе отсутствует ID счёта: {new_account}"
        )

        assert new_account["customerId"] == customer_id, (
            "Созданный счёт принадлежит другому клиенту. "
            f"Ожидался: {customer_id}. "
            f"Получен: {new_account['customerId']}."
        )

        assert new_account["id"] != source_account_id, (
            "ID нового и исходного счетов совпадают"
        )

        assert new_account["type"] == "SAVINGS", (
            "Создан счёт другого типа. "
            "Ожидался: SAVINGS. "
            f"Получен: {new_account['type']}."
        )

    with allure.step("Получить созданный счёт по ID"):
        saved_response = api_client.get_account(
            account_id=new_account["id"],
        )

        assert saved_response.status_code == 200, (
            "Созданный счёт не удалось получить. "
            f"Код: {saved_response.status_code}. "
            f"Ответ: {saved_response.text!r}"
        )

        saved_account = saved_response.json()

        assert saved_account["id"] == new_account["id"]
        assert saved_account["customerId"] == customer_id
        assert saved_account["type"] == "SAVINGS"