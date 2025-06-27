"""
bot_commands.py - Bot komutları ayarlama fonksiyonu
Telegram'da görünecek komut listesini ayarlar.
"""

import logging
from telegram import BotCommand

logger = logging.getLogger(__name__)

async def set_bot_commands(bot):
    """Bot komutlarını Telegram'da görünür hale getirir."""
    commands = [
        BotCommand("start", "🚀 Botu başlat ve hoş geldin mesajını gör"),
        BotCommand("help", "❓ Komutlar hakkında detaylı yardım al"),
        BotCommand("del", "🗑️ Yanıtladığın tek mesajı sil"),
        BotCommand("purge", "🧹 Yanıtladığın mesajdan itibaren temizlik yap"),
        BotCommand("purgefrom", "📍 Aralık temizliği için başlangıç noktası seç"),
        BotCommand("purgeto", "🎯 Aralık temizliği için bitiş noktası seç ve temizle"),
        BotCommand("stats", "📊 Bot istatistiklerini görüntüle")
    ]
    
    try:
        await bot.set_my_commands(commands)
        logger.info("Bot komutları başarıyla ayarlandı")
    except Exception as e:
        logger.error(f"Bot komutları ayarlanamadı: {e}") 