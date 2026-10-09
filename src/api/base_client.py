import time
from typing import Any

import allure
import requests
from requests import Response

class RateLimitError(RuntimeError):
    """Стенд ограничил запросы текущего API-прогона."""

class BaseApiClient:
    def __init__(
        self,
        base_url: str,
        timeout: float = 15,
        min_request_interval: float = 1.5,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.min_request_interval = min_request_interval
        self._last_request_time = 0.0
        self._rate_limit_message: str | None = None
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/json",
            }
        )

    def _wait_before_request(self) -> None:
        if self._last_request_time == 0:
            return

        elapsed = (
            time.monotonic()
            - self._last_request_time
        )
        delay = self.min_request_interval - elapsed

        if delay > 0:
            time.sleep(delay)

    def request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> Response:
        if self._rate_limit_message is not None:
            raise RateLimitError(self._rate_limit_message)

        if endpoint.startswith(("http://", "https://")):
            url = endpoint
        else:
            url = (
                f"{self.base_url}/"
                f"{endpoint.lstrip('/')}"
            )

        self._wait_before_request()

        with allure.step(
            f"{method.upper()} {endpoint}"
        ):
            self._attach_request(
                method=method,
                url=url,
                kwargs=kwargs,
            )

            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    timeout=self.timeout,
                    **kwargs,
                )
            finally:
                self._last_request_time = time.monotonic()

            self._attach_response(response)

            for received_response in (
                *response.history,
                response,
            ):
                content_type = (
                    received_response.headers.get(
                        "Content-Type",
                        "",
                    ).lower()
                )
                response_text = received_response.text.lower()

                is_rate_limited = (
                    received_response.status_code == 429
                    or (
                        "text/html" in content_type
                        and (
                            "error 1015" in response_text
                            or "you are being rate limited"
                            in response_text
                        )
                    )
                )

                if is_rate_limited:
                    retry_after = (
                        received_response.headers.get(
                            "Retry-After",
                            "не указан",
                        )
                    )

                    self._rate_limit_message = (
                        "Стенд ограничил запросы. "
                        f"HTTP-код: "
                        f"{received_response.status_code}. "
                        f"Retry-After: {retry_after}. "
                        "Новые запросы этим клиентом "
                        "остановлены. Ответ сохранён в Allure."
                    )

                    raise RateLimitError(
                        self._rate_limit_message
                    )

            return response
    def get(
        self,
        endpoint: str,
        **kwargs: Any,
    ) -> Response:
        return self.request(
            method="GET",
            endpoint=endpoint,
            **kwargs,
        )

    def post(
        self,
        endpoint: str,
        **kwargs: Any,
    ) -> Response:
        return self.request(
            method="POST",
            endpoint=endpoint,
            **kwargs,
        )

    def put(
        self,
        endpoint: str,
        **kwargs: Any,
    ) -> Response:
        return self.request(
            method="PUT",
            endpoint=endpoint,
            **kwargs,
        )

    def delete(
        self,
        endpoint: str,
        **kwargs: Any,
    ) -> Response:
        return self.request(
            method="DELETE",
            endpoint=endpoint,
            **kwargs,
        )

    def close(self) -> None:
        self.session.close()

    @staticmethod
    def _attach_request(
        method: str,
        url: str,
        kwargs: dict[str, Any],
    ) -> None:
        request_data = {
            "method": method.upper(),
            "url": url,
            "params": BaseApiClient._hide_sensitive_data(
                kwargs.get("params")
            ),
            "json": BaseApiClient._hide_sensitive_data(
                kwargs.get("json")
            ),
            "data": BaseApiClient._hide_sensitive_data(
                kwargs.get("data")
            ),
        }

        allure.attach(
            body=str(request_data),
            name="API request",
            attachment_type=allure.attachment_type.TEXT,
        )

    @staticmethod
    def _attach_response(response: Response) -> None:
        response_info = (
            f"Status code: {response.status_code}\n"
            f"URL: {response.url}\n"
            f"Content-Type: "
            f"{response.headers.get('Content-Type')}\n\n"
            f"{response.text}"
        )

        allure.attach(
            body=response_info,
            name=f"API response [{response.status_code}]",
            attachment_type=allure.attachment_type.TEXT,
        )

    @staticmethod
    def _hide_sensitive_data(data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        hidden_data = {}

        for key, value in data.items():
            if "password" in key.lower():
                hidden_data[key] = "***"
            else:
                hidden_data[key] = value

        return hidden_data