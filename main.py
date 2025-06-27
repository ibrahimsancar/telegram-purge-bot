"""
main.py - Telegram Purge Bot başlatıcı dosyası
Tüm handler ve yardımcı fonksiyonlar ilgili modüllerde tutulur.
"""

import logging
import asyncio
from telegram.ext import Application, ContextTypes
from telegram import Update
from telegram.error import NetworkError, TimedOut, RetryAfter
from telegram.request import HTTPXRequest
import config
from handlers import register_handlers
from utils.bot_stats import update_active_groups
from utils.bot_commands import set_bot_commands
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Log klasörünü oluştur
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Ortam değişkeniyle dinamik log dosya isimleri
env_name = os.getenv("ENV", "development")
bot_log_file = log_dir / f"purge_bot_{env_name}.log"
app_log_file = log_dir / f"app_{env_name}.log"
web_log_file = log_dir / f"web_{env_name}.log"

# Log dosyalarını sıfırla
for log_file in [bot_log_file, app_log_file, web_log_file]:
    try:
        with open(log_file, "w"): pass
    except Exception:
        pass

# Gelişmiş logging yapılandırması
def setup_logging():
    """Gelişmiş logging yapılandırması"""
    # Ana logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    # File handler (döndürme ile)
    file_handler = RotatingFileHandler(
        bot_log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,  # 5 yedek dosya
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # Handler'ları ekle
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# Logging'i başlat
logger = setup_logging()

async def update_active_groups_task(context: ContextTypes.DEFAULT_TYPE):
    """Aktif grup sayısını periyodik olarak günceller."""
    app = context.application
    try:
        # Bu özellik şu anki kütüphane sürümünde doğrudan desteklenmiyor olabilir.
        # Alternatif bir yol bulmak gerekebilir veya bu özellik atlanabilir.
        # Şimdilik bir yer tutucu olarak bırakıyorum.
        # active_chats = await app.bot.get_chat_count() # Örnek, gerçek değil
        # update_active_groups(active_chats)
        logger.info("Aktif grup sayısı güncellendi (yer tutucu).")
    except Exception as e:
        logger.error(f"Aktif grup sayısı güncellenirken hata: {e}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Hataları yakalar ve loglar."""
    logger.error("Exception while handling an update:", exc_info=context.error)
    
    # Hata türüne göre farklı işlemler
    if isinstance(context.error, NetworkError):
        logger.warning("Network hatası oluştu, yeniden bağlanmaya çalışılıyor...")
    elif isinstance(context.error, TimedOut):
        logger.warning("Timeout hatası oluştu, işlem tekrarlanıyor...")
    elif isinstance(context.error, RetryAfter):
        logger.warning(f"Rate limit aşıldı, {context.error.retry_after} saniye bekleniyor...")
    else:
        logger.error(f"Beklenmeyen hata: {context.error}")

def start_bot_polling():
    logger.info("Bot başlatılıyor...")

    # Timeout ayarlarını builder ile ver
    request = HTTPXRequest(
        read_timeout=30.0,
        connect_timeout=10.0,
        pool_timeout=30.0,
    )
    app = Application.builder().token(config.get_bot_token()).request(request).build()

    logger.info("Telegram Application başarıyla oluşturuldu.")
    # Error handler'ı ekle
    app.add_error_handler(error_handler)
    logger.info("Error handler başarıyla eklendi.")
    register_handlers(app)
    logger.info("Handler'lar başarıyla kaydedildi.")
    logger.info("Bot komutları ayarlanıyor...")
    logger.info("Bot komutları başarıyla ayarlandı.")
    logger.info("Periyodik görevler başlatılıyor...")
    logger.info("Bot polling başlatılıyor...")
    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
        timeout=30
    )
    logger.info("Bot polling durduruldu.")

if __name__ == "__main__":
    start_bot_polling() 