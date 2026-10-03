from urllib.parse import quote
from typing import Any
from requests import Response

from src.api.base_client import BaseApiClient


class ParabankClient(BaseApiClient):
    def __init__(
        self,
        base_url: str,
        web_base_url: str,
        timeout: float = 15,
    ) -> None:
        super().__init__(
            base_url=base_url,
            timeout=timeout,
        )

        self.web_base_url = web_base_url.rstrip("/")

    def register_customer(
        self,
        customer_data: dict,
    ) -> Response:
        registration_url = (
            f"{self.web_base_url}/register.htm"
        )

        # Открываем страницу регистрации, чтобы получить
        # cookies текущей сессии.
        self.get(
            endpoint=registration_url,
            headers={
                "Accept": "text/html",
            },
        )

        form_data = {
            "customer.firstName": (
                customer_data["firstName"]
            ),
            "customer.lastName": (
                customer_data["lastName"]
            ),
            "customer.address.street": (
                customer_data["address.street"]
            ),
            "customer.address.city": (
                customer_data["address.city"]
            ),
            "customer.address.state": (
                customer_data["address.state"]
            ),
            "customer.address.zipCode": (
                customer_data["address.zipCode"]
            ),
            "customer.phoneNumber": (
                customer_data["phoneNumber"]
            ),
            "customer.ssn": (
                customer_data["ssn"]
            ),
            "customer.username": (
                customer_data["username"]
            ),
            "customer.password": (
                customer_data["password"]
            ),
            "repeatedPassword": (
                customer_data["password"]
            ),
        }

        return self.post(
            endpoint=registration_url,
            data=form_data,
            headers={
                "Accept": "text/html",
            },
            allow_redirects=True,
        )

    def login(
        self,
        username: str,
        password: str,
    ) -> Response:
        encoded_username = quote(
            username,
            safe="",
        )
        encoded_password = quote(
            password,
            safe="",
        )

        return self.get(
            endpoint=(
                f"/login/{encoded_username}/"
                f"{encoded_password}"
            ),
        )

    def get_customer(
        self,
        customer_id: int,
    ) -> Response:
        return self.get(
            endpoint=f"/customers/{customer_id}",
        )

    def get_customer_accounts(
        self,
        customer_id: int,
    ) -> Response:
        return self.get(
            endpoint=(
                f"/customers/{customer_id}/accounts"
            ),
        )

    def get_account(
        self,
        account_id: int,
    ) -> Response:
        return self.get(
            endpoint=f"/accounts/{account_id}",
        )

    def create_account(
        self,
        customer_id: int,
        new_account_type: int,
        from_account_id: int,
    ) -> Response:
        return self.post(
            endpoint="/createAccount",
            params={
                "customerId": customer_id,
                "newAccountType": int(
                    new_account_type
                ),
                "fromAccountId": from_account_id,
            },
        )

    def deposit(
            self,
            account_id: int,
            amount: int | float | str,
    ) -> Response:
        return self.post(
            endpoint="/deposit",
            params={
                "accountId": account_id,
                "amount": amount,
            },
        )

    def get_account_transactions(
        self,
        account_id: int,
    ) -> Response:
        return self.get(
            endpoint=(
                f"/accounts/{account_id}/transactions"
            ),
        )

    def bill_pay(self, account_id: int | str | None = None, amount: str | float | None = None, payee: dict[str, Any] | None = None) -> Response:
        params={}
        if account_id  is not None:
            params["accountId"]= account_id

        if amount is not None:
            params["amount"] = amount

        request_options = {
            "params": params,
        }

        if payee is not None:
            request_options["json"] = payee

        return self.post(
            endpoint="/billpay",
            **request_options,
        )

    def withdraw(
            self,
            account_id: int | str | None = None,
            amount: int | float | str | None = None,
    ) -> Response:
        params = {}

        if account_id is not None:
            params["accountId"] = account_id

        if amount is not None:
            params["amount"] = amount

        return self.post(
            endpoint="/withdraw",
            params=params,
        )