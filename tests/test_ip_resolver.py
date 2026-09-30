# tests/test_ip_resolver.py
import pytest
import requests
from unittest.mock import patch
from ip_geo_upload import IpResolver  # замени your_module на имя файла без .py


@patch("ip_geo_upload.requests.get")
def test_get_ip_success(mock_get):
    mock_resp = requests.Response()
    mock_resp.status_code = 200
    mock_resp._content = b'{"ip": "1.2.3.4"}'
    mock_get.return_value = mock_resp

    ip = IpResolver.get_ip()
    assert ip == "1.2.3.4"
    mock_get.assert_called_once()


@patch("ip_geo_upload.requests.get")
def test_get_ip_missing_field(mock_get):
    mock_resp = requests.Response()
    mock_resp.status_code = 200
    mock_resp._content = b'{}'
    mock_get.return_value = mock_resp

    with pytest.raises(RuntimeError, match="Ошибка парсинга IP"):
        IpResolver.get_ip()


@patch("ip_geo_upload.requests.get")
def test_get_ip_network_error(mock_get):
    mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")

    with pytest.raises(RuntimeError, match="Не удалось получить IP"):
        IpResolver.get_ip()
