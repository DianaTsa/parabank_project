import allure
import pytest

BILL_PAY_INVALID_ACCOUNT_DEFECT = pytest.mark.xfail(
    reason=(
        "PB-002: Bill Pay с пустым accountId или числовым "
        "ID несуществующего счёта возвращает HTTP 500 "
        "вместо ожидаемой клиентской ошибки 4xx"
    ),
    raises=AssertionError,
    strict=True,
)


@pytest.mark.api
@pytest.mark.regression
@pytest.mark.negative
@allure.epic("ParaBank API")
@allure.feature("Bill Pay")
@allure.story("Валидация обязательных параметров")
@pytest.mark.parametrize(
    "missing_parameter",
    [
        pytest.param(
            "account_id",
            marks=pytest.mark.xfail(
                reason=(
                    "PB-001: Bill Pay без accountId возвращает "
                    "HTTP 500 и HTML-страницу ошибки вместо "
                    "ожидаемой клиентской ошибки 4xx"
                ),
                raises=AssertionError,
                strict=True,
            ),
            id="without-account-id",
        ),
    ],
)
def test_bill_pay_without_required_parameter(
    api_client,
    funded_account,
    payee_data,
    missing_parameter,
):
    account_id = funded_account["id"]

    allure.dynamic.title(
        "Bill Pay без обязательного параметра "
        f"{missing_parameter}"
    )

    request_data = {
        "account_id": account_id,
        "payee": payee_data,
    }

    request_data.pop(missing_parameter)

    with allure.step(
        f"Отправить запрос без {missing_parameter}"
    ):
        response = api_client.bill_pay(
            **request_data,
        )

    with allure.step(
        "Проверить, что сервис вернул клиентскую ошибку"
    ):
        assert 400 <= response.status_code < 500, (
            "Ожидалась ошибка 4xx при отсутствии "
            f"параметра {missing_parameter}. "
            f"Получен код: {response.status_code}. "
            f"URL: {response.url}. "
            f"Ответ: {response.text!r}"
        )


@pytest.mark.api
@pytest.mark.regression
@pytest.mark.negative
@allure.epic("ParaBank API")
@allure.feature("Bill Pay")
@allure.story("Валидация accountId")
@pytest.mark.parametrize(
    ("invalid_account_id", "case_description"),
    [
        pytest.param(
            "",
            "пустой accountId",
            marks=BILL_PAY_INVALID_ACCOUNT_DEFECT,
            id="empty-account-id",
        ),
        pytest.param(
            "invalid",
            "строка вместо числового accountId",
            id="string-account-id",
        ),
        pytest.param(
            0,
            "нулевой accountId",
            marks=BILL_PAY_INVALID_ACCOUNT_DEFECT,
            id="zero-account-id",
        ),
        pytest.param(
            -1,
            "отрицательный accountId",
            marks=BILL_PAY_INVALID_ACCOUNT_DEFECT,
            id="negative-account-id",
        ),
        pytest.param(
            2147483648,
            "accountId выше максимального значения int32",
            id="above-int32-max",
        ),
        pytest.param(
            -2147483649,
            "accountId ниже минимального значения int32",
            id="below-int32-min",
        ),
        pytest.param(
            999999999,
            "проверяемый несуществующий accountId",
            marks=BILL_PAY_INVALID_ACCOUNT_DEFECT,
            id="nonexistent-account-id",
        ),
    ],
)
def test_bill_pay_with_invalid_account_id(
    api_client,
    payee_data,
    invalid_account_id,
    case_description,
):
    allure.dynamic.title(
        f"Bill Pay: {case_description}"
    )

    allure.dynamic.parameter(
        "account_id",
        invalid_account_id,
    )

    if invalid_account_id == 999999999:
        with allure.step(
                "Проверить, что выбранный счёт не существует"
        ):
            account_response = api_client.get_account(
                account_id=invalid_account_id,
            )

            expected_message = (
                f"Could not find account #{invalid_account_id}"
            )

            account_not_found = (
                    account_response.status_code == 400
                    and account_response.text.strip()
                    == expected_message
            )

            if not account_not_found:
                pytest.fail(
                    "Предусловие не выполнено: ожидался "
                    "HTTP 400 с сообщением об отсутствии "
                    "выбранного счёта. "
                    f"AccountId: {invalid_account_id}. "
                    f"Получен код: "
                    f"{account_response.status_code}. "
                    f"Ответ: {account_response.text!r}"
                )
    with allure.step(
        "Отправить Bill Pay с accountId="
        f"{invalid_account_id!r}"
    ):
        response = api_client.bill_pay(
            account_id=invalid_account_id,
            amount="1.00",
            payee=payee_data,
        )

    with allure.step(
        "Проверить, что сервис вернул клиентскую ошибку"
    ):
        error_message = (
            "Для некорректного accountId ожидалась "
            "ошибка класса 4xx. "
            f"AccountId: {invalid_account_id!r}. "
            f"Описание: {case_description}. "
            f"Получен код: {response.status_code}. "
            f"URL: {response.url}. "
            f"Ответ: {response.text!r}"
        )

        if not (
            400 <= response.status_code < 500
            or response.status_code == 500
        ):
            pytest.fail(error_message)

        assert 400 <= response.status_code < 500, (
            error_message
        )