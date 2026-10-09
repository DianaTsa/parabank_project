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
    funded_account,
    payee_data,
):
    account_id = funded_account["id"]
    amount = Decimal("1.00")

    allure.dynamic.parameter("account_id", account_id)
    allure.dynamic.parameter("amount", str(amount))

    with allure.step("Получить баланс счёта перед оплатой"):
        account_before_response = api_client.get_account(
            account_id=account_id,
        )

        assert account_before_response.status_code == 200, (
            "Не удалось получить счёт перед оплатой. "
            f"Код: {account_before_response.status_code}. "
            f"Ответ: {account_before_response.text!r}"
        )

        account_before = account_before_response.json()
        balance_before = Decimal(
            str(account_before["balance"])
        )

        assert balance_before >= amount, (
            "На счёте недостаточно средств для теста. "
            f"Баланс: {balance_before}. "
            f"Сумма платежа: {amount}."
        )

    with allure.step(f"Оплатить счёт на сумму {amount}"):
        response = api_client.bill_pay(
            account_id=account_id,
            amount=str(amount),
            payee=payee_data,
        )

    with allure.step("Проверить HTTP-код"):
        assert response.status_code == 200, (
            "Ожидался код 200, "
            f"получен {response.status_code}. "
            f"URL: {response.url}. "
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

    with allure.step("Проверить результат операции Bill Pay"):
        result = response.json()

        assert result["accountId"] == account_id, (
            "В ответе указан другой счёт. "
            f"Ожидался: {account_id}. "
            f"Получен: {result['accountId']}."
        )

        assert Decimal(str(result["amount"])) == amount, (
            "В ответе указана другая сумма. "
            f"Ожидалась: {amount}. "
            f"Получена: {result['amount']}."
        )

        assert result["payeeName"] == payee_data["name"], (
            "В ответе указан другой получатель. "
            f"Ожидался: {payee_data['name']!r}. "
            f"Получен: {result['payeeName']!r}."
        )

    with allure.step("Получить баланс счёта после оплаты"):
        account_after_response = api_client.get_account(
            account_id=account_id,
        )

        assert account_after_response.status_code == 200, (
            "Не удалось получить счёт после оплаты. "
            f"Код: {account_after_response.status_code}. "
            f"Ответ: {account_after_response.text!r}"
        )

        account_after = account_after_response.json()
        balance_after = Decimal(
            str(account_after["balance"])
        )

    with allure.step("Проверить списание суммы со счёта"):
        expected_balance = balance_before - amount

        assert balance_after == expected_balance, (
            "Баланс изменился некорректно. "
            f"До оплаты: {balance_before}. "
            f"Сумма платежа: {amount}. "
            f"Ожидаемый баланс: {expected_balance}. "
            f"Фактический баланс: {balance_after}."
        )