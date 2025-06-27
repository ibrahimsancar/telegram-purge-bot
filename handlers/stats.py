"""
stats.py - /stats komutu handler'ı
Botun teknik ve genel istatistiklerini gösterir.
"""

import asyncio
from telegram.ext import CommandHandler, ContextTypes
from telegram import Update
from utils.help_texts import HELP_TEXT
from utils.admin import is_admin
from web.database import SessionLocal
from web import crud

STATS_TEXT = """
📊 <b>Telegram Purge Bot İstatistikleri</b>

<b>🤖 Bot Bilgileri:</b>
• Bot Adı: Telegram Purge Bot
• Sürüm: 2.0
• Geliştirici: İbrahim Can Sancar

<b>⚙️ Teknik Özellikler:</b>
• Maksimum silinecek mesaj: 100
• Rate limiting: 0.1 saniye
• Mesaj yaşı sınırı: 2 gün
• Anonim admin desteği: ✅

<b>🔧 Kullanılabilir Komutlar:</b>
• /start - Bot başlatma
• /help - Yardım menüsü
• /del - Tek mesaj silme
• /purge - Toplu temizlik
• /purgefrom - Aralık başlangıcı
• /purgeto - Aralık bitişi
• /stats - Bu menü

<b>📈 Performans:</b>
• Hızlı mesaj işleme
• Akıllı yaş kontrolü
• Detaylı raporlama
• Hata toleransı

<b>🛡️ Güvenlik:</b>
• Admin yetki kontrolü
• Bot mesajı koruması
• Rate limiting
• Hata yönetimi

Bot aktif ve çalışır durumda! 🚀

🤖 <i>Bu bot İbrahim Can Sancar tarafından geliştirilmiştir</i>
"""

async def auto_delete_message(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int, delay: int = 10):
    """Mesajı belirtilen süre sonra otomatik siler."""
    await asyncio.sleep(delay)
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        pass  # Mesaj zaten silinmiş olabilir

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/stats komutu için bot istatistiklerini gönderir."""
    asyncio.create_task(auto_delete_message(context, update.effective_chat.id, update.message.message_id, 1))
    
    if not await is_admin(update, context):
        error_message = "❌ Bu komutu sadece admin'ler kullanabilir."
        error_message += "\n\n🤖 <i>Bu bot İbrahim Can Sancar tarafından geliştirilmiştir</i>"
        try:
            result_message = await update.message.reply_text(error_message, parse_mode='HTML')
            asyncio.create_task(auto_delete_message(context, update.effective_chat.id, result_message.message_id, 10))
        except Exception as e:
            result_message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=error_message,
                parse_mode='HTML'
            )
            asyncio.create_task(auto_delete_message(context, update.effective_chat.id, result_message.message_id, 10))
        return

    db = SessionLocal()
    try:
        total_deleted_messages = crud.get_stats(db).get('total_deleted_messages', 0)
        total_purge_commands = crud.get_stats(db).get('total_purge_commands', 0)
        active_groups = crud.get_stats(db).get('active_groups', 0)

        stats_text = f"""
📊 <b>Telegram Purge Bot İstatistikleri</b>

<b>🤖 Bot Bilgileri:</b>
• Bot Adı: Telegram Purge Bot
• Sürüm: 2.0
• Geliştirici: İbrahim Can Sancar

<b>📈 Genel İstatistikler:</b>
• Toplam Silinen Mesaj: <b>{total_deleted_messages}</b>
• Toplam Temizleme Komutu: <b>{total_purge_commands}</b>
• Aktif Grup Sayısı: <b>{active_groups}</b>

<b>⚙️ Teknik Özellikler:</b>
• Maksimum silinecek mesaj: 100
• Rate limiting: 0.1 saniye
• Mesaj yaşı sınırı: 2 gün
• Anonim admin desteği: ✅

<b>🔧 Kullanılabilir Komutlar:</b>
• /start - Bot başlatma
• /help - Yardım menüsü
• /del - Tek mesaj silme
• /purge - Toplu temizlik
• /purgefrom - Aralık başlangıcı
• /purgeto - Aralık bitişi
• /stats - Bu menü

<b>🛡️ Güvenlik:</b>
• Admin yetki kontrolü
• Bot mesajı koruması
• Rate limiting
• Hata yönetimi

Bot aktif ve çalışır durumda! 🚀

🤖 <i>Bu bot İbrahim Can Sancar tarafından geliştirilmiştir</i>
"""

    finally:
        db.close()

    await update.message.reply_text(stats_text, parse_mode='HTML')

stats_handler = CommandHandler("stats", stats_command) 