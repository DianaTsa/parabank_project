from decimal import Decimal

import allure
import pytest


@pytest.mark.api
@pytest.mark.regression
@pytest.mark.positive
@allure.epic("ParaBank API")
@allure.feature("Accounts")
@allure.story("Withdraw")
@pytest.mark.parametrize(
    "withdraw_amount",
    [
        pytest.param(
            Decimal("0.01"),
            id="withdraw-minimal-amount",
        ),
        pytest.param(
            Decimal("1.00"),
            id="withdraw-one",
        ),
        pytest.param(
            Decimal("5.00"),
            id="withdraw-five",
        ),
    ],
)
def test_successful_withdraw(
    api_client,
    funded_account,
    withdraw_amount,
):
    account_id = funded_account["id"]

    allure.dynamic.title(
        f"Успешное снятие {withdraw_amount} "
        f"со счёта {account_id}"
    )
    allure.dynamic.parameter("account_id", account_id)
    allure.dynamic.parameter(
        "withdraw_amount",
        str(withdraw_amount),
    )

    with allure.step("Получить баланс перед снятием"):
        before_response = api_client.get_account(
            account_id=account_id,
        )

        assert before_response.status_code == 200, (
            "Не удалось получить счёт перед снятием. "
            f"Код: {before_response.status_code}. "
            f"Ответ: {before_response.text!r}"
        )

        balance_before = Decimal(
            str(before_response.json()["balance"])
        )

        assert balance_before >= withdraw_amount, (
            f"Недостаточно средств: баланс {balance_before}, "
            f"сумма снятия {withdraw_amount}."
        )

    with allure.step(f"Снять {withdraw_amount} со счёта"):
        withdraw_response = api_client.withdraw(
            account_id=account_id,
            amount=str(withdraw_amount),
        )

        assert withdraw_response.status_code == 200, (
            "Withdraw завершился с ошибкой. "
            f"Код: {withdraw_response.status_code}. "
            f"Ответ: {withdraw_response.text!r}"
        )

    with allure.step("Получить баланс после снятия"):
        after_response = api_client.get_account(
            account_id=account_id,
        )

        assert after_response.status_code == 200, (
            "Не удалось получить счёт после снятия. "
            f"Код: {after_response.status_code}. "
            f"Ответ: {after_response.text!r}"
        )

        balance_after = Decimal(
            str(after_response.json()["balance"])
        )

    with allure.step("Проверить списание суммы"):
        expected_balance = balance_before - withdraw_amount

        assert balance_after == expected_balance, (
            "Баланс изменился некорректно. "
            f"До: {balance_before}; "
            f"снято: {withdraw_amount}; "
            f"ожидалось: {expected_balance}; "
            f"получено: {balance_after}."
        )


@pytest.mark.api
@pytest.mark.regression
@pytest.mark.negative
@allure.epic("ParaBank API")
@allure.feature("Accounts")
@allure.story("Withdraw validation")
@pytest.mark.parametrize(
    "missing_parameter",
    [
        pytest.param("account_id",
                     id="without_id",
                     ),
        pytest.param(
            "amount",
            id="without-amount",
        ),
    ],
)

def test_withdraw_without_required_parameter(
        api_client,
        funded_account,
        missing_parameter,
):
    account_id = funded_account["id"]
    invalid_amount = "invalid"

    with allure.step("Получить баланс перед некорректным запросом"):

        before_response = api_client.get_account(
            account_id=account_id
        )

        assert before_response.status_code == 200,(
            "Не удалось получить счет перед withdraw"
            f"КодЖ {before_response.status_code}"
            f"ответ:{before_response.text!r}"
        )

        balance_before = Decimal(str(before_response.json()["balance"]))

    with allure.step(
        f"Отправить Withdraw с amount={invalid_amount!r}"
    ):
        response = api_client.withdraw(
            account_id=account_id,
            amount=invalid_amount,
        )

    with allure.step(
            "Проверить, что операция отклонена"
    ):
        assert not 200 <= response.status_code < 300, (
            "Сервис принял строку вместо суммы. "
            f"Код: {response.status_code}. "
            f"URL: {response.url}. "
            f"Ответ: {response.text!r}"
        )

    with allure.step(
            "Получить баланс после некорректного запроса"
    ):
        after_response = api_client.get_account(
            account_id=account_id,
        )

        assert after_response.status_code == 200, (
            "Не удалось получить счёт после Withdraw. "
            f"Код: {after_response.status_code}. "
            f"Ответ: {after_response.text!r}"
        )

        balance_after = Decimal(
            str(after_response.json()["balance"])
        )

    with allure.step(
            "Проверить, что баланс не изменился"
    ):
        assert balance_after == balance_before, (
            "После некорректного Withdraw изменился баланс. "
            f"Баланс до: {balance_before}. "
            f"Баланс после: {balance_after}."
        )