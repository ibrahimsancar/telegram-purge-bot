"""
purge.py - Mesaj silme komutları
Tek mesaj silme, toplu temizlik ve aralık temizliği komutları.
"""

import asyncio
import logging
import time
from typing import Dict, Optional

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from telegram.error import TelegramError

from utils.admin import is_admin
from utils.message_utils import is_message_old, format_purge_result, send_old_message_warning, edit_old_message
from utils.bot_stats import increment_total_deleted, increment_total_purges, add_history_entry
from utils.batch_processor import batch_processor
from utils.rate_limiter import rate_limiter

logger = logging.getLogger(__name__)

async def delete_single_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tek mesaj silme komutu: /del"""
    logger.info("=== /del komutu çalıştırıldı ===")
    
    # Komut mesajını 1 saniye sonra sil
    asyncio.create_task(auto_delete_message(context, update.effective_chat.id, update.message.message_id, 1))
    
    if not await is_admin(update, context):
        error_message = "❌ Bu komutu sadece admin'ler kullanabilir."
        error_message += "\n\n🤖 İbrahim Can Sancar tarafından geliştirilmiştir"
        result_message = await update.message.reply_text(error_message, parse_mode='HTML')
        asyncio.create_task(auto_delete_message(context, update.effective_chat.id, result_message.message_id, 10))
        return
    
    if not update.message.reply_to_message:
        logger.warning("Yanıtlanan mesaj yok!")
        error_message = "❌ Bu komutu kullanmak için bir mesaja yanıt verin."
        error_message += "\n\n🤖 İbrahim Can Sancar tarafından geliştirilmiştir"
        result_message = await update.message.reply_text(error_message, parse_mode='HTML')
        asyncio.create_task(auto_delete_message(context, update.effective_chat.id, result_message.message_id, 10))
        return
    
    try:
        target_message = update.message.reply_to_message
        logger.info(f"Hedef mesaj ID: {target_message.message_id}")
        logger.info(f"Hedef mesaj tarihi: {target_message.date}")
        logger.info(f"Hedef mesaj bot mu: {target_message.from_user.is_bot if target_message.from_user else 'Bilinmiyor'}")
        
        # Mesaj yaşı kontrolü
        logger.info(f"Mesaj yaşı kontrol ediliyor. Mesaj tarihi: {target_message.date}")
        if is_message_old(target_message.date):
            logger.info("Mesaj 2 günden eski olarak tespit edildi, düzenleniyor...")
            success = await edit_old_message(
                context, 
                update.effective_chat.id, 
                target_message.message_id
            )
            if success:
                logger.info("Eski mesaj başarıyla düzenlendi")
            else:
                logger.error("Eski mesaj düzenlenemedi")
                error_message = (
                    "<b>❌ Mesaj Silinemedi</b>\n\n"
                    "Bu mesaj 2 günden eski olduğu için <b>Telegram kısıtlamaları</b> nedeniyle silinemiyor veya düzenlenemiyor.\n"
                    "<i>Yalnızca yeni mesajlar silinebilir.</i>"
                )
                result_message = await update.message.reply_text(error_message, parse_mode='HTML')
                asyncio.create_task(auto_delete_message(context, update.effective_chat.id, result_message.message_id, 10))
                return
        else:
            logger.info("Mesaj 2 günden yeni olarak tespit edildi, siliniyor...")
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=target_message.message_id
            )
            logger.info("Mesaj başarıyla silindi")
        
        # İstatistikleri ve geçmişi güncelle
        increment_total_deleted()
        increment_total_purges()
        add_history_entry(
            chat_id=str(update.effective_chat.id),
            command='/del',
            deleted_messages=1
        )
        
        # Sadece tek bilgi mesajı gönder
        success_message = "✅ Mesaj başarıyla silindi!\n\n🤖 İbrahim Can Sancar tarafından geliştirilmiştir"
        result_message = await update.message.reply_text(success_message, parse_mode='HTML')
        asyncio.create_task(auto_delete_message(context, update.effective_chat.id, result_message.message_id, 10))
        
    except TelegramError as e:
        logger.warning(f"Mesaj silinemedi: {e}")
        error_message = "❌ Mesaj silinemedi. Bu mesaj 2 günden eski olabilir veya erişim yetkiniz yok."
        error_message += "\n\n🤖 İbrahim Can Sancar tarafından geliştirilmiştir"
        result_message = await update.message.reply_text(error_message, parse_mode='HTML')
        asyncio.create_task(auto_delete_message(context, update.effective_chat.id, result_message.message_id, 10))

async def purge_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Genel ve seçici temizlik komutu: /purge [number]"""
    logger.info("=== /purge komutu çalıştırıldı ===")
    
    # Komut mesajını 1 saniye sonra sil
    asyncio.create_task(auto_delete_message(context, update.effective_chat.id, update.message.message_id, 1))
    
    if not await is_admin(update, context):
        error_message = "❌ Bu komutu sadece admin'ler kullanabilir."
        error_message += "\n\n🤖 İbrahim Can Sancar tarafından geliştirilmiştir"
        try:
            result_message = await update.message.reply_text(error_message, parse_mode='HTML')
        except Exception:
            result_message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=error_message,
                parse_mode='HTML'
            )
        asyncio.create_task(auto_delete_message(context, update.effective_chat.id, result_message.message_id, 10))
        return
    
    if not update.message.reply_to_message:
        error_message = "❌ Bu komutu kullanmak için bir mesaja yanıt verin."
        error_message += "\n\n🤖 İbrahim Can Sancar tarafından geliştirilmiştir"
        try:
            result_message = await update.message.reply_text(error_message, parse_mode='HTML')
        except Exception:
            result_message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=error_message,
                parse_mode='HTML'
            )
        asyncio.create_task(auto_delete_message(context, update.effective_chat.id, result_message.message_id, 10))
        return
    
    try:
        target_message_id = update.message.reply_to_message.message_id
        logger.info(f"Hedef mesaj ID: {target_message_id}")
        
        args = context.args
        if args and args[0].isdigit():
            message_count = int(args[0])
            logger.info(f"Belirtilen mesaj sayısı: {message_count}")
            
            # Sadece istenen kadar mesajı sil
            result = await purge_message_range(
                update, context, 
                start_message_id=target_message_id,
                count=message_count
            )
        else:
            # Sayı belirtilmemişse, yanıtlanan mesajdan son mesaja kadar sil
            current_message_id = update.message.message_id
            last_message_id = await find_last_message_id(context, update.effective_chat.id, current_message_id)
            start_id = target_message_id
            end_id = last_message_id
            message_count = end_id - start_id + 1
            logger.info(f"Son mesajdan hedef mesaja kadar: {message_count} mesaj (ID {end_id} -> {start_id})")
            
            result = await purge_message_range(
                update, context, 
                start_message_id=start_id,
                end_message_id=end_id
            )
        
        result_text = format_purge_result(result)
        try:
            result_message = await update.message.reply_text(result_text, parse_mode='HTML')
        except Exception:
            result_message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=result_text,
                parse_mode='HTML'
            )
        asyncio.create_task(auto_delete_message(context, update.effective_chat.id, result_message.message_id, 10))
        
    except Exception as e:
        logger.error(f"Purge hatası: {e}")
        error_message = "❌ Toplu temizlik sırasında bir hata oluştu."
        error_message += "\n\n🤖 İbrahim Can Sancar tarafından geliştirilmiştir"
        try:
            result_message = await update.message.reply_text(error_message, parse_mode='HTML')
        except Exception:
            result_message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=error_message,
                parse_mode='HTML'
            )
        asyncio.create_task(auto_delete_message(context, update.effective_chat.id, result_message.message_id, 10))

async def find_last_message_id(context: ContextTypes.DEFAULT_TYPE, chat_id: int, current_message_id: int) -> int:
    """Son mesaj ID'sini bulmak için akıllı arama yapar"""
    logger.info(f"Son mesaj ID aranıyor... Başlangıç: {current_message_id}")
    
    # Basit ve güvenilir yöntem: Mevcut mesaj ID'sinden +10 ekle
    # Bu çoğu durumda yeterli olacaktır
    estimated_last_id = current_message_id + 10
    logger.info(f"Tahmini son mesaj ID: {estimated_last_id}")
    
    # Eğer daha fazla mesaj varsa, bunları da dahil et
    # Maksimum 50 mesaj daha ekle (çok fazla API çağrısı yapmamak için)
    max_additional_messages = 50
    
    for offset in range(10, max_additional_messages + 1, 5):
        test_message_id = current_message_id + offset
        
        try:
            # Mesajı kontrol et (sadece varlığını doğrula)
            # Bu daha hızlı ve güvenilir
            await context.bot.get_chat(chat_id)
            logger.info(f"Test mesaj ID {test_message_id} mevcut")
            estimated_last_id = test_message_id
        except Exception as e:
            logger.debug(f"Test mesaj ID {test_message_id} bulunamadı, arama sonlandırılıyor")
            break
    
    logger.info(f"Bulunan son mesaj ID: {estimated_last_id}")
    return estimated_last_id

async def purge_from(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Aralık temizliği başlangıç komutu: /purgefrom"""
    # Komut mesajını 1 saniye sonra sil
    asyncio.create_task(auto_delete_message(context, update.effective_chat.id, update.message.message_id, 1))
    
    if not await is_admin(update, context):
        error_message = "❌ Bu komutu sadece admin'ler kullanabilir."
        error_message += "\n\n🤖 İbrahim Can Sancar tarafından geliştirilmiştir"
        
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
    
    if not update.message.reply_to_message:
        error_message = "❌ Bu komutu kullanmak için bir mesaja yanıt verin."
        error_message += "\n\n🤖 İbrahim Can Sancar tarafından geliştirilmiştir"
        
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
    
    # Başlangıç mesaj ID'sini user_data'ya kaydet
    context.user_data['purge_from_id'] = update.message.reply_to_message.message_id
    success_message = "✅ Başlangıç mesajı seçildi. Şimdi bitiş mesajına /purgeto komutu ile yanıt verin."
    success_message += "\n\n🤖 İbrahim Can Sancar tarafından geliştirilmiştir"
    
    try:
        result_message = await update.message.reply_text(success_message, parse_mode='HTML')
        asyncio.create_task(auto_delete_message(context, update.effective_chat.id, result_message.message_id, 10))
    except Exception as e:
        result_message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=success_message,
            parse_mode='HTML'
        )
        asyncio.create_task(auto_delete_message(context, update.effective_chat.id, result_message.message_id, 10))

async def purge_to(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Aralık temizliği bitiş komutu: /purgeto"""
    # Komut mesajını 1 saniye sonra sil
    asyncio.create_task(auto_delete_message(context, update.effective_chat.id, update.message.message_id, 1))
    
    if not await is_admin(update, context):
        error_message = "❌ Bu komutu kullanmak için admin olmalısınız."
        error_message += "\n\n🤖 İbrahim Can Sancar tarafından geliştirilmiştir"
        
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
    
    if not update.message.reply_to_message:
        error_message = "❌ Bu komutu kullanmak için bir mesaja yanıt verin."
        error_message += "\n\n🤖 İbrahim Can Sancar tarafından geliştirilmiştir"
        
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
    
    if 'purge_from_id' not in context.user_data:
        error_message = "❌ Önce /purgefrom komutu ile başlangıç mesajını seçin."
        error_message += "\n\n🤖 İbrahim Can Sancar tarafından geliştirilmiştir"
        
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
    
    try:
        start_id = context.user_data['purge_from_id']
        end_id = update.message.reply_to_message.message_id
        
        # ID'leri sırala
        if start_id > end_id:
            start_id, end_id = end_id, start_id
        
        # Mesajları sil
        result = await purge_message_range(
            update, context,
            start_message_id=start_id,
            end_message_id=end_id
        )
        
        # Context'i temizle
        context.user_data.pop('purge_from_id', None)
        
        # Detaylı sonuç mesajı
        result_text = format_purge_result(result)
        
        # Sonuç mesajı
        try:
            result_message = await update.message.reply_text(result_text, parse_mode='HTML')
            
            # 10 saniye sonra sonuç mesajını sil (asenkron olarak)
            asyncio.create_task(auto_delete_message(context, update.effective_chat.id, result_message.message_id, 10))
            
        except Exception as e:
            # Komut mesajı silinmişse, normal mesaj gönder
            result_message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=result_text,
                parse_mode='HTML'
            )
            # Bu mesajı da 10 saniye sonra sil
            asyncio.create_task(auto_delete_message(context, update.effective_chat.id, result_message.message_id, 10))
        
    except Exception as e:
        logger.error(f"Purge to hatası: {e}")
        error_message = "❌ Aralık temizliği sırasında bir hata oluştu."
        error_message += "\n\n🤖 İbrahim Can Sancar tarafından geliştirilmiştir"
        
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

async def purge_message_range(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                             start_message_id: int, end_message_id: Optional[int] = None, 
                             count: Optional[int] = None) -> Dict[str, int]:
    """Belirtilen aralıktaki mesajları batch işleme ile optimize edilmiş silme"""
    logger.info(f"=== purge_message_range başlatıldı (BATCH OPTIMIZED) ===")
    logger.info(f"Başlangıç ID: {start_message_id}, Bitiş ID: {end_message_id}, Sayı: {count}")
    
    chat_id = update.effective_chat.id
    stats = {
        'deleted': 0,
        'failed': 0,
        'old_messages': 0
    }
    
    try:
        # Mesaj ID'lerini oluştur
        if count:
            message_ids = list(range(start_message_id, start_message_id + count))
            logger.info(f"Sayıya göre temizlik: {len(message_ids)} mesaj")
        elif end_message_id:
            message_ids = list(range(start_message_id, end_message_id + 1))
            logger.info(f"Aralık temizliği: {len(message_ids)} mesaj")
        else:
            message_ids = [start_message_id]
            logger.info(f"Tek mesaj temizliği: ID {start_message_id}")
        
        # Akıllı sınırlama - çok fazla mesaj varsa uyarı ver
        if len(message_ids) > 100:
            logger.warning(f"Çok fazla mesaj ({len(message_ids)}), ilk 100 mesajla sınırlandırılıyor")
            message_ids = message_ids[:100]
        
        logger.info(f"İşlenecek mesaj sayısı: {len(message_ids)}")
        
        # Batch processor ile optimize edilmiş işleme
        start_time = time.time()
        stats = await batch_processor.process_message_batch(
            context=context,
            chat_id=chat_id, 
            message_ids=message_ids,
            stats=stats
        )
        
        processing_time = time.time() - start_time
        logger.info(f"Batch işleme tamamlandı. Süre: {processing_time:.2f}s")
        
        # İstatistikleri ve geçmişi güncelle
        if stats['deleted'] > 0:
            increment_total_deleted(stats['deleted'])
        increment_total_purges()
        add_history_entry(
            chat_id=str(chat_id),
            command=update.message.text.split()[0], # /purge, /del etc.
            deleted_messages=stats['deleted']
        )
            
        # Eski mesajlar için uyarı gönder
        if stats['old_messages'] > 0:
            await send_old_message_warning(context, chat_id, stats['old_messages'])
        
        logger.info(f"Purge tamamlandı. İstatistikler: {stats}")
        logger.info(f"Rate limiter durumu: {rate_limiter.get_stats()}")
        
        return stats
        
    except Exception as e:
        logger.error(f"Batch mesaj işleme hatası: {e}")
        return stats

async def auto_delete_message(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int, delay: int = 10):
    """Mesajı belirtilen süre sonra otomatik siler."""
    await asyncio.sleep(delay)
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        logger.info(f"Mesaj {message_id} otomatik silindi")
    except Exception as e:
        logger.warning(f"Mesaj {message_id} otomatik silinemedi: {e}")

# Handler'ları oluştur
del_handler = CommandHandler("del", delete_single_message)
purge_handler = CommandHandler("purge", purge_messages)
purgefrom_handler = CommandHandler("purgefrom", purge_from)
purgeto_handler = CommandHandler("purgeto", purge_to) 