import pytest
from task_cherkasov_roman_asset_web_service import app


NOT_EXISTING_PATH = "/THIS_PATH_DOES_NOT_EXIST"

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


# def test_service_reply_to_root_path

def test_error_404(client):
    # resp = requests.get("https://httpstatuses.com/503")
    resp = client.get(NOT_EXISTING_PATH)
    assert 404 == resp.status_code
