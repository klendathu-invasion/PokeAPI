from pathlib import Path

import pytest
import pytest_check as check
from fastapi import status
from fastapi.responses import FileResponse

from ...config.env import settings
from ..test_main import TestClient, client, client_with_engine, fake, session


def test_get_all_users(client: TestClient):
    response = client.get("/debug/all_users")
    check.equal(response.status_code, status.HTTP_200_OK)
    check.is_instance(response.json(), list)


@pytest.fixture(
    params=[("json", False, None), ("json", True, None), ("sql", False, "users")]
)
def test_get_tables(request, client: TestClient):
    mode, save, name = request.param
    if name:
        response = client.get(f"/debug/tables?mode={mode}&save={save}&name={name}")
    else:
        response = client.get(f"/debug/tables?mode={mode}&save={save}")
    check.equal(response.status_code, status.HTTP_200_OK)


def test_get_coverage(mocker, client: TestClient):
    mocker.patch("pathlib.Path.exists")
    mocker.patch("shutil.make_archive")

    response = client.get("/debug/coverage")
    check.equal(response.status_code, status.HTTP_200_OK)


def test_get_coverage2(mocker, client: TestClient):
    def send_false():
        return False

    mocker.patch("pathlib.Path.exists", side_effect=send_false)
    mocker.patch("pathlib.Path.is_file", side_effect=send_false)
    mocker.patch("pathlib.Path.touch")
    mocker.patch("subprocess.run")
    mocker.patch("pathlib.Path.unlink")

    response = client.get("/debug/coverage")
    check.equal(response.status_code, status.HTTP_208_ALREADY_REPORTED)


def test_get_info(client: TestClient):
    response = client.get("/debug/info")
    check.equal(response.status_code, status.HTTP_200_OK)
    check.equal(response.json(), settings.model_dump())


def test_get_schema(client_with_engine: TestClient):
    path = Path("./sql/schema.sql")
    if path.is_file():
        path.unlink()
    response = client_with_engine.get("/debug/schema")
    check.equal(response.status_code, status.HTTP_200_OK)
    check.equal(response.text, "".join(open("./sql/schema.sql").readlines()))


def test_get_reset_database(client_with_engine: TestClient):
    response = client_with_engine.get("/debug/reset")
    check.equal(response.status_code, status.HTTP_200_OK)
    check.equal(response.json(), {"message": "database is reseting"})
