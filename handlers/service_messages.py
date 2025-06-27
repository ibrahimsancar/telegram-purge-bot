"""
service_messages.py - Servis mesajları otomatik silme
Grup katılma, ayrılma, davet etme gibi servis mesajlarını anlık siler.
"""

import asyncio
import logging
from typing import Optional

from telegram import Update, Message
from telegram.ext import ContextTypes, MessageHandler, filters
from telegram.error import TelegramError

from utils.admin import is_admin
import config

logger = logging.getLogger(__name__)

# Silinecek servis mesajı türleri
SERVICE_MESSAGE_TYPES_TO_DELETE = {
    'new_chat_members',      # Gruba katılma
    'left_chat_member',      # Gruptan ayrılma
    'new_chat_title',        # Grup adı değişikliği (isteğe bağlı)
    'new_chat_photo',        # Grup fotoğrafı değişikliği (isteğe bağlı)
    'delete_chat_photo',     # Grup fotoğrafı silme (isteğe bağlı)
}

# Silinmeyecek servis mesajı türleri (önemli işlemler)
SERVICE_MESSAGE_TYPES_TO_KEEP = {
    'pinned_message',        # Mesaj sabitleme
    'new_chat_photo',        # Grup fotoğrafı (isteğe bağlı)
    'delete_chat_photo',     # Grup fotoğrafı silme (isteğe bağlı)
    'new_chat_title',        # Grup adı değişikliği (isteğe bağlı)
}

async def auto_delete_service_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Servis mesajlarını otomatik olarak siler"""
    
    # Ayar kapalıysa işlemi yapma
    if not config.get_delete_service_messages():
        return
    
    # Sadece grup sohbetlerinde çalış
    if not update.effective_chat or update.effective_chat.type not in ['group', 'supergroup']:
        return
    
    message = update.message
    if not message:
        return
    
    # Servis mesajı kontrolü
    if not is_service_message(message):
        return
    
    # Bot yönetici mi kontrol et
    if not await is_bot_admin(context, update.effective_chat.id):
        logger.debug(f"Bot {update.effective_chat.id} grubunda yönetici değil, servis mesajı silinmiyor")
        return
    
    # Servis mesajı türünü belirle
    message_type = get_service_message_type(message)
    if not message_type:
        return
    
    # Mesaj türüne göre karar ver
    if should_delete_service_message(message_type, message):
        logger.info(f"Servis mesajı siliniyor: {message_type} (ID: {message.message_id})")
        
        # Mesajı anlık sil
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=message.message_id
            )
            logger.info(f"Servis mesajı başarıyla silindi: {message_type} (ID: {message.message_id})")
            
        except TelegramError as e:
            logger.warning(f"Servis mesajı silinemedi: {e}")
        except Exception as e:
            logger.error(f"Servis mesajı silme hatası: {e}")
    else:
        logger.debug(f"Servis mesajı korunuyor: {message_type} (ID: {message.message_id})")

def is_service_message(message: Message) -> bool:
    """Mesajın servis mesajı olup olmadığını kontrol eder"""
    return (
        message.new_chat_members or
        message.left_chat_member or
        message.new_chat_title or
        message.new_chat_photo or
        message.delete_chat_photo or
        message.pinned_message
    )

def get_service_message_type(message: Message) -> Optional[str]:
    """Servis mesajının türünü belirler"""
    if message.new_chat_members:
        return 'new_chat_members'
    elif message.left_chat_member:
        return 'left_chat_member'
    elif message.new_chat_title:
        return 'new_chat_title'
    elif message.new_chat_photo:
        return 'new_chat_photo'
    elif message.delete_chat_photo:
        return 'delete_chat_photo'
    elif message.pinned_message:
        return 'pinned_message'
    else:
        return None

def should_delete_service_message(message_type: str, message: Message) -> bool:
    """Servis mesajının silinip silinmeyeceğini belirler"""
    
    # Önemli mesajları koru
    if message_type in SERVICE_MESSAGE_TYPES_TO_KEEP:
        return False
    
    # Belirli türleri sil
    if message_type in SERVICE_MESSAGE_TYPES_TO_DELETE:
        return True
    
    # Özel durumlar
    if message_type == 'new_chat_members':
        # Bot kendisi katılıyorsa silme
        if message.new_chat_members:
            for member in message.new_chat_members:
                if member.is_bot and member.id == message.bot.id:
                    logger.info("Bot kendisi katılıyor, mesaj korunuyor")
                    return False
        return True
    
    return False

async def is_bot_admin(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> bool:
    """Botun grupta yönetici olup olmadığını kontrol eder"""
    try:
        bot_member = await context.bot.get_chat_member(chat_id, context.bot.id)
        return bot_member.status in ['administrator', 'creator']
    except Exception as e:
        logger.warning(f"Bot yönetici kontrolü hatası: {e}")
        return False

# Handler'ı oluştur
service_message_handler = MessageHandler(
    filters.ChatType.GROUPS & filters.UpdateType.MESSAGE,
    auto_delete_service_message
) 