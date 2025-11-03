import os
import requests
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask import jsonify
from functools import wraps
from dotenv import load_dotenv

# İş mantığı ve veri yapıları ebebek.py'den alınır
from ebebek import (
    get_password_from_sheets,
    user_login,  # kullanılmıyor ama import güvenli
    validate_barkodsuz,
    validate_kayitsiz,
    query_product,
    add_barkodsuz,
    add_hasarli,
    add_kayitsiz,
    get_stats,
    save_to_excel,
    barkodsuz_dict,
    kayıtsız_list,
    hasarli_dict,
)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

# Sunucu tarafı "Eklenenler" durumu (kategori+barkod bazında adet biriktirir)
eklenenler = {}  # key: f"{kategori}:{barkod}" -> {title, brand, image_link, barkod, kategori, adet}

def format_brand_name(brand_name):
    """Marka adının her kelimesinin baş harfini büyük yapar"""
    if not brand_name:
        return ""
    # Her kelimenin ilk harfini büyük yap
    return " ".join(word.capitalize() for word in str(brand_name).split())


def is_password_enabled():
    return os.getenv('PASSWORD_ENABLED', 'false').lower() == 'true'


# Jinja filtre: ebebek CDN 96x96 görsellerini 96'nın katına ölçekle
@app.template_filter('resize96')
def resize96(url, multiplier=2):
    try:
        mult = int(multiplier)
        if mult < 1:
            mult = 1
        size = 96 * mult
        # sadece "/96/96/" geçen linklerde değiştir
        return url.replace('/96/96/', f'/{size}/{size}/') if isinstance(url, str) else url
    except Exception:
        return url


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Eğer şifre kontrolü aktif değilse, direkt erişime izin ver
        if not is_password_enabled():
            return fn(*args, **kwargs)
        # Eğer kullanıcı giriş yapmışsa, erişime izin ver
        if session.get('logged_in'):
            return fn(*args, **kwargs)
        # Giriş yapılmamışsa, ana sayfaya yönlendir (login sayfası gösterilecek)
        return redirect(url_for('index'))
    return wrapper


@app.route('/api/login', methods=['POST'])
def api_login():
    """JSON tabanlı login endpoint - hepsiburada tarzı"""
    # Eğer şifre kontrolü aktif değilse, otomatik login yap
    if not is_password_enabled():
        session['logged_in'] = True
        return jsonify({'success': True, 'message': 'Giriş başarılı', 'redirect': '/'})
    
    data = request.get_json(silent=True) or {}
    password = data.get('password', '').strip()
    
    if not password:
        return jsonify({'success': False, 'error': 'Şifre boş olamaz'}), 400
    
    # Şifreyi Google Sheets'ten al
    correct_password = get_password_from_sheets()
    
    if correct_password is None:
        return jsonify({'success': False, 'error': 'Şifre yüklenemedi. İnternet veya SHEET_ID ayarını kontrol edin.'}), 500
    
    if password == correct_password:
        session['logged_in'] = True
        return jsonify({'success': True, 'message': 'Şifre doğru', 'redirect': '/'})
    else:
        return jsonify({'success': False, 'error': 'Yanlış şifre!'}), 401


@app.route('/login', methods=['GET'])
def login_redirect():
    """Eski /login route'u için redirect - geriye dönük uyumluluk"""
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.clear()
    flash('Oturum kapatıldı.', 'info')
    return redirect(url_for('index'))


@app.route('/')
def index():
    # Şifre kontrolü - giriş yapılmamışsa login sayfası göster
    if is_password_enabled() and not session.get('logged_in'):
        return render_template('login.html')
    # Giriş yapılmışsa ana sayfayı göster
    stats = get_stats()
    # eklenenleri liste olarak ilet
    eklenenler_list = list(eklenenler.values())
    return render_template('index.html', stats=stats, eklenenler=eklenenler_list)


@app.route('/add/barkodsuz', methods=['POST'])
@login_required
def add_barkodsuz_route():
    barkod = request.form.get('barkod', '').strip()
    ok, msg = validate_barkodsuz(barkod)
    if not ok:
        flash(msg, 'danger')
        return redirect(url_for('index'))

    product = query_product(barkod)
    if not product:
        flash(f"{barkod} için ürün bulunamadı.", 'warning')
        return redirect(url_for('index'))

    adet = add_barkodsuz(barkod, product)
    flash(f"Ürün eklendi. Adet: {adet}", 'success')
    return redirect(url_for('index'))


@app.route('/add/hasarli', methods=['POST'])
@login_required
def add_hasarli_route():
    barkod = request.form.get('barkod', '').strip()
    ok, msg = validate_barkodsuz(barkod)
    if not ok:
        flash(msg, 'danger')
        return redirect(url_for('index'))

    product = query_product(barkod)
    if not product:
        flash(f"{barkod} için ürün bulunamadı.", 'warning')
        return redirect(url_for('index'))

    adet = add_hasarli(barkod, product)
    flash(f"Hasarlı ürün eklendi. Adet: {adet}", 'success')
    return redirect(url_for('index'))


@app.route('/add/kayitsiz', methods=['POST'])
@login_required
def add_kayitsiz_route():
    barkod = request.form.get('barkod', '').strip()
    ok, msg = validate_kayitsiz(barkod)
    if not ok:
        flash(msg, 'danger')
        return redirect(url_for('index'))
    yeni = add_kayitsiz(barkod)
    if yeni:
        flash('Kayıtsız barkod eklendi.', 'success')
    else:
        flash('Bu barkod zaten kayıtlı.', 'info')
    return redirect(url_for('index'))


@app.route('/save')
@login_required
def save_route():
    # Mevcut fonksiyon dosyayı oluşturup kaydeder
    if not barkodsuz_dict and not kayıtsız_list and not hasarli_dict:
        flash('Kaydedilecek veri yok.', 'warning')
        return redirect(url_for('index'))
    
    try:
        # EXE içinde çalışırken dosya yolunu düzelt
        import sys
        if getattr(sys, 'frozen', False):
            # EXE modunda - EXE'nin çalıştığı dizine kaydet
            base_path = os.path.dirname(sys.executable)
        else:
            # Normal modda - script'in bulunduğu dizine kaydet
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        # Mevcut dizini kaydet
        original_dir = os.getcwd()
        
        # Dizin değiştir
        os.chdir(base_path)
        
        # Dosya listesini al
        before = set(os.listdir('.'))
        
        # Excel dosyasını oluştur
        save_to_excel()
        
        # Yeni dosyaları bul
        after = set(os.listdir('.'))
        created = list(after - before)
        created = [f for f in created if f.endswith('.xlsx') and f.startswith('EBEBEK')]
        
        # Orijinal dizine dön
        os.chdir(original_dir)
        
        if not created:
            flash('Dosya oluşturulamadı.', 'danger')
            return redirect(url_for('index'))
        
        # En son oluşturulanı seç ve tam yolunu al
        created.sort(key=lambda x: os.path.getmtime(os.path.join(base_path, x)), reverse=True)
        file_path = os.path.join(base_path, created[0])
        
        return send_file(file_path, as_attachment=True)
    
    except Exception as e:
        import traceback
        error_msg = f"Dosya kaydedilirken hata oluştu: {str(e)}"
        print(f"ERROR: {error_msg}")
        print(traceback.format_exc())
        flash(error_msg, 'danger')
        return redirect(url_for('index'))


# --- JSON API: Sayfa yenilenmeden ekleme akışları ---
@app.route('/api/add/barkodsuz', methods=['POST'])
@login_required
def api_add_barkodsuz():
    data = request.get_json(silent=True) or {}
    barkod = (data.get('barkod') or '').strip()
    ok, msg = validate_barkodsuz(barkod)
    if not ok:
        return jsonify({'ok': False, 'message': msg}), 400
    product = query_product(barkod)
    if not product:
        return jsonify({'ok': False, 'message': f"{barkod} için ürün bulunamadı."}), 404
    adet = add_barkodsuz(barkod, product)
    stats = get_stats()
    key = f"barkodsuz:{barkod}"
    item = eklenenler.get(key)
    if not item:
        # Marka adını formatla
        formatted_brand = format_brand_name(product.get('brand', ''))
        eklenenler[key] = {
            'title': product.get('title'),
            'brand': formatted_brand,
            'image_link': product.get('image_link'),
            'barkod': barkod,
            'kategori': 'barkodsuz',
            'adet': adet,
        }
    else:
        eklenenler[key]['adet'] = adet
    return jsonify({
        'ok': True,
        'message': 'Ürün eklendi',
        'adet': adet,
        'card': {
            'title': product.get('title'),
            'brand': format_brand_name(product.get('brand', '')),
            'image_link': product.get('image_link'),
            'stock_status': product.get('stock_status'),
            'price': product.get('price'),
            'barkod': barkod,
        },
        'stats': stats,
        'eklenenler': list(eklenenler.values()),
    })


@app.route('/api/add/hasarli', methods=['POST'])
@login_required
def api_add_hasarli():
    data = request.get_json(silent=True) or {}
    barkod = (data.get('barkod') or '').strip()
    ok, msg = validate_barkodsuz(barkod)
    if not ok:
        return jsonify({'ok': False, 'message': msg}), 400
    product = query_product(barkod)
    if not product:
        return jsonify({'ok': False, 'message': f"{barkod} için ürün bulunamadı."}), 404
    adet = add_hasarli(barkod, product)
    stats = get_stats()
    key = f"hasarli:{barkod}"
    item = eklenenler.get(key)
    if not item:
        # Marka adını formatla
        formatted_brand = format_brand_name(product.get('brand', ''))
        eklenenler[key] = {
            'title': product.get('title'),
            'brand': formatted_brand,
            'image_link': product.get('image_link'),
            'barkod': barkod,
            'kategori': 'hasarli',
            'adet': adet,
        }
    else:
        eklenenler[key]['adet'] = adet
    return jsonify({
        'ok': True,
        'message': 'Hasarlı ürün eklendi',
        'adet': adet,
        'card': {
            'title': product.get('title'),
            'brand': format_brand_name(product.get('brand', '')),
            'image_link': product.get('image_link'),
            'stock_status': product.get('stock_status'),
            'price': product.get('price'),
            'barkod': barkod,
        },
        'stats': stats,
        'eklenenler': list(eklenenler.values()),
    })


@app.route('/api/add/kayitsiz', methods=['POST'])
@login_required
def api_add_kayitsiz():
    data = request.get_json(silent=True) or {}
    barkod = (data.get('barkod') or '').strip()
    ok, msg = validate_kayitsiz(barkod)
    if not ok:
        return jsonify({'ok': False, 'message': msg}), 400
    yeni = add_kayitsiz(barkod)
    stats = get_stats()
    key = f"kayitsiz:{barkod}"
    item = eklenenler.get(key)
    if not item:
        eklenenler[key] = {
            'title': barkod,
            'brand': '',
            'image_link': '',
            'barkod': barkod,
            'kategori': 'kayitsiz',
            'adet': 1,
        }
    # zaten kayıtlıysa adet artırmayız (kayıtsız listede tekil tutuluyor)
    return jsonify({
        'ok': True,
        'message': 'Eklendi' if yeni else 'Zaten kayıtlı',
        'yeni': yeni,
        'barkod': barkod,
        'stats': stats,
        'eklenenler': list(eklenenler.values()),
    })


@app.route('/api/eklenenler/delete', methods=['POST'])
@login_required
def api_eklenenler_delete():
    data = request.get_json(silent=True) or {}
    key = (data.get('key') or '').strip()
    if not key:
        return jsonify({'ok': False, 'message': 'Key gerekli'}), 400
    if key in eklenenler:
        # Önce ana veri yapılarından sil
        try:
            kategori, barkod = key.split(':', 1)
        except ValueError:
            kategori, barkod = None, None
        if kategori == 'barkodsuz' and barkod in barkodsuz_dict:
            del barkodsuz_dict[barkod]
        elif kategori == 'hasarli' and barkod in hasarli_dict:
            del hasarli_dict[barkod]
        elif kategori == 'kayitsiz' and barkod in kayıtsız_list:
            try:
                kayıtsız_list.remove(barkod)
            except ValueError:
                pass
        # Eklenenler listesinden de sil
        del eklenenler[key]
        stats = get_stats()
        return jsonify({'ok': True, 'eklenenler': list(eklenenler.values()), 'stats': stats})
    return jsonify({'ok': False, 'message': 'Kayıt bulunamadı'}), 404


@app.route('/reset', methods=['POST'])
@login_required
def reset_all():
    barkodsuz_dict.clear()
    hasarli_dict.clear()
    kayıtsız_list.clear()
    eklenenler.clear()
    flash('Tüm veriler sıfırlandı.', 'info')
    return redirect(url_for('index'))


@app.route('/api/eklenenler/manual_add', methods=['POST'])
@login_required
def api_manual_add():
    data = request.get_json(silent=True) or {}
    kategori = (data.get('kategori') or '').strip()
    barkod = (data.get('barkod') or '').strip()
    title = (data.get('title') or '').strip()
    brand = (data.get('brand') or '').strip()
    # Marka adını formatla
    brand = format_brand_name(brand)
    image_link = (data.get('image_link') or '').strip()
    try:
        qty = int(data.get('adet') or 1)
    except Exception:
        qty = 0

    if kategori not in ['barkodsuz', 'hasarli', 'kayitsiz']:
        return jsonify({'ok': False, 'message': 'Geçersiz kategori'}), 400
    
    # Barkod sadece kayıtsız için zorunlu
    if kategori == 'kayitsiz':
        if not barkod:
            return jsonify({'ok': False, 'message': 'Kayıtsız için barkod gereklidir'}), 400
    
    # Barkod yoksa otomatik oluştur (barkodsuz/hasarli için)
    if not barkod and kategori in ['barkodsuz', 'hasarli']:
        import uuid
        barkod = f"MANUAL_{uuid.uuid4().hex[:10].upper()}"
    
    if kategori in ['barkodsuz', 'hasarli']:
        # Adet varsa kullan, yoksa 1
        if qty < 1:
            qty = 1
        # Ürün adı yoksa barkod kullan
        if not title:
            title = barkod

    if kategori == 'barkodsuz':
        # Ürün bilgisi yoksa API'den getir
        product = {'title': title, 'brand': brand, 'image_link': image_link}
        for _ in range(qty):
            add_barkodsuz(barkod, product)
        title = product.get('title')
        brand = product.get('brand')
        image_link = product.get('image_link')
    elif kategori == 'hasarli':
        product = {'title': title, 'brand': brand, 'image_link': image_link}
        for _ in range(qty):
            add_hasarli(barkod, product)
        title = product.get('title')
        brand = product.get('brand')
        image_link = product.get('image_link')
    else:
        # kayıtsız - EBHJ ile başlamalı ve 14 karakter olmalı
        ok, msg = validate_kayitsiz(barkod)
        if not ok:
            return jsonify({'ok': False, 'message': msg}), 400
        add_kayitsiz(barkod)

    # eklenenler sözlüğünü güncelle
    key = f"{kategori}:{barkod}"
    item = eklenenler.get(key)
    if not item:
        eklenenler[key] = {
            'title': title or barkod,
            'brand': brand,
            'image_link': image_link,
            'barkod': barkod,
            'kategori': kategori,
            'adet': qty if kategori != 'kayitsiz' else 1,
        }
    else:
        if kategori != 'kayitsiz':
            eklenenler[key]['adet'] += qty

    stats = get_stats()
    return jsonify({'ok': True, 'eklenenler': list(eklenenler.values()), 'stats': stats})


@app.route('/api/eklenenler/decrement', methods=['POST'])
@login_required
def api_eklenenler_decrement():
    data = request.get_json(silent=True) or {}
    key = data.get('key', '').strip() if isinstance(data.get('key'), str) else str(data.get('key', '')).strip()
    if not key:
        return jsonify({'ok': False, 'message': 'Key gerekli'}), 400
    
    # Key'deki escape karakterlerini temizle (HTML attribute'dan gelen escape karakterleri)
    import re
    # \" ile başlayıp \" ile bitiyorsa, bunları kaldır
    if key.startswith('\\"') and key.endswith('\\"'):
        key = key[2:-2]
    # Tüm escape karakterlerini temizle
    key = re.sub(r'\\"', '', key)  # \" karakterlerini kaldır
    key = key.strip('"')  # Baş ve sondaki " karakterlerini kaldır
    key = key.strip()  # Whitespace'leri temizle
    
    # Key'i eklenenler dict'indeki key'lerle karşılaştır
    if key not in eklenenler:
        return jsonify({'ok': False, 'message': f'Kayıt bulunamadı. Key: {repr(key)}, Mevcut keys: {[repr(k) for k in eklenenler.keys()]}'}), 404
    try:
        kategori, barkod = key.split(':', 1)
    except ValueError:
        return jsonify({'ok': False, 'message': 'Key format hatalı'}), 400
    if kategori == 'barkodsuz':
        if barkod in barkodsuz_dict:
            # Adet kontrolü: Eğer adet 1 ise azaltma yapma
            current_adet = barkodsuz_dict[barkod]['ADET']
            if current_adet <= 1:
                stats = get_stats()
                return jsonify({'ok': False, 'message': 'Ürün adeti 1, daha fazla azaltılamaz', 'eklenenler': list(eklenenler.values()), 'stats': stats}), 400
            
            barkodsuz_dict[barkod]['ADET'] -= 1
            eklenenler[key]['adet'] = barkodsuz_dict[barkod]['ADET']
    elif kategori == 'hasarli':
        if barkod in hasarli_dict:
            # Adet kontrolü: Eğer adet 1 ise azaltma yapma
            current_adet = hasarli_dict[barkod]['ADET']
            if current_adet <= 1:
                stats = get_stats()
                return jsonify({'ok': False, 'message': 'Ürün adeti 1, daha fazla azaltılamaz', 'eklenenler': list(eklenenler.values()), 'stats': stats}), 400
            
            hasarli_dict[barkod]['ADET'] -= 1
            eklenenler[key]['adet'] = hasarli_dict[barkod]['ADET']
    elif kategori == 'kayitsiz':
        if barkod in kayıtsız_list:
            try:
                kayıtsız_list.remove(barkod)
            except ValueError:
                pass
        if key in eklenenler:
            del eklenenler[key]
    stats = get_stats()
    return jsonify({'ok': True, 'eklenenler': list(eklenenler.values()), 'stats': stats})


@app.route('/api/eklenenler/increment', methods=['POST'])
@login_required
def api_eklenenler_increment():
    data = request.get_json(silent=True) or {}
    key = data.get('key', '').strip() if isinstance(data.get('key'), str) else str(data.get('key', '')).strip()
    if not key:
        return jsonify({'ok': False, 'message': 'Key gerekli'}), 400
    
    # Key'deki escape karakterlerini temizle (HTML attribute'dan gelen escape karakterleri)
    import re
    # \" ile başlayıp \" ile bitiyorsa, bunları kaldır
    if key.startswith('\\"') and key.endswith('\\"'):
        key = key[2:-2]
    # Tüm escape karakterlerini temizle
    key = re.sub(r'\\"', '', key)  # \" karakterlerini kaldır
    key = key.strip('"')  # Baş ve sondaki " karakterlerini kaldır
    key = key.strip()  # Whitespace'leri temizle
    
    # Key'i eklenenler dict'indeki key'lerle karşılaştır
    if key not in eklenenler:
        return jsonify({'ok': False, 'message': f'Kayıt bulunamadı. Key: {repr(key)}, Mevcut keys: {[repr(k) for k in eklenenler.keys()]}'}), 404
    try:
        kategori, barkod = key.split(':', 1)
    except ValueError:
        return jsonify({'ok': False, 'message': 'Key format hatalı'}), 400
    if kategori == 'barkodsuz':
        product = {
            'title': eklenenler[key].get('title'),
            'brand': format_brand_name(eklenenler[key].get('brand', '')),
            'image_link': eklenenler[key].get('image_link'),
        }
        adet = add_barkodsuz(barkod, product)
        eklenenler[key]['adet'] = adet
    elif kategori == 'hasarli':
        product = {
            'title': eklenenler[key].get('title'),
            'brand': format_brand_name(eklenenler[key].get('brand', '')),
            'image_link': eklenenler[key].get('image_link'),
        }
        adet = add_hasarli(barkod, product)
        eklenenler[key]['adet'] = adet
    else:
        # kayıtsız için arttırma yapmayız
        return jsonify({'ok': False, 'message': 'Kayıtsız için arttırma desteklenmiyor'}), 400
    stats = get_stats()
    return jsonify({'ok': True, 'eklenenler': list(eklenenler.values()), 'stats': stats})


@app.route('/api/search', methods=['POST'])
@login_required
def api_search():
    """Ürün arama endpoint'i - metin bazlı arama"""
    data = request.get_json(silent=True) or {}
    search_term = (data.get('q') or data.get('query') or '').strip()
    
    if not search_term:
        return jsonify({'ok': False, 'message': 'Arama terimi boş olamaz'}), 400
    
    try:
        # ebebek API'sini kullanarak arama yap
        url = "https://ebebek.wawlabs.com/autocomplete"
        response = requests.get(f"{url}?q={search_term}", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            products = data.get("products") or []
            # Ürünleri formatla
            formatted_products = []
            for product in products:
                formatted_products.append({
                    'title': product.get('title', ''),
                    'brand': format_brand_name(product.get('brand', '')),
                    'image_link': product.get('image_link', ''),
                    'stock_status': product.get('stock_status', ''),
                    'price': product.get('price', ''),
                    'barkod': product.get('barkod', ''),
                })
            
            return jsonify({
                'ok': True,
                'products': formatted_products,
                'count': len(formatted_products)
            })
        else:
            return jsonify({'ok': False, 'message': f'API hatası: {response.status_code}'}), 500
            
    except Exception as e:
        return jsonify({'ok': False, 'message': f'Arama hatası: {str(e)}'}), 500


@app.route('/api/shutdown', methods=['POST'])
def shutdown():
    """Uygulamayı kapat - Temiz bir şekilde (hepsiburada tarzı)"""
    
    def cleanup():
        """Temizlik işlemleri"""
        try:
            # Verileri temizle
            barkodsuz_dict.clear()
            hasarli_dict.clear()
            kayıtsız_list.clear()
            eklenenler.clear()
            
            # Session'ı tamamen temizle
            session.clear()
            session.permanent = False
        except:
            pass
        
        # System exit
        import os
        os._exit(0)
    
    # 0.5 saniye bekle ve temizle
    import threading
    threading.Timer(0.5, cleanup).start()
    return jsonify({'success': True})




if __name__ == '__main__':
    import webbrowser
    import threading, time
    import sys
    import ctypes
    
    # Konsolu gizle (Windows'ta)
    if sys.platform == 'win32':
        try:
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        except:
            pass
    
    # Tarayıcıyı ayrı bir thread'de aç
    def open_browser():
        time.sleep(1.5)  # Sunucunun başlaması için bekle
        webbrowser.open('http://127.0.0.1:5002/')
    
    threading.Thread(target=open_browser).start()
    app.run(debug=False, port=5002, use_reloader=False)


