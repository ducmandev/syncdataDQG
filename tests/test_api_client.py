import pytest
from unittest.mock import MagicMock, patch
from common.services.api_client import ApiClient

@patch('common.services.api_client.httpx.Client')
def test_login_success(mock_client):
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"token": "fake_token", "token_type": "bearer"}
    mock_client.return_value.post.return_value = mock_response

    # This assumes settings are loaded, may need to mock settings for isolated tests
    with patch('common.services.api_client.settings') as mock_settings:
        api_client = ApiClient()
        # Act
        token = api_client._login("test_shop")
        # Assert
        assert token == "fake_token"