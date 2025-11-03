# EBEBEK BARKOD TAKİP SİSTEMİ

## Kurulum ve Çalıştırma

### Normal Python Modu

1. **Gerekli paketleri yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

2. **.env dosyasını oluşturun:**
   - `env.example.txt` dosyasını `.env` olarak kopyalayın
   - `.env` dosyasını düzenleyip `SHEET_ID` ve diğer ayarları yapın

3. **Uygulamayı çalıştırın:**
   ```bash
   python gui.py
   ```
   veya
   ```bash
   run.bat
   ```

### EXE Modu

1. **EXE oluşturmak için:**
   ```bash
   build_exe.bat
   ```
   veya
   ```bash
   pyinstaller EbebekBarkodTakip.spec
   ```

2. **EXE'yi çalıştırmak için:**
   ```bash
   run_exe.bat
   ```
   veya
   ```bash
   dist\EbebekBarkodTakip.exe
   ```

## Önemli Notlar

- `.env` dosyası EXE ile birlikte gelmelidir (aynı klasörde)
- İlk çalıştırmada `.env` dosyasını kontrol edin
- Tarayıcı otomatik olarak açılacaktır
- Port: `5002` (değiştirmek için `gui.py` dosyasındaki port numarasını düzenleyin)

## .env Dosyası Ayarları

```
SHEET_ID=your_google_sheet_id
PASSWORD_ENABLED=true
SECRET_KEY=change-this-in-production
```

## Özellikler

- ✅ Barkod okuma ve takip
- ✅ Excel'e kaydetme
- ✅ Karanlık/Aydınlık tema
- ✅ Ürün arama (metin bazlı)
- ✅ Kategori bazlı ekleme (Barkodsuz, Hasarlı, Kayıtsız)
- ✅ Manuel ürün ekleme
- ✅ Adet artırma/azaltma
- ✅ Otomatik marka formatı (büyük harf)





