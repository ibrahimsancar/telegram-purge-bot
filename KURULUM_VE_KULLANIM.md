# 📚 Telegram Purge Bot - Kurulum ve Kullanım Kılavuzu

## 📋 İçindekiler

- [🎯 Proje Hakkında](#-proje-hakkında)
- [🚀 Hızlı Başlangıç](#-hızlı-başlangıç)
- [⚙️ Detaylı Kurulum](#️-detaylı-kurulum)
- [🤖 Bot Komutları](#-bot-komutları)
- [🌐 Web Yönetim Paneli](#-web-yönetim-paneli)
- [🔧 Yapılandırma](#-yapılandırma)
- [🐛 Sorun Giderme](#-sorun-giderme)
- [📞 Destek](#-destek)

---

## 🎯 Proje Hakkında

Telegram Purge Bot, grup yöneticilerinin istenmeyen mesajları hızlı ve güvenli bir şekilde temizlemesi için geliştirilmiş bir Telegram botudur.

### ✨ Özellikler
- **Hızlı Mesaj Silme**: Tek tıkla toplu mesaj temizliği
- **Güvenli**: Sadece admin yetkisi olan kullanıcılar
- **Akıllı**: 48 saat kuralına uyum
- **Web Paneli**: Modern yönetim arayüzü
- **Gerçek Zamanlı**: Canlı log takibi

---

## 🚀 Hızlı Başlangıç

### 1️⃣ Bot Token'ı Alın
1. Telegram'da [@BotFather](https://t.me/BotFather) ile konuşun
2. `/newbot` komutunu gönderin
3. Bot adı ve kullanıcı adı belirleyin
4. Size verilen token'ı kaydedin

### 2️⃣ Projeyi İndirin
```bash
git clone https://github.com/ibrahimsancar/telegram-purge-bot.git
cd telegram-purge-bot
```

### 3️⃣ Kurulum Yapın
```bash
# Windows
kurulum.bat

# Linux/Mac
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4️⃣ Bot Token'ını Ayarlayın
`settings.json` dosyasını düzenleyin:
```json
{
    "bot_token": "YOUR_BOT_TOKEN_HERE",
    "delete_service_messages": false
}
```

### 5️⃣ Botu Başlatın
```bash
# Windows
baslat.bat

# Linux/Mac
python main.py
```

---

## ⚙️ Detaylı Kurulum

### Sistem Gereksinimleri
- **Python**: 3.8 veya üzeri
- **İşletim Sistemi**: Windows, Linux, macOS
- **İnternet**: Aktif bağlantı
- **Disk Alanı**: En az 100MB

### Windows Kurulumu

#### Otomatik Kurulum (Önerilen)
1. `kurulum.bat` dosyasını çift tıklayın
2. Kurulum tamamlanana kadar bekleyin
3. Hata durumunda aşağıdaki manuel kurulumu deneyin

#### Manuel Kurulum
```cmd
# Python kontrolü
python --version

# Sanal ortam oluşturma
python -m venv .venv

# Sanal ortam aktifleştirme
.venv\Scripts\activate

# Paket yükleme
pip install -r requirements.txt
```

### Linux/macOS Kurulumu
```bash
# Python kontrolü
python3 --version

# Sanal ortam oluşturma
python3 -m venv .venv

# Sanal ortam aktifleştirme
source .venv/bin/activate

# Paket yükleme
pip install -r requirements.txt
```

### Bot Token'ı Ayarlama
1. `settings.json` dosyasını açın
2. `"bot_token"` alanına bot token'ınızı yazın
3. Dosyayı kaydedin

```json
{
    "bot_token": "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
    "delete_service_messages": false
}
```

---

## 🤖 Bot Komutları

### 🏠 Temel Komutlar

#### `/start`
- **Açıklama**: Botu başlatır ve hoş geldin mesajı gösterir
- **Kullanım**: `/start`
- **Yetki**: Herkes
- **Örnek**: `/start`

#### `/help`
- **Açıklama**: Detaylı yardım menüsünü gösterir
- **Kullanım**: `/help`
- **Yetki**: Herkes
- **Örnek**: `/help`

#### `/stats`
- **Açıklama**: Bot kullanım istatistiklerini gösterir
- **Kullanım**: `/stats`
- **Yetki**: Herkes
- **Örnek**: `/stats`

### 🗑️ Mesaj Silme Komutları

#### `/del`
- **Açıklama**: Tek mesaj siler
- **Kullanım**: Silinecek mesaja yanıt vererek `/del`
- **Yetki**: Sadece adminler
- **Örnek**: 
  ```
  [Mesaja yanıt ver] → /del
  ```

#### `/purge`
- **Açıklama**: Toplu mesaj temizliği yapar
- **Kullanım 1**: Yanıtlanan mesajdan itibaren en son mesaja kadar siler
- **Kullanım 2**: Belirtilen sayıda mesaj siler
- **Yetki**: Sadece adminler
- **Örnekler**:
  ```
  [Mesaja yanıt ver] → /purge
  [Mesaja yanıt ver] → /purge 10
  ```

#### `/purgefrom` ve `/purgeto`
- **Açıklama**: Belirtilen aralıktaki mesajları siler
- **Kullanım**: 
  1. Başlangıç mesajına yanıt vererek `/purgefrom`
  2. Bitiş mesajına yanıt vererek `/purgeto`
- **Yetki**: Sadece adminler
- **Örnek**:
  ```
  [Başlangıç mesajına yanıt] → /purgefrom
  [Bitiş mesajına yanıt] → /purgeto
  ```

---

## 🌐 Web Yönetim Paneli

### Erişim
- **URL**: http://127.0.0.1:8001
- **Başlatma**: `baslat.bat` çalıştırın
- **Tarayıcı**: Otomatik açılır

### Özellikler

#### 🤖 Bot Kontrolü
- **Başlat**: Botu çalıştırır
- **Durdur**: Botu durdurur
- **Yeniden Başlat**: Botu yeniden başlatır

#### 🔑 Token Yönetimi
- **Token Girişi**: Güvenli token girişi
- **Görünürlük Kontrolü**: Göz butonu ile token göster/gizle
- **Kaydet**: Token'ı kaydeder
- **Kısayolları Ekle**: Bot komutlarını ayarlar

#### ⚙️ Ayarlar
- **Servis Mesajları**: Otomatik servis mesajı silme
- **Toggle Kontrolü**: Açık/kapalı durumu

#### 📊 Canlı Loglar
- **Gerçek Zamanlı**: Anlık log takibi
- **Otomatik Yenileme**: Belirli aralıklarla güncelleme
- **Manuel Yenileme**: Yenile butonu
- **Log Seviyeleri**: Renkli log kategorileri

### Kullanım Adımları
1. `baslat.bat` dosyasını çalıştırın
2. Tarayıcıda http://127.0.0.1:8001 adresine gidin
3. Bot token'ınızı girin ve kaydedin
4. "Başlat" butonuna tıklayın
5. Bot durumunu takip edin

---

## 🔧 Yapılandırma

### settings.json Ayarları

```json
{
    "bot_token": "YOUR_BOT_TOKEN_HERE",
    "delete_service_messages": false
}
```

#### Parametreler
- **bot_token**: Bot token'ınız (zorunlu)
- **delete_service_messages**: Servis mesajlarını otomatik silme (opsiyonel)

### config.py Ayarları

```python
# Log Seviyesi
LOG_LEVEL = "INFO"

# Web Panel Ayarları
WEB_HOST = "127.0.0.1"
WEB_PORT = 8001

# Rate Limiting
RATE_LIMIT_DELAY = 0.1

# Maksimum Mesaj Sayısı
MAX_MESSAGES_PER_REQUEST = 100
```

### Ortam Değişkenleri
```bash
# Log dosya isimleri için
export ENV=production  # purge_bot_production.log
export ENV=development # purge_bot_development.log (varsayılan)
```

---

## 🐛 Sorun Giderme

### Yaygın Sorunlar

#### ❌ "Python kurulu değil" Hatası
**Çözüm:**
1. Python'u https://python.org adresinden indirin
2. Kurulum sırasında "Add Python to PATH" seçeneğini işaretleyin
3. Bilgisayarı yeniden başlatın

#### ❌ "Sanal ortam aktifleştirilemedi" Hatası
**Çözüm:**
1. `kurulum.bat` dosyasını tekrar çalıştırın
2. Yönetici olarak çalıştırmayı deneyin
3. Antivirüs programını geçici olarak devre dışı bırakın

#### ❌ "Gerekli paketler yüklenemedi" Hatası
**Çözüm:**
1. İnternet bağlantınızı kontrol edin
2. Proxy ayarlarınızı kontrol edin
3. Manuel olarak pip install -r requirements.txt çalıştırın

#### ❌ "Bot token geçersiz" Hatası
**Çözüm:**
1. Bot token'ınızı @BotFather'dan tekrar alın
2. settings.json dosyasında doğru formatta olduğunu kontrol edin
3. Token'ın başında ve sonunda fazladan boşluk olmadığından emin olun

#### ❌ "Port 8001 kullanımda" Hatası
**Çözüm:**
1. Diğer uygulamaları kapatın
2. Bilgisayarı yeniden başlatın
3. config.py dosyasında farklı port belirleyin

#### ❌ "Bot mesaj gönderemiyor" Hatası
**Çözüm:**
1. Botu gruba admin olarak eklediğinizden emin olun
2. Bot'a şu yetkileri verin:
   - Mesajları silme
   - Mesajları okuma
   - Mesaj gönderme
3. Bot'un aktif olduğunu kontrol edin

### Log Dosyaları
- **Bot Logları**: `logs/purge_bot_development.log`
- **Web Logları**: `logs/web_development.log`
- **Hata Detayları**: Log dosyalarını inceleyin

### Performans Sorunları
- **Yavaş Mesaj Silme**: Rate limiting ayarlarını kontrol edin
- **Yüksek CPU Kullanımı**: Maksimum mesaj sayısını azaltın
- **Bellek Sorunları**: Log dosyalarını temizleyin

---

## 📞 Destek

### İletişim
- **Geliştirici**: [İbrahim Can Sancar](https://github.com/ibrahimsancar)
- **İletişim**: [X (Twitter)](https://x.com/ibrahimsancar0)
- **GitHub Issues**: [Proje Sayfası](https://github.com/ibrahimsancar/telegram-purge-bot/issues)

### Hata Bildirimi
Hata bildirirken şu bilgileri ekleyin:
- **Hata açıklaması**: Ne oldu?
- **Beklenen davranış**: Ne olması gerekiyordu?
- **Adımlar**: Hatayı nasıl tekrarlayabilirim?
- **Sistem bilgileri**: İşletim sistemi, Python sürümü
- **Log dosyaları**: Varsa hata logları

### Özellik İsteği
Yeni özellik önerirken:
- **Özellik açıklaması**: Ne yapması gerekiyor?
- **Kullanım senaryosu**: Nasıl kullanılacak?
- **Fayda**: Ne gibi avantajlar sağlayacak?

---

## 📋 Önemli Notlar

### 🔐 Güvenlik
- Bot token'ınızı kimseyle paylaşmayın
- settings.json dosyasını güvenli tutun
- Düzenli olarak bot token'ınızı yenileyin

### 📅 Telegram Sınırlamaları
- **48 Saat Kuralı**: 48 saatten eski mesajlar silinemez
- **Rate Limiting**: API sınırlarına uyum gerekir
- **Admin Yetkisi**: Sadece adminler komutları kullanabilir

### ⏱️ Otomatik İşlemler
- Bot komutları 1 saniye sonra otomatik silinir
- Sonuç mesajları 10 saniye sonra otomatik silinir
- Uyarı mesajları 20 saniye sonra otomatik silinir

### 🚀 Performans
- **Batch İşleme**: Mesajlar 8'li gruplar halinde işlenir
- **Rate Limiting**: API sınırlarına uyum için otomatik gecikme
- **Akıllı Hata Yönetimi**: Hataları otomatik olarak yönetir

---

## 🎉 Başarı!

Artık Telegram Purge Bot'unuzu kullanmaya hazırsınız! 

### İlk Adımlar
1. ✅ Kurulum tamamlandı
2. ✅ Bot token'ı ayarlandı
3. ✅ Web panel erişimi sağlandı
4. 🚀 Botu başlatın ve kullanmaya başlayın!

### Yardım
- **Komutlar**: `/help` yazarak bot içinde yardım alın
- **Web Panel**: http://127.0.0.1:8001 adresinden yönetin
- **Dokümantasyon**: Bu dosyayı referans olarak kullanın

---

*Bu kılavuz sürekli güncellenmektedir. Son güncelleme: 27 Ocak 2025* 