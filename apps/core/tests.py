from http import HTTPStatus

import pytest
import responses
from django.conf import settings
from requests.exceptions import RequestException

from core.retriever import SWAPIRetriever, SWAPIException


class TestRetriever:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.api_client = SWAPIRetriever()
        self.test_url = "test"

    @responses.activate
    def test_valid_response(self):
        valid_response = {"ok": 1}
        responses.add(
            responses.GET,
            f"{settings.SWAPI_URL}{self.test_url}",
            json=valid_response,
            status=HTTPStatus.OK,
        )
        content = self.api_client.call_api(self.test_url)
        assert content == valid_response
        content = self.api_client.retrieve_one(self.test_url)
        assert content == valid_response

    @responses.activate
    def test_invalid_status_code(self):
        responses.add(
            responses.GET,
            f"{settings.SWAPI_URL}{self.test_url}",
            status=HTTPStatus.NOT_FOUND,
        )
        with pytest.raises(SWAPIException):
            self.api_client.call_api(self.test_url)

    @responses.activate
    def test_request_exception(self):
        responses.add(
            responses.GET,
            f"{settings.SWAPI_URL}{self.test_url}",
            body=RequestException(),
        )
        with pytest.raises(SWAPIException):
            self.api_client.call_api(self.test_url)

    @responses.activate
    def test_api_url_added(self):
        responses.add(responses.GET, f"{self.test_url}", status=HTTPStatus.OK)
        with pytest.raises(SWAPIException) as exc:
            self.api_client.call_api(self.test_url)
        # Responses library will point out that call was made to URL with SWAPI prefix
        assert settings.SWAPI_URL in str(exc._excinfo[1].__cause__)

    @responses.activate
    def test_paginating(self):
        second_url = "test_2"
        valid_response = {"results": 1, "next": second_url}
        second_reponse = {"results": 2}
        responses.add(
            responses.GET,
            f"{settings.SWAPI_URL}{self.test_url}",
            json=valid_response,
            status=HTTPStatus.OK,
        )
        responses.add(
            responses.GET,
            f"{settings.SWAPI_URL}{second_url}",
            json=second_reponse,
            status=HTTPStatus.OK,
        )
        content = list(self.api_client.retrieve_all(self.test_url))
        assert len(content) == 2
        assert content[0] == valid_response.get("results")
        assert content[1] == second_reponse.get("results")
