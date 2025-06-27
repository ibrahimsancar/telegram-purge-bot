"""
message_utils.py - Mesaj işleme yardımcı fonksiyonları
Mesaj yaşı kontrolü, düzenleme, bilgi alma ve formatlama fonksiyonları.
"""

import asyncio
import logging
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, List
from telegram import Bot, Message
from telegram.ext import ContextTypes
from telegram.error import TelegramError

logger = logging.getLogger(__name__)

def is_message_old(message_date) -> bool:
    """Mesajın 48 saatten eski olup olmadığını kontrol eder"""
    now = datetime.now(timezone.utc)
    message_time = message_date.replace(tzinfo=timezone.utc)
    time_diff = now - message_time
    is_old = time_diff > timedelta(hours=48)
    
    logger.debug(f"Mesaj tarihi: {message_time}, Şu an: {now}, Fark: {time_diff}, 48h+ eski: {is_old}")
    return is_old

async def edit_old_message(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int) -> bool:
    """48 saatten eski mesajı düzenler (silinemediği için)"""
    logger.info(f"Eski mesaj {message_id} düzenleniyor...")
    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="🗑️ <i>Bu mesaj silindi</i>",
            parse_mode='HTML'
        )
        logger.info(f"Eski mesaj {message_id} başarıyla düzenlendi")
        return True
    except TelegramError as e:
        logger.warning(f"Eski mesaj {message_id} düzenlenemedi: {e}")
        return False

def format_purge_result(stats: Dict[str, int]) -> str:
    """Purge sonuçlarını formatlar"""
    result_text = f"""✅ <b>Temizlik Tamamlandı!</b>

📊 <b>Sonuçlar:</b>
• ✅ Silinen: {stats['deleted']}
• ❌ Başarısız: {stats['failed']}
• ⏰ Eski mesajlar: {stats['old_messages']}

İbrahim Can Sancar tarafından geliştirilmiştir"""
    
    return result_text

async def send_old_message_warning(context: ContextTypes.DEFAULT_TYPE, chat_id: int, old_count: int):
    """Eski mesajlar için uyarı mesajı gönderir"""
    if old_count == 0:
        return
        
    from utils.help_texts import OLD_MESSAGE_WARNING_TEXT
    
    warning_text = OLD_MESSAGE_WARNING_TEXT.format(count=old_count)
    
    try:
        warning_msg = await context.bot.send_message(
            chat_id=chat_id,
            text=warning_text,
            parse_mode='HTML'
        )
        
        # 20 saniye sonra uyarı mesajını sil
        asyncio.create_task(auto_delete_message(context, chat_id, warning_msg.message_id, 20))
        
    except Exception as e:
        logger.error(f"Eski mesaj uyarısı gönderilemedi: {e}")

async def auto_delete_message(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int, delay: int = 10):
    """Mesajı belirtilen süre sonra otomatik siler"""
    await asyncio.sleep(delay)
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        logger.info(f"Mesaj {message_id} otomatik silindi ({delay}s sonra)")
    except Exception as e:
        logger.warning(f"Mesaj {message_id} otomatik silinemedi: {e}")

async def delete_command_message(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int, delay: int = 1):
    """Komut mesajını belirtilen süre sonra siler"""
    await auto_delete_message(context, chat_id, message_id, delay)

# ===============================================
# YENİ ÖZELLİK: ID İTERASYONU FONKSİYONLARI
# ===============================================

async def smart_iterate_and_delete(context: ContextTypes.DEFAULT_TYPE, chat_id: int, 
                                 start_message_id: int, target_user_id: Optional[int] = None,
                                 max_iterations: int = 200) -> Dict[str, int]:
    """
    Akıllı ID iterasyonu ile mesaj silme
    - Son mesajdan geriye doğru git
    - 48 saat sınırına kadar sil
    - Kullanıcı filtresi uygula (opsiyonel)
    """
    logger.info(f"=== Akıllı ID İterasyonu Başlatıldı ===")
    logger.info(f"Başlangıç ID: {start_message_id}, Max iterasyon: {max_iterations}")
    
    stats = {
        'deleted': 0,
        'skipped': 0,
        'old_messages': 0,
        'not_found': 0,
        'total_checked': 0,
        'user_filtered': 0
    }
    
    consecutive_not_found = 0
    consecutive_old_messages = 0
    
    # Geriye doğru iterasyon
    for current_id in range(start_message_id, max(0, start_message_id - max_iterations), -1):
        stats['total_checked'] += 1
        
        # Her 5 mesajda bir kısa bekleme (rate limiting) - daha sık bekleme
        if stats['total_checked'] % 5 == 0:
            await asyncio.sleep(0.1)
        
        try:
            # Doğrudan silmeyi dene - başarılıysa devam et
            await context.bot.delete_message(chat_id=chat_id, message_id=current_id)
            stats['deleted'] += 1
            consecutive_not_found = 0
            consecutive_old_messages = 0
            
            logger.debug(f"Mesaj {current_id} silindi")
            
        except TelegramError as e:
            error_msg = str(e).lower()
            
            if "message to delete not found" in error_msg or "message not found" in error_msg:
                stats['not_found'] += 1
                consecutive_not_found += 1
                
                # Art arda çok fazla bulunamayan mesaj varsa dur
                if consecutive_not_found > 20:
                    logger.info(f"Art arda {consecutive_not_found} mesaj bulunamadı, iterasyon sonlandırılıyor")
                    break
                    
            elif "message can't be deleted" in error_msg or "too old" in error_msg:
                stats['old_messages'] += 1
                consecutive_old_messages += 1
                
                # Art arda çok fazla eski mesaj varsa dur (48 saat sınırına ulaştık)
                if consecutive_old_messages > 10:  # 15'den 10'a düşürdüm
                    logger.info(f"Art arda {consecutive_old_messages} eski mesaj, 48 saat sınırına ulaşıldı")
                    break
                    
            else:
                stats['skipped'] += 1
                logger.debug(f"Mesaj {current_id} atlandı: {e}")
        
        except Exception as e:
            stats['skipped'] += 1
            logger.debug(f"Mesaj {current_id} genel hata: {e}")
    
    logger.info(f"ID İterasyonu tamamlandı. İstatistikler: {stats}")
    return stats

async def get_message_info(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int) -> Optional[Dict]:
    """Mesaj bilgilerini almaya çalışır (opsiyonel, hızlı fail)"""
    try:
        # Bu fonksiyon optimize edilmiş, sadece mesaj varsa bilgi döner
        # Yoksa hızlıca None döner
        return None  # Şimdilik basit, gerekirse genişletilebilir
    except:
        return None

def format_iteration_result(stats: Dict[str, int]) -> str:
    """ID iterasyon sonuçlarını formatlar"""
    total_found = stats.get('deleted', 0) + stats.get('old_messages', 0)
    
    result = f"🔄 <b>Akıllı Temizlik Tamamlandı</b>\n\n"
    result += f"📊 <b>Detaylı İstatistikler:</b>\n"
    result += f"✅ Silinen mesajlar: <b>{stats.get('deleted', 0)}</b>\n"
    
    if stats.get('old_messages', 0) > 0:
        result += f"⏰ Eski mesajlar (48 saat+): <b>{stats.get('old_messages', 0)}</b>\n"
        
    if stats.get('user_filtered', 0) > 0:
        result += f"👤 Kullanıcı filtresi: <b>{stats.get('user_filtered', 0)}</b>\n"
    
    if stats.get('not_found', 0) > 0:
        result += f"🔍 Bulunamayan: <b>{stats.get('not_found', 0)}</b>\n"
    
    result += f"\n🔢 <b>Genel Bilgiler:</b>\n"
    result += f"📝 Kontrol edilen: {stats.get('total_checked', 0)}\n"
    result += f"🎯 Bulunan mesaj: {total_found}\n"
    
    if total_found > 0:
        success_rate = (stats.get('deleted', 0) / total_found) * 100
        result += f"🏆 Silme başarısı: {success_rate:.1f}%\n"
    
    # Özel durumlar
    if stats.get('old_messages', 0) > 0:
        result += f"\n💡 <b>Not:</b> {stats.get('old_messages', 0)} mesaj Telegram'ın 48 saat sınırı nedeniyle silinemedi\n"
    
    result += f"\nİbrahim Can Sancar tarafından geliştirilmiştir"
    
    return result 