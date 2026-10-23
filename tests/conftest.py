"""Shared fixtures for isolated mock OMS API and database tests."""
import threading
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from werkzeug.serving import make_server
from playwright.sync_api import sync_playwright

from src.app import create_app
from src.oms_api_client import OMSApiClient


@pytest.fixture(scope="session")
def oms_environment():
    """Provide one local server and one isolated DB shared by the test session."""
    with TemporaryDirectory(prefix="oms-tests-") as tmp:
        db_path = str(Path(tmp) / "oms-test.sqlite")
        app = create_app(db_path)
        server = make_server("127.0.0.1", 0, app, threaded=True)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base_url = f"http://127.0.0.1:{server.server_port}"
        try:
            yield {"base_url": base_url, "db_path": db_path}
        finally:
            server.shutdown()
            thread.join(timeout=3)


@pytest.fixture(scope="session")
def oms_server(oms_environment):
    return oms_environment["base_url"]


@pytest.fixture(scope="session")
def oms_db_path(oms_environment):
    return oms_environment["db_path"]


@pytest.fixture
def api(oms_server):
    """Low-level Playwright API context, retained for direct protocol checks."""
    with sync_playwright() as playwright:
        context = playwright.request.new_context(base_url=oms_server)
        yield context
        context.dispose()


@pytest.fixture
def oms_client(api):
    """Reusable OMS API abstraction built on Playwright's APIRequestContext."""
    return OMSApiClient(api)


@pytest.fixture
def auth_headers(oms_client):
    response = oms_client.login("qa.user@example.com", "Passw0rd!")
    assert response.status == 200, response.text()
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
