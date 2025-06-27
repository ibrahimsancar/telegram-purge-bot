"""
help_texts.py - Yardım ve bilgi metinleri
"""

HELP_TEXT = """🤖 <b>Purge Bot - Komut Listesi</b>

<b>🔹 Temel Komutlar:</b>
• <code>/start</code> - Botu başlat
• <code>/help</code> - Bu yardım menüsü

<b>🗑️ Temizlik Komutları:</b>
• <code>/del</code> - Yanıtlanan mesajı sil
• <code>/purge</code> - Yanıtlanan mesajdan itibaren tüm mesajları sil
• <code>/purge [sayı]</code> - Belirtilen sayıda mesaj sil

<b>🎯 Aralık Temizliği:</b>
• <code>/purgefrom</code> - Başlangıç mesajını seç
• <code>/purgeto</code> - Bitiş mesajını seç ve aralığı temizle

<b>📊 İstatistikler:</b>
• <code>/stats</code> - Bot kullanım istatistikleri

<b>⚠️ Önemli Notlar:</b>
• Sadece adminler temizlik yapabilir
• 48 saatten eski mesajlar Telegram tarafından silinemez
• Bot komutları 1 saniye sonra otomatik silinir

🤖 <i>Bu bot İbrahim Can Sancar tarafından geliştirilmiştir</i>"""

PERMISSION_DENIED_TEXT = """❌ <b>Yetki Hatası</b>

Bu komutu kullanmak için grup adminı olmalısınız.

🤖 <i>Bu bot İbrahim Can Sancar tarafından geliştirilmiştir</i>"""

OLD_MESSAGE_WARNING_TEXT = """⚠️ <b>Eski Mesaj Uyarısı</b>

{count} adet mesaj 48 saatten eski olduğu için Telegram API tarafından silinemedi.

<b>💡 Telegram Sınırlaması:</b>
• Botlar 48 saatten eski mesajları silemez
• Bu durum Telegram'ın güvenlik politikası gereğidir
• Eski mesajlar yerine "Mesaj silindi" metni ile değiştirildi

🤖 <i>Bu bot İbrahim Can Sancar tarafından geliştirilmiştir</i>""" 