from decimal import Decimal

import allure
import pytest


@pytest.mark.api
@pytest.mark.smoke
@pytest.mark.positive
@allure.epic("ParaBank API")
@allure.feature("Accounts")
@allure.story("Bill Pay")
@allure.title("Успешная оплата счёта")
def test_successful_bill_pay(
    api_client,
    source_account,
    payee_data,
):
    account_id = source_account["id"]
    amount = Decimal("1.00")

    print(f"Source Account ID: {account_id}")

    with allure.step(
        "Получить баланс счёта перед оплатой"
    ):
        account_before_response = api_client.get_account(
            account_id=account_id,
        )

        assert account_before_response.status_code == 200, (
            "Не удалось получить исходный счёт. "
            f"Код: {account_before_response.status_code}. "
            f"Ответ: {account_before_response.text}"
        )

        account_before = account_before_response.json()
        balance_before = Decimal(
            str(account_before["balance"])
        )

        assert balance_before >= amount, (
            "На счёте недостаточно средств для теста. "
            f"Баланс: {balance_before}, сумма: {amount}"
        )

    with allure.step(
        f"Оплатить счёт на сумму {amount}"
    ):
        response = api_client.bill_pay(
            account_id=account_id,
            amount=str(amount),
            payee=payee_data,
        )

    with allure.step("Проверить HTTP-код"):
        assert response.status_code == 200, (
            "Ожидался код 200, "
            f"получен {response.status_code}. "
            f"Ответ: {response.text}"
        )

    with allure.step("Проверить Content-Type"):
        content_type = response.headers.get(
            "Content-Type",
            "",
        )

        assert "application/json" in content_type, (
            "Ожидался JSON. "
            f"Получен Content-Type: {content_type}. "
            f"Ответ: {response.text}"
        )

    with allure.step(
        "Проверить результат операции Bill Pay"
    ):
        result = response.json()

        assert result["accountId"] == account_id
        assert Decimal(str(result["amount"])) == amount
        assert result["payeeName"] == payee_data["name"]

    with allure.step(
        "Получить баланс счёта после оплаты"
    ):
        account_after_response = api_client.get_account(
            account_id=account_id,
        )

        assert account_after_response.status_code == 200

        account_after = account_after_response.json()
        balance_after = Decimal(
            str(account_after["balance"])
        )

    with allure.step(
        "Проверить списание суммы со счёта"
    ):
        assert balance_after == balance_before - amount, (
            "Баланс изменился некорректно. "
            f"До оплаты: {balance_before}, "
            f"после оплаты: {balance_after}, "
            f"сумма: {amount}"
        )