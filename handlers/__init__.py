"""
handlers/__init__.py - Handler modüllerini yükleyen ana dosya
Bu dosya tüm handler'ları import eder ve Telegram botuna ekler.
"""

from telegram.ext import Application

# Handler modüllerini import et
from .start import start_handler
from .help import help_handler
from .purge import del_handler, purge_handler, purgefrom_handler, purgeto_handler
from .stats import stats_handler
from .service_messages import service_message_handler

def register_handlers(app: Application):
    """Tüm handler'ları uygulamaya ekler"""
    
    # Temel komutlar
    app.add_handler(start_handler)
    app.add_handler(help_handler)
    
    # Silme komutları
    app.add_handler(del_handler)
    app.add_handler(purge_handler)
    app.add_handler(purgefrom_handler)
    app.add_handler(purgeto_handler)
    
    # İstatistik komutları
    app.add_handler(stats_handler)
    
    # Sistem mesajları (en son ekle - düşük öncelik)
    app.add_handler(service_message_handler) 