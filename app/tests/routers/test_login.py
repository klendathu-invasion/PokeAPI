import pytest
import pytest_check as check
from fastapi import status

from ...config.env import settings
from ..test_main import TestClient, TestingSessionLocal, client, fake, session
from ..utils.fake_model import fake_user


class FakeRequest:
    def __init__(self, status_code: int, _json: dict):
        self.status_code = status_code
        self._json = _json

    def json(self):
        return self._json

    def text(self):
        return str(self._json)
