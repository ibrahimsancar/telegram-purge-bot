"""
batch_processor.py - Batch mesaj işleme modülü
Mesajları gruplar halinde işleyerek performansı artırır.
"""

import asyncio
import logging
from typing import List, Dict, Any
from telegram.ext import ContextTypes
from telegram.error import TelegramError
from .rate_limiter import rate_limiter

logger = logging.getLogger(__name__)

class BatchProcessor:
    """Batch mesaj işleme sınıfı"""
    
    def __init__(self, batch_size: int = 5, delay_between_batches: float = 0.2):
        self.batch_size = batch_size
        self.delay_between_batches = delay_between_batches
        
    async def process_message_batch(
        self, 
        context: ContextTypes.DEFAULT_TYPE,
        chat_id: int,
        message_ids: List[int],
        stats: Dict[str, int]
    ) -> Dict[str, int]:
        """Mesaj ID'lerini batch halinde işler"""
        
        # Mesajları batch'lere böl
        batches = [
            message_ids[i:i + self.batch_size] 
            for i in range(0, len(message_ids), self.batch_size)
        ]
        
        logger.info(f"Toplam {len(message_ids)} mesaj, {len(batches)} batch'te işlenecek")
        
        for batch_index, batch in enumerate(batches):
            logger.info(f"Batch {batch_index + 1}/{len(batches)} işleniyor: {len(batch)} mesaj")
            
            # Batch'teki mesajları paralel işle
            tasks = [
                self._delete_single_message(context, chat_id, msg_id, stats)
                for msg_id in batch
            ]
            
            # Paralel çalıştır
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Batch'ler arası delay
            if batch_index < len(batches) - 1:
                await asyncio.sleep(self.delay_between_batches)
                
        return stats
    
    async def _delete_single_message(
        self,
        context: ContextTypes.DEFAULT_TYPE, 
        chat_id: int, 
        message_id: int,
        stats: Dict[str, int]
    ) -> None:
        """Tek mesajı siler ve istatistikleri günceller"""
        
        # Rate limiting uygulanması
        await rate_limiter.wait_if_needed()
        
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            stats['deleted'] += 1
            rate_limiter.report_success()
            logger.debug(f"Mesaj {message_id} başarıyla silindi")
            
        except TelegramError as e:
            error_msg = str(e).lower()
            rate_limiter.report_failure(error_msg)
            
            if "message can't be deleted" in error_msg or "too old" in error_msg or "message is too old" in error_msg:
                # 2 günden eski mesajlar - bilgilendirme yap
                stats['old_messages'] += 1
                logger.debug(f"Mesaj {message_id} çok eski (2+ gün) - Telegram API kısıtlaması")
                
            elif "message to delete not found" in error_msg:
                # Mesaj bulunamadı - sessizce atla
                logger.debug(f"Mesaj {message_id} bulunamadı")
                
            elif "too many requests" in error_msg:
                # Rate limit hatası - özel davranış
                logger.warning(f"Rate limit aşıldı, mesaj {message_id} işlenemedi")
                stats['failed'] += 1
                
            else:
                # Diğer hatalar
                stats['failed'] += 1
                logger.warning(f"Mesaj {message_id} silinemedi: {e}")
                
        except Exception as e:
            stats['failed'] += 1
            rate_limiter.report_failure("unknown")
            logger.error(f"Mesaj {message_id} işlenirken hata: {e}")

# Global batch processor instance
batch_processor = BatchProcessor(batch_size=8, delay_between_batches=0.15) 