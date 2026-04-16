import pytest
from unittest.mock import patch, MagicMock


def test_list_transactions_returns_json_on_success():
    import functions
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "total": 1,
        "results": [{"id": "txn1", "amount": -50.0, "description": "Supermercado"}]
    }
    with patch("functions.requests.get", return_value=mock_response):
        with patch("functions.get_api_token", return_value="fake-token"):
            result = functions.list_transactions("acc-123")

    assert result["results"][0]["id"] == "txn1"


def test_list_transactions_returns_none_on_failure():
    import functions
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"
    with patch("functions.requests.get", return_value=mock_response):
        with patch("functions.get_api_token", return_value="fake-token"):
            result = functions.list_transactions("acc-123")

    assert result is None
