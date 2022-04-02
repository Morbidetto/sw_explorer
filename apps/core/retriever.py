from http import HTTPStatus
from typing import Iterator

import requests
import ujson
from django.conf import settings

class SWAPIException(Exception):
    pass

class SWAPIRetriever():
    def __init__(self):
        self.session = requests.Session()
    
    def retrieve(self, endpoint: str = "") -> Iterator[dict]:
        next_page = f"{settings.SWAPI_URL}{endpoint}"
        while next_page:
            try:
                response = self.session.get(next_page)
            except requests.exceptions.RequestException:
                raise SWAPIException("Request exception")
            if response.status_code == HTTPStatus.OK:
                content = ujson.loads(response.content)
                yield content
            else:
                raise SWAPIException("Status code is not ok")
            next_page = content.get("next")
