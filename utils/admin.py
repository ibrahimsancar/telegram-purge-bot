"""
admin.py - Admin kontrol fonksiyonu
Kullanıcının admin olup olmadığını kontrol eder.
"""

from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Kullanıcının admin olup olmadığını kontrol eder."""
    try:
        user = update.effective_user
        chat = update.effective_chat
        if not user or not chat:
            logger.warning("Kullanıcı veya chat nesnesi yok.")
            return False
        if chat.type == "private":
            return True
        if user.id == 1087968824 and user.username == "GroupAnonymousBot":
            logger.info("Anonim admin tespit edildi, komut izni verildi!")
            return True
        member = await context.bot.get_chat_member(chat.id, user.id)
        status = str(getattr(member, 'status', '')).lower()
        logger.info(f"Admin kontrolü: user_id={user.id}, status={status}, username={user.username}")
        return status in ["administrator", "owner", "creator"]
    except Exception as e:
        logger.error(f"Admin kontrolü hatası: {e}")
        return False 