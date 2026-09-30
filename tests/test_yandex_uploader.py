# tests/test_yandex_uploader.py
import pytest
from unittest.mock import patch, PropertyMock
import requests
from ip_geo_upload import YandexDiskUploader




def test_uploader_invalid_token():
    with pytest.raises(ValueError, match="OAuth-токен Яндекс.Диска не может быть пустым"):
        YandexDiskUploader("")


@patch("ip_geo_upload.requests.put")
@patch("ip_geo_upload.requests.get")
def test_ensure_folder_creates_new(mock_get, mock_put):
    # Эмулируем, что папки нет: сервер вернёт 201
    resp_put = requests.Response()
    resp_put.status_code = 201
    mock_put.return_value = resp_put

    uploader = YandexDiskUploader("fake-token")
    uploader.ensure_folder("/ip_geo_data")

    mock_put.assert_called_once()


@patch("ip_geo_upload.requests.put")
@patch("ip_geo_upload.requests.get")
def test_ensure_folder_already_exists(mock_get, mock_put):
    # Папка уже есть: сервер вернёт 409
    resp_put = requests.Response()
    resp_put.status_code = 409
    mock_put.return_value = resp_put

    uploader = YandexDiskUploader("fake-token")
    # Не должно быть исключения
    uploader.ensure_folder("/ip_geo_data")

    mock_put.assert_called_once()


@patch("ip_geo_upload.requests.put")
@patch("ip_geo_upload.requests.get")
def test_upload_json_data_success(mock_get, mock_put):
    # 1. Эмулируем получение ссылки на загрузку
    resp_get = requests.Response()
    resp_get.status_code = 200
    resp_get._content = b'{"href": "https://upload.yandex.net/abc123"}'
    mock_get.return_value = resp_get

    # 2. Эмулируем успешную загрузку
    resp_put = requests.Response()
    resp_put.status_code = 201
    mock_put.return_value = resp_put

    uploader = YandexDiskUploader("fake-token")
    json_payload = '{"city": "Moscow"}'

    uploader.upload_json_data(json_payload, "/ip_geo_data/test.json")

    # Проверка: сначала GET за ссылкой, потом PUT с данными
    assert mock_get.call_count == 1
    assert mock_put.call_count == 1

@patch("requests.put")
def test_ensure_folder_server_error(mock_put):
    # Создаём реальный экземпляр — headers инициализируются внутри __init__
    uploader = YandexDiskUploader(token="fake_token")

    # Эмулируем ошибку сервера
    mock_resp = requests.Response()
    mock_resp.status_code = 500
    mock_put.return_value = mock_resp

    # Ловим именно то, что реально выбрасывает raise_for_status()
    with pytest.raises(requests.exceptions.HTTPError):
        uploader.ensure_folder("/test/path")
