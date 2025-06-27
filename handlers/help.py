"""
help.py - Yardım komutları handler'ı
/help komutu için fonksiyonlar burada bulunur.
"""

import asyncio
from telegram.ext import CommandHandler, ContextTypes
from telegram import Update
from utils.help_texts import HELP_TEXT
from utils.message_utils import delete_command_message

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/help komutu için yardım mesajı gönderir."""
    # Komut mesajını 1 saniye sonra sil
    asyncio.create_task(delete_command_message(context, update.effective_chat.id, update.message.message_id, 1))
    
    await update.message.reply_text(HELP_TEXT, parse_mode='HTML')

help_handler = CommandHandler("help", help_command) 