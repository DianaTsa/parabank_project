import allure
import pytest

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
            id="without-account-id",),
        pytest.param(
            "amount",
            id="without-amount",

        ),

    ],
)

def test_bill_pay_without_required_parameter(api_client, source_account, payee_data, missing_parameter,):
    allure.dynamic.title(
        f"Bill Pay без обязательного параметра "
        f"{missing_parameter}"
    )

    request_data = {
        "account_id": source_account["id"],
        "amount": "1.00",
        "payee": payee_data,
    }

    request_data.pop(missing_parameter)

    with allure.step(f"Отправить запрос без {missing_parameter}"):

        response = api_client.bill_pay(** request_data,)

    with allure.step(
            "Проверить, что сервис вернул клиентскую ошибку"
    ):
        assert 400 <= response.status_code < 500, (
            "Ожидалась ошибка 4xx при отсутствии "
            f"параметра {missing_parameter}, "
            f"получен код {response.status_code}. "
            f"Ответ: {response.text}"
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
            id="zero-account-id",
        ),
        pytest.param(
            -1,
            "отрицательный accountId",
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
            "несуществующий accountId",
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

    with allure.step(
        f"Отправить Bill Pay с accountId="
        f"{invalid_account_id!r}"
    ):
        response = api_client.bill_pay(
            account_id=invalid_account_id,
            amount="1.00",
            payee=payee_data,
        )

    with allure.step(
        "Проверить, что операция не выполнена"
    ):
        assert not 200 <= response.status_code < 300, (
            "Сервис выполнил Bill Pay с некорректным "
            f"accountId={invalid_account_id!r}. "
            f"Описание: {case_description}. "
            f"Код: {response.status_code}. "
            f"URL: {response.request.url}. "
            f"Ответ: {response.text!r}"
        )

