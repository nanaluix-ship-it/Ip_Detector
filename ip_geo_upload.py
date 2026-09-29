import os
import json
import time
import requests
from typing import Any, Dict


class IpResolver:
    """Получает текущий IP через ipify."""
    API_URL = "https://api.ipify.org"

    @classmethod
    def get_ip(cls) -> str:
        try:
            resp = requests.get(cls.API_URL, params={"format": "json"}, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            ip = data.get("ip")
            if not ip:
                raise ValueError("В ответе API отсутствует поле 'ip'.")
            return ip
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Не удалось получить IP: {e}") from e
        except ValueError as e:
            raise RuntimeError(f"Ошибка парсинга IP: {e}") from e


class GeoLocator:
    """
    Определяет локацию по IP.
    """
    BASE_URL = "https://ipinfo.io"

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"
    }

    def locate(self, ip: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/{ip}/geo"
        try:
            resp = requests.get(url, headers=self.HEADERS, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            if not data.get("city"):
                print("[ВНИМАНИЕ] Город не определён — возможно, политика API изменилась.")
            return data
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ошибка запроса к ipinfo: {e}") from e
        except ValueError as e:
            raise RuntimeError(f"Ошибка парсинга JSON от ipinfo: {e}") from e


class YandexDiskUploader:
    """Загружает данные на Яндекс.Диск через REST API."""
    DISK_API_BASE = "https://cloud-api.yandex.net/v1/disk"

    def __init__(self, token: str) -> None:
        if not token:
            raise ValueError("OAuth-токен Яндекс.Диска не может быть пустым.")
        self.headers = {"Authorization": f"OAuth {token}"}

    def ensure_folder(self, path: str) -> None:
        """Создаёт папку, если её ещё нет."""
        resp = requests.put(
            f"{self.DISK_API_BASE}/resources",
            headers=self.headers,
            params={"path": path},
            timeout=10,
        )

        if resp.status_code not in (201, 409):
            resp.raise_for_status()

    def upload_json_data(self, json_string: str, disk_path: str) -> None:
        """
        Загружает JSON‑строку напрямую на Яндекс.Диск.
        """
        params = {"path": disk_path, "overwrite": "true"}

        # Получаем временную ссылку для загрузки
        resp = requests.get(
            f"{self.DISK_API_BASE}/resources/upload",
            headers=self.headers,
            params=params,
            timeout=10,
        )
        resp.raise_for_status()
        upload_url = resp.json()["href"]

        put_resp = requests.put(upload_url, data=json_string.encode("utf-8"), timeout=60)
        put_resp.raise_for_status()


def main() -> None:
    # Шаг 1: Получаем IP
    ip = IpResolver.get_ip()
    print(f"IP получен: {ip}")

    # Шаг 2: Определяем локацию
    locator = GeoLocator()
    geo = locator.locate(ip)

    city = geo.get("city", "неизвестен")
    region = geo.get("region", "неизвестен")
    country = geo.get("country", "неизвестна")

    print(f"Город: {city}")
    print(f"Регион: {region}")
    print(f"Страна: {country}")

    # Добавляем IP в данные
    geo["ip"] = ip

    # Сериализуем в JSON‑строку
    json_payload = json.dumps(geo, ensure_ascii=False, indent=2)

    # Шаг 3: Загружаем на Яндекс.Диск
    token = os.environ.get("YANDEX_DISK_TOKEN")
    if not token:
        raise ValueError("Не задан YANDEX_DISK_TOKEN. Проверьте настройки запуска в IDE.")

    uploader = YandexDiskUploader(token)
    folder = "ip_geo_data"
    uploader.ensure_folder(folder)

    filename = f"geo_{int(time.time())}.json"
    disk_path = f"/{folder}/{filename}"

    # Загружаем сразу из памяти
    uploader.upload_json_data(json_payload, disk_path)
    print(f"Файл успешно загружен на Диск: {disk_path}")


    print("\nИтоговые данные (JSON):")
    print(json_payload)


if __name__ == "__main__":
    main()