# 🤖 Telegram Purge Bot

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Telegram](https://img.shields.io/badge/Telegram-Bot%20API-blue.svg)](https://core.telegram.org/bots/api)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Telegram grupları için geliştirilmiş, hızlı ve güvenli mesaj temizleme botu. Grup yöneticilerinin istenmeyen mesajları kolayca silebilmesi için tasarlanmıştır.

## ✨ Özellikler

### 🗑️ Mesaj Silme Yetenekleri
- **Tek Mesaj Silme**: `/del` komutu ile yanıtlanan mesajı anında sil
- **Toplu Temizlik**: `/purge` ile belirtilen aralıktaki tüm mesajları temizle
- **Sayısal Temizlik**: `/purge [sayı]` ile belirli sayıda mesaj sil
- **Aralık Temizliği**: `/purgefrom` ve `/purgeto` komutları ile özel aralık seç

### 🛡️ Güvenlik Özellikleri
- **Admin Kontrolü**: Sadece grup yöneticileri komutları kullanabilir
- **Yaş Kontrolü**: 2 günden eski mesajlar korunur (Telegram API sınırlaması)
- **Rate Limiting**: Spam ve kötüye kullanım koruması
- **Hata Toleransı**: Silinemeyen mesajlar için akıllı hata yönetimi

### 📊 Raporlama ve İstatistikler
- **Detaylı Raporlar**: Silinen, düzenlenen ve başarısız işlemler için ayrı sayaçlar
- **Grup İstatistikleri**: `/stats` komutu ile kullanım verilerini görüntüle
- **Gerçek Zamanlı Bilgi**: Her işlem sonrası anlık durum raporu

### 🔧 Otomatik Özellikler
- **Servis Mesajları**: Katılma/ayrılma mesajlarını otomatik sil
- **Komut Temizliği**: Bot komutlarını otomatik temizle
- **Akıllı Mesaj Yönetimi**: Eski mesajları düzenle, yenileri sil

### 🌐 Web Yönetim Paneli
- **Modern Arayüz**: Responsive ve kullanıcı dostu tasarım
- **Bot Kontrolü**: Başlatma, durdurma ve yeniden başlatma
- **Token Yönetimi**: Güvenli token girişi ve görünürlük kontrolü
- **Gerçek Zamanlı Loglar**: Canlı log takibi ve otomatik yenileme

## 📋 Komutlar

### 🏠 Temel Komutlar
- `/start` - Bot hakkında genel bilgi ve hoş geldin mesajı
- `/help` - Detaylı komut rehberi ve kullanım örnekleri
- `/stats` - Bot kullanım istatistikleri ve performans bilgileri

### 🗑️ Silme Komutları
- `/del` - Yanıtlanan tek mesajı sil
- `/purge` - Yanıtlanan mesajdan son mesaja kadar toplu temizlik
- `/purge [sayı]` - Yanıtlanan mesajdan itibaren belirtilen sayıda mesaj sil
- `/purgefrom` - Aralık temizliği için başlangıç mesajını işaretle
- `/purgeto` - Aralık temizliği için bitiş mesajını işaretle ve temizliği başlat

## 🚀 Kurulum

### Gereksinimler
- Python 3.8+
- python-telegram-bot kütüphanesi
- Telegram Bot Token

### Hızlı Kurulum

1. **Repoyu klonlayın:**
```bash
git clone https://github.com/ibrahimsancar/telegram-purge-bot.git
cd telegram-purge-bot
```

2. **Gerekli paketleri yükleyin:**
```bash
pip install -r requirements.txt
```

3. **Konfigürasyon yapın:**
```bash
# config.py dosyasında bot token'ınızı ayarlayın
# settings.json dosyasında bot token'ınızı girin
```

4. **Botu çalıştırın:**
```bash
python main.py
```

### Windows için Hızlı Başlatma
```bash
# Gerekli paketleri yükle
kurulum.bat

# Botu başlat
baslat.bat
```

## 💡 Kullanım Örnekleri

### Tek Mesaj Silme
1. Silinecek mesaja yanıt verin
2. `/del` komutunu yazın
3. Mesaj anında silinir

### Toplu Temizlik
1. Başlangıç mesajına yanıt verin
2. `/purge` komutunu yazın
3. O mesajdan son mesaja kadar tümü silinir

### Belirli Sayıda Mesaj Silme
1. Herhangi bir mesaja yanıt verin
2. `/purge 20` yazın (son 20 mesajı siler)
3. İşlem tamamlandığında rapor gösterilir

### Aralık Temizliği
1. Başlangıç mesajına yanıt verip `/purgefrom` yazın
2. Bitiş mesajına yanıt verip `/purgeto` yazın
3. Belirlenen aralıktaki tüm mesajlar silinir

## 🔧 Teknik Detaylar

### Performans
- **İşleme Hızı**: 0.1 saniye gecikme ile mesaj işleme
- **Maksimum Mesaj**: Tek seferde 100 mesaja kadar
- **Bellek Kullanımı**: Minimal RAM footprint
- **API Optimizasyonu**: Telegram rate limiting'e uyum

### Güvenlik
- **Admin Kontrolü**: Otomatik yetki doğrulama
- **Mesaj Koruması**: 2 günden eski mesajları koru
- **Hata Yönetimi**: Graceful error handling
- **Log Sistemi**: Detaylı işlem kayıtları

### Uyumluluk
- **Telegram API**: Bot API 6.0+ uyumlu
- **Python**: 3.8+ sürümleri destekler
- **İşletim Sistemi**: Windows, Linux, macOS
- **Grup Türleri**: Tüm grup türlerinde çalışır

## 📞 Destek ve İletişim

### 🇹🇷 Yardım
- `/help` yazarak Türkçe detaylı yardım alabilirsiniz.
- Komut açıklamaları ve kullanım örnekleri bot içinde mevcuttur.

### Geliştirici İletişim
- **Geliştirici**: [İbrahim Can Sancar](https://github.com/ibrahimsancar)
- **İletişim**: [X (Twitter)](https://x.com/ibrahimsancar0)
- **Bug Raporu**: [GitHub Issues](https://github.com/ibrahimsancar/telegram-purge-bot/issues)

### Özellik İstekleri
- [GitHub Issues](https://github.com/ibrahimsancar/telegram-purge-bot/issues) üzerinden önerilerde bulunabilirsiniz
- Topluluk katkıları memnuniyetle karşılanır
- Pull request'ler incelenir ve entegre edilir

## 📄 Lisans

Bu proje MIT lisansı altında yayınlanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakınız.

---

🤖 **Bu bot İbrahim Can Sancar tarafından geliştirilmiştir**

💡 **İpucu**: Botun tüm özelliklerini keşfetmek için `/help` komutunu kullanmayı unutmayın!

## ⭐ Yıldız Verin

Bu projeyi beğendiyseniz, GitHub'da yıldız vermeyi unutmayın! ⭐

---

*Son güncelleme: 27 Haziran 2025*
