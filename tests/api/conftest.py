from uuid import uuid4
from decimal import Decimal
import allure
import pytest
from faker import Faker
from src.api.parabank_client import ParabankClient
from src.settings import settings


@pytest.fixture(scope="session")
def api_client():
    client = ParabankClient(
        base_url=settings.base_api_url,
        web_base_url=settings.base_ui_url,
        timeout=settings.api_timeout,
        min_request_interval=2.0,
    )

    yield client

    client.close()


def _build_customer_data(faker):
    suffix = uuid4().hex

    return {
        "firstName": faker.first_name(),
        "lastName": faker.last_name(),
        "address.street": faker.street_address(),
        "address.city": faker.city(),
        "address.state": faker.state_abbr(),
        "address.zipCode": faker.postcode(),
        "phoneNumber": faker.phone_number(),
        "ssn": faker.ssn(),
        "username": f"autotest_{suffix}",
        "password": "TestPassword123!",
    }

@pytest.fixture
def customer_data(faker):
    return _build_customer_data(faker)

@pytest.fixture(scope="session")
def run_customer_data():
    customer = _build_customer_data(Faker("en_US"))

    customer["username"] = f"api_{uuid4().hex[:16]}"

    return customer


@pytest.fixture(scope="session")
def registered_customer(
    api_client,
    run_customer_data,
):
    with allure.step(
        "Один раз зарегистрировать пользователя API-прогона"
    ):
        registration_response = (
            api_client.register_customer(
                customer_data=run_customer_data,
            )
        )

        assert registration_response.status_code == 200, (
            "Не удалось зарегистрировать клиента. "
            f"Код: {registration_response.status_code}. "
            f"Ответ: {registration_response.text[:500]!r}"
        )

        content_type = (
            registration_response.headers.get(
                "Content-Type",
                "",
            ).lower()
        )

        assert "text/html" in content_type, (
            "От регистрации ожидалась HTML-страница. "
            f"Получен Content-Type: {content_type}. "
            f"Ответ: {registration_response.text[:500]!r}"
        )

        assert (
            "Your account was created successfully"
            in registration_response.text
        ), (
            "ParaBank не подтвердил регистрацию. "
            f"Ответ: {registration_response.text[:500]!r}"
        )

    with allure.step(
        "Получить пользователя прогона через REST login"
    ):
        login_response = api_client.login(
            username=run_customer_data["username"],
            password=run_customer_data["password"],
        )

        assert login_response.status_code == 200, (
            "Не удалось авторизовать клиента. "
            f"Код: {login_response.status_code}. "
            f"Ответ: {login_response.text[:500]!r}"
        )

        content_type = (
            login_response.headers.get(
                "Content-Type",
                "",
            ).lower()
        )

        assert "application/json" in content_type, (
            "От REST login ожидался JSON. "
            f"Получен Content-Type: {content_type}. "
            f"Ответ: {login_response.text[:500]!r}"
        )

        customer = login_response.json()

        assert isinstance(customer, dict), (
            f"Ожидался объект клиента: {customer}"
        )

        assert customer.get("id") is not None, (
            f"REST login не вернул ID клиента: {customer}"
        )

    return {
        "request": run_customer_data,
        "response": customer,
    }


@pytest.fixture
def customer_accounts(
    api_client,
    registered_customer,
):
    customer_id = registered_customer["response"]["id"]

    with allure.step(
        f"Получить счета клиента с ID {customer_id}"
    ):
        response = api_client.get_customer_accounts(
            customer_id=customer_id,
        )

    assert response.status_code == 200, (
        "Не удалось получить счета клиента. "
        f"Код: {response.status_code}. "
        f"Ответ: {response.text}"
    )

    accounts = response.json()

    assert isinstance(accounts, list), (
        "Ожидался список счетов, "
        f"получено: {accounts}"
    )

    assert len(accounts) > 0, (
        f"У клиента с ID {customer_id} нет счетов"
    )

    return accounts


@pytest.fixture
def source_account(customer_accounts):
    return customer_accounts[0]

@pytest.fixture
def payee_data():
    return{
        "name": "Automation Utility Company",
        "address": {
            "street": "123 Main Street",
            "city": "Moscow",
            "state": "TX",
            "zipCode": "78701",
        },
        "phoneNumber": "555-123-4567",
        "accountNumber": 987654,
    }

@pytest.fixture
def created_account(api_client, registered_customer, source_account):

    customer_id = registered_customer["response"]["id"]
    source_account_id = source_account["id"]

    with allure.step("Cоздать отдельный сберегательный счет для теста withdraw"):
        response = api_client.create_account(
            customer_id=customer_id, new_account_type=1, from_account_id=source_account_id,)

        assert response.status_code == 200, (
            "Не удалось создать счёт для теста. "
            f"Код: {response.status_code}. "
            f"URL: {response.request.url}. "
            f"Ответ: {response.text!r}"
        )

        account = response.json()

        assert account.get("id") is not None, ("Ответ создания счета не содержит ID", f"Ответ: {account}")

        assert account["customerId"] == customer_id, (
            "Созданный счёт принадлежит другому клиенту. "
            f"Ожидался customerId={customer_id}. "
            f"Получен customerId={account.get('customerId')}."
        )

        assert account["id"] != source_account_id, (
            "ID созданного счёта совпал с ID исходного счёта"
        )

        with allure.step(
                f"Проверить существование созданного счёта "
                f"{account['id']}"
        ):
            get_response = api_client.get_account(
                account_id=account["id"],
            )

        assert get_response.status_code == 200, (
            "Созданный счёт не удалось получить по ID. "
            f"Код: {get_response.status_code}. "
            f"Ответ: {get_response.text!r}"
        )

        return get_response.json()

@pytest.fixture
def funded_account(
        api_client,
        created_account,
):
    account_id = created_account["id"]
    deposit_amount = Decimal("20.00")

    with allure.step(
            f"Получить баланс счёта {account_id} "
            "перед пополнением"
    ):
        before_response = api_client.get_account(
            account_id=account_id,
        )

    assert before_response.status_code == 200, (
        "Не удалось получить счёт перед пополнением. "
        f"Код: {before_response.status_code}. "
        f"Ответ: {before_response.text!r}"
    )

    balance_before = Decimal(
        str(before_response.json()["balance"])
    )

    with allure.step(
            f"Пополнить счёт {account_id} "
            f"на {deposit_amount}"
    ):
        deposit_response = api_client.deposit(
            account_id=account_id,
            amount=str(deposit_amount),
        )

    assert deposit_response.status_code == 200, (
        "Не удалось пополнить созданный счёт. "
        f"Код: {deposit_response.status_code}. "
        f"URL: {deposit_response.request.url}. "
        f"Ответ: {deposit_response.text!r}"
    )

    with allure.step(
            f"Получить баланс счёта {account_id} "
            "после пополнения"
    ):
        after_response = api_client.get_account(
            account_id=account_id,
        )

    assert after_response.status_code == 200, (
        "Не удалось получить счёт после пополнения. "
        f"Код: {after_response.status_code}. "
        f"Ответ: {after_response.text!r}"
    )

    funded_account_data = after_response.json()

    balance_after = Decimal(
        str(funded_account_data["balance"])
    )

    expected_balance = balance_before + deposit_amount

    assert balance_after == expected_balance, (
        "Баланс после пополнения изменился некорректно. "
        f"Баланс до: {balance_before}. "
        f"Сумма пополнения: {deposit_amount}. "
        f"Ожидалось: {expected_balance}. "
        f"Получено: {balance_after}."
    )

    return funded_account_data


