# tests/test_geo_locator.py
import pytest
from unittest.mock import patch
import requests
from ip_geo_upload import GeoLocator



@patch("ip_geo_upload.requests.get")
def test_locate_success(mock_get):
    mock_resp = requests.Response()
    mock_resp.status_code = 200
    mock_resp._content = b'{"city": "Moscow", "region": "Moscow Oblast", "country": "RU"}'
    mock_get.return_value = mock_resp

    locator = GeoLocator()
    data = locator.locate("1.2.3.4")

    assert data["city"] == "Moscow"
    assert "ip" not in data  # IP не добавляется внутри locate
    mock_get.assert_called_once()


@patch("ip_geo_upload.requests.get")
def test_locate_no_city(mock_get, capsys):
    mock_resp = requests.Response()
    mock_resp.status_code = 200
    mock_resp._content = b'{"region": "Unknown", "country": "XX"}'
    mock_get.return_value = mock_resp

    locator = GeoLocator()
    data = locator.locate("1.2.3.4")

    captured = capsys.readouterr()
    assert "[ВНИМАНИЕ] Город не определён" in captured.out
    assert data.get("city") is None


@patch("ip_geo_upload.requests.get")
def test_locate_http_error(mock_get):
    mock_resp = requests.Response()
    mock_resp.status_code = 500
    mock_get.return_value = mock_resp

    locator = GeoLocator()
    with pytest.raises(RuntimeError, match="Ошибка запроса к ipinfo"):
        locator.locate("1.2.3.4")

@patch("requests.get")
def test_locate_invalid_json(mock_get):
    mock_resp = requests.Response()
    mock_resp.status_code = 200
    # Это НЕ JSON — вызовет JSONDecodeError при вызове .json()
    mock_resp._content = b"<html><body>Error</body></html>"
    mock_get.return_value = mock_resp

    locator = GeoLocator()

    # Теперь сообщение будет точно таким, как ты ожидаешь
    with pytest.raises(RuntimeError, match="Ошибка парсинга JSON"):
        locator.locate("1.2.3.4")
