# 🏪 Ebebek Barkod Takip Sistemi

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)]()

> Profesyonel bir barkod takip ve raporlama sistemi. Barkodsuz, kayıtsız ve hasarlı ürünleri kolayca yönetin.

## 📋 Proje Hakkında

Ebebek Barkod Takip Sistemi, barkodsuz, kayıtsız ve hasarlı ürünleri takip etmek için geliştirilmiş profesyonel bir Python uygulamasıdır. Modern terminal arayüzü, Excel raporlama desteği ve esnek yapılandırma seçenekleri sunar.

### ✨ Özellikler

- 🔐 **Güvenli Giriş**: Google Sheets üzerinden şifre yönetimi (Opsiyonel)
- 🏷️ **Barkodsuz Ürün Takibi**: 11-13 haneli barkod ile ürün sorgulama ve adet takibi
- ❓ **Kayıtsız Barkod Takibi**: EBHJ ile başlayan 14 karakterlik barkod kaydı
- ⚠️ **Hasarlı Ürün Takibi**: Hasarlı ürünlerin barkod bazında kaydı
- 📊 **Excel Raporu**: Otomatik Excel formatında profesyonel raporlama
- 🎨 **Modern Terminal Arayüzü**: Renkli ve kullanıcı dostu arayüz
- ⚡ **Canlı İstatistikler**: Gerçek zamanlı ürün ve barkod istatistikleri
- 🎯 **API Entegrasyonu**: Ebebek API ile gerçek zamanlı ürün sorgulama

## 📸 Ekran Görüntüleri

```
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║        🏪  EBEBEK BARKOD TAKİP SİSTEMİ v2.0  📦            ║
║                                                            ║
║              ⚡ Hızlı • Güvenli • Profesyonel ⚡            ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
```

## 🚀 Hızlı Başlangıç

### Gereksinimler

- Python 3.7 veya üzeri
- Windows, macOS veya Linux
- İnternet bağlantısı (API sorguları için)

### Kurulum

1. **Projeyi klonlayın:**
```bash
git clone https://github.com/canbmaj7/ebebek-barkod-takip.git
cd ebebek-barkod-takip
```

2. **Gerekli paketleri yükleyin:**
```bash
pip install -r requirements.txt
```

3. **Yapılandırma dosyasını oluşturun:**

   **Windows için:**
   ```bash
   copy .env.example .env
   ```

   **Linux/Mac için:**
   ```bash
   cp .env.example .env
   ```

4. **Projeyi çalıştırın:**
```bash
python ebebek.py
```

## ⚙️ Yapılandırma

### Şifre Kontrolünü Kapatma (Demo Modu)

Projeyi şifre olmadan kullanmak için `.env` dosyasını düzenleyin:

```env
PASSWORD_ENABLED=false
```

**Varsayılan olarak şifre kontrolü aktif değildir.** İlk kullanıcılar için demo modu açıktır.

### Şifre Kontrolünü Aktif Etme

1. `.env` dosyasını düzenleyin:
```env
PASSWORD_ENABLED=true
SHEET_ID=KENDI_SHEET_ID_NIZ
```

2. Google Sheets oluşturun ve ilk satır B1 hücresine şifrenizi yazın

3. Sheet ID'yi URL'den alın:
```
https://docs.google.com/spreadsheets/d/SHEET_ID_BURASI/gviz/tq?tqx=out:csv&sheet=Sheet1
```

## 📖 Kullanım

### Ana Menü

Program başlatıldığında ana menü görüntülenir:

```
+=======================================================+
|                   📋 İŞLEM MENÜSÜ                   |
+=======================================================+
|                                                       |
|  【1】 ➜  🏷️  Barkodsuzlar │ 11-13 haneli barkod   |
|  【2】 ➜  ❓ Kayıtsızlar  │ EBHJ ile başlayan     |
|  【3】 ➜  ⚠️  Hasarlılar   │ 11-13 haneli barkod   |
|  【4】 ➜  💾 Kaydet & Çık │ Excel dosyası oluştur |
|                                                       |
+=======================================================+
```

### Barkodsuzlar (Seçenek 1)

11 veya 13 haneli barkod girererek ürün bilgilerini sorgulayın:
- Barkod sisteme kaydedilir
- API'den ürün bilgileri çekilir
- Adet takibi otomatik yapılır

**Örnek:** `8691234567890`

### Kayıtsızlar (Seçenek 2)

EBHJ ile başlayan 14 karakterlik barkodları kaydedin:
- Özel format: `EBHJ` + 10 rakam
- Adet takibi yok (liste formatında)

**Örnek:** `EBHJ1003942527`

### Hasarlılar (Seçenek 3)

Hasarlı ürünleri kaydedin:
- 11 veya 13 haneli barkod
- API'den ürün bilgileri alınır
- Adet takibi yapılır

### Excel Raporu (Seçenek 4)

Tüm verileri Excel formatında kaydeder:
- `BARKODSUZLAR` sayfası: Tarih, İçerik, Adet
- `KAYITSIZLAR` sayfası: Barkod listesi
- `HASARLILAR` sayfası: Tarih, İçerik, Adet

**Dosya adı formatı:** `EBEBEK DD.MM.YYYY.xlsx`

## 📊 Excel Rapor Yapısı

### BARKODSUZLAR Sayfası
| TARİH | İÇERİK | ADET |
|-------|--------|------|
| 15.01.2024 | Bebek Bezi Premium | 3 |

### KAYITSIZLAR Sayfası
| BARKODLAR | BARKODLAR | BARKODLAR |
|-----------|-----------|-----------|
| EBHJ1003942527 | EBHJ1003942528 | EBHJ1003942529 |

### HASARLILAR Sayfası
| TARİH | İÇERİK | ADET |
|-------|--------|------|
| 15.01.2024 | Oyuncak Seti | 2 |

## 🔧 API Yapılandırması

Program, Ebebek API'sini kullanır:

- **API URL:** `https://ebebek.wawlabs.com/autocomplete`
- **Sorgu:** `?q=BARKOD_NUMARASI`
- **Format:** JSON

### API Kullanımı

```python
import requests

url = "https://ebebek.wawlabs.com/autocomplete"
barkod = "8691234567890"
response = requests.get(f"{url}?q={barkod}")
data = response.json()
```

## 📦 Bağımlılıklar

| Paket | Versiyon | Açıklama |
|-------|----------|----------|
| requests | 2.31.0 | HTTP istekleri için |
| pandas | 2.1.3 | Veri işleme |
| openpyxl | 3.1.2 | Excel dosyası oluşturma |
| colorama | 0.4.6 | Terminal renklendirme |
| python-dotenv | 1.0.0 | Environment variable yönetimi |

## 🛡️ Güvenlik

### Şifre Yönetimi

- Şifre Google Sheets üzerinden dinamik olarak alınır
- Şifre girişi terminalde gizlenir (getpass)
- Her girişte doğrulama yapılır
- Demo modu şifre kontrolünü devre dışı bırakır

### .env Dosyası

`.env` dosyası git'e eklenmez (`.gitignore`'da). Hassas bilgileri `.env` dosyasında saklayın:

```env
# Şifre kontrolünü kapat (Demo modu)
PASSWORD_ENABLED=false

# Veya şifre kontrolünü aktif et
PASSWORD_ENABLED=true
SHEET_ID=your_sheet_id_here
```

## 📁 Proje Yapısı

```
ebebek-barkod-takip/
│
├── ebebek.py              # Ana uygulama dosyası
├── requirements.txt        # Python bağımlılıkları
├── .env                    # Yapılandırma dosyası (git'te yok)
├── .env.example           # Örnek yapılandırma dosyası
├── .gitignore             # Git ignore kuralları
├── README.md              # Bu dosya
└── *.xlsx                 # Oluşturulan Excel raporları (git'te yok)
```

## 🐛 Bilinen Sorunlar ve Çözümler

### Terminal Encoding Hatası

**Sorun:** Windows'ta Türkçe karakterler görünmüyor.

**Çözüm:** Kod otomatik encoding düzeltmesi yapıyor. Eğer sorun devam ederse:
```bash
chcp 65001
```

### API Bağlantı Hatası

**Sorun:** `✗ API hatası: 503`

**Çözüm:** 
- İnternet bağlantınızı kontrol edin
- Ebebek API'sinin çalıştığından emin olun
- VPN kullanıyor musanız kapatmayı deneyin

### Şifre Yüklenemedi

**Sorun:** `✗ HATA: Şifre yüklenemedi!`

**Çözüm:**
- `.env` dosyasında `PASSWORD_ENABLED=false` yapın
- İnternet bağlantınızı kontrol edin
- Google Sheets'in public olduğundan emin olun

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen önce bir issue açın.

### Geliştirme

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Commit edin (`git commit -m 'Add some AmazingFeature'`)
4. Push edin (`git push origin feature/AmazingFeature`)
5. Pull Request açın

## 📝 Changelog

### v2.0.0 (Ocak 2024)
- ✨ Şifre kontrolü opsiyonel hale getirildi
- ✨ .env dosyası desteği eklendi
- ✨ Demo modu desteği
- 🐛 Terminal encoding sorunları düzeltildi
- 📊 İstatistik görselleştirme iyileştirildi

### v1.0.0
- 🎉 İlk release
- Temel barkod takip özellikleri
- Excel raporlama

## 👤 Geliştirici

**Ahmet Can Otlu**
- GitHub: [@canbmaj7](https://github.com/canbmaj7)
- Email: ahmetcanotlu@gmail.com

## 📄 Lisans

Bu proje özel kullanım içindir. Tüm hakları saklıdır.

## 🙏 Teşekkürler

- Ebebek API ekibine teşekkürler
- Tüm katkıda bulunanlara teşekkürler

## 📞 İletişim

Sorularınız için [issue açın](https://github.com/canbmaj7/ebebek-barkod-takip/issues) veya email gönderin.

---

**⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın!**
