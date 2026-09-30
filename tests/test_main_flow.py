# tests/test_main_flow.py
import os
import pytest
from unittest.mock import patch
from ip_geo_upload import main

@patch("ip_geo_upload.IpResolver.get_ip", return_value="1.2.3.4")
@patch("ip_geo_upload.GeoLocator.locate", return_value={"city": "Moscow"})
@patch("ip_geo_upload.YandexDiskUploader.ensure_folder")
@patch("ip_geo_upload.YandexDiskUploader.upload_json_data")
def test_main_missing_token(mock_upload, mock_ensure, mock_locate, mock_get_ip):
    # Убираем токен из окружения
    os.environ.pop("YANDEX_DISK_TOKEN", None)

    with pytest.raises(ValueError, match="Не задан YANDEX_DISK_TOKEN"):
        main()

    # Убеждаемся, что до загрузки дело не дошло
    mock_ensure.assert_not_called()
    mock_upload.assert_not_called()
