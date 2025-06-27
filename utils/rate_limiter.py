"""
rate_limiter.py - Akıllı rate limiting modülü
Telegram API limitlerini yönetir ve performansı optimize eder.
"""

import asyncio
import time
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class SmartRateLimiter:
    """Akıllı rate limiting sınıfı"""
    
    def __init__(self):
        self.last_call_time = 0.0
        self.consecutive_failures = 0
        self.consecutive_successes = 0
        self.base_delay = 0.05  # 50ms base delay
        self.max_delay = 2.0    # 2 saniye max delay
        self.backoff_multiplier = 1.5
        
    async def wait_if_needed(self) -> None:
        """Gerekirse bekleme yapar"""
        current_delay = self._calculate_delay()
        
        if current_delay > 0:
            logger.debug(f"Rate limit: {current_delay:.3f}s bekleniyor")
            await asyncio.sleep(current_delay)
            
        self.last_call_time = time.time()
    
    def report_success(self) -> None:
        """Başarılı işlem raporla"""
        self.consecutive_failures = 0
        self.consecutive_successes += 1
        
        # Başarılı işlemler delay'i azaltır (min: base_delay)
        if self.consecutive_successes > 3:
            self.base_delay = max(0.03, self.base_delay * 0.9)
            
    def report_failure(self, error_type: str = "unknown") -> None:
        """Başarısız işlem raporla"""
        self.consecutive_successes = 0
        self.consecutive_failures += 1
        
        # Rate limit hataları için özel davranış
        if "too many requests" in error_type.lower():
            self.base_delay = min(self.max_delay, self.base_delay * 2.0)
            logger.warning(f"Rate limit hit! Delay artırıldı: {self.base_delay:.3f}s")
    
    def _calculate_delay(self) -> float:
        """Mevcut delay'i hesaplar"""
        # Base delay
        delay = self.base_delay
        
        # Ardışık hatalar exponential backoff ekler
        if self.consecutive_failures > 0:
            backoff = min(
                self.max_delay, 
                delay * (self.backoff_multiplier ** self.consecutive_failures)
            )
            delay = backoff
            
        # Son çağrıdan bu yana geçen süreyi hesaba kat
        time_since_last = time.time() - self.last_call_time
        remaining_delay = max(0, delay - time_since_last)
        
        return remaining_delay
    
    def get_stats(self) -> Dict[str, any]:
        """Rate limiter istatistiklerini döndürür"""
        return {
            'base_delay': self.base_delay,
            'consecutive_failures': self.consecutive_failures,
            'consecutive_successes': self.consecutive_successes,
            'current_delay': self._calculate_delay()
        }

# Global rate limiter instance
rate_limiter = SmartRateLimiter() 