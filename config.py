"""
config.py - Bot yapılandırma dosyası
Tüm sabitler ve ayarlar burada tutulur.
"""

import os
import json
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

SETTINGS_FILE = "settings.json"

def _read_settings() -> dict:
    """Ayarları settings.json dosyasından okur."""
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def _write_settings(settings: dict) -> None:
    """Ayarları settings.json dosyasına yazar."""
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

def get_bot_token() -> str:
    """Bot token'ını settings.json dosyasından okur."""
    settings = _read_settings()
    return settings.get("bot_token", "")

def save_bot_token(token: str) -> None:
    """Bot token'ını settings.json dosyasına yazar."""
    settings = _read_settings()
    settings["bot_token"] = token
    _write_settings(settings)

def get_delete_service_messages() -> bool:
    """Servis mesajlarını silme ayarını settings.json dosyasından okur."""
    settings = _read_settings()
    return settings.get("delete_service_messages", True) # Varsayılan olarak True

def set_delete_service_messages(value: bool) -> None:
    """Servis mesajlarını silme ayarını settings.json dosyasına yazar."""
    settings = _read_settings()
    settings["delete_service_messages"] = value
    _write_settings(settings) 