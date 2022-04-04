from http import HTTPStatus
from typing import Iterator

import requests
import ujson
from django.conf import settings


class SWAPIException(Exception):
    pass


class SWAPIRetriever:
    def __init__(self) -> None:
        self.session = requests.Session()

    def retrieve_all(self, endpoint: str = "") -> Iterator[dict]:
        next_page = endpoint
        while next_page:
            content = self.call_api(next_page)
            yield content.get("results")
            next_page = content.get("next")

    def retrieve_one(self, endpoint: str = "") -> dict:
        return self.call_api(endpoint)

    def call_api(self, endpoint: str = "") -> dict:
        endpoint = (
            endpoint
            if endpoint.startswith(settings.SWAPI_URL)
            else f"{settings.SWAPI_URL}{endpoint}"
        )
        try:
            response = self.session.get(endpoint)
        except requests.exceptions.RequestException:
            raise SWAPIException("Request exception")
        if response.status_code == HTTPStatus.OK:
            content = ujson.loads(response.content)
            return content
        else:
            raise SWAPIException("Status code is not ok")
