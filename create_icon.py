"""
Icon oluşturucu - Ebebek Barkod Takip Sistemi için icon oluşturur
Login sayfasındaki 3D kutu tasarımını kullanır
"""
from PIL import Image, ImageDraw
import os
import math

def draw_gradient_background(draw, width, height, start_color, end_color, angle=135):
    """Gradient arka plan çizer"""
    # 135 derece açı ile gradient (sol üstten sağ alta)
    angle_rad = math.radians(angle)
    
    for y in range(height):
        for x in range(width):
            # Diyagonal mesafe hesapla
            distance = (x * math.cos(angle_rad) + y * math.sin(angle_rad))
            max_distance = width * math.cos(angle_rad) + height * math.sin(angle_rad)
            
            if max_distance > 0:
                ratio = distance / max_distance
                ratio = max(0, min(1, ratio))  # 0-1 arası sınırla
            else:
                ratio = 0
            
            # Renk interpolasyonu
            r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
            
            draw.point((x, y), fill=(r, g, b))

def draw_3d_box(draw, center_x, center_y, size, angle=15):
    """3D kutu çizer"""
    # Kutu boyutları
    box_width = size
    box_height = size
    box_depth = size * 0.4
    
    # Perspektif açısı
    angle_rad = math.radians(angle)
    depth_offset_x = box_depth * math.cos(angle_rad)
    depth_offset_y = box_depth * math.sin(angle_rad)
    
    # Köşe noktaları (ön yüz)
    front_left = (center_x - box_width // 2, center_y - box_height // 2)
    front_right = (center_x + box_width // 2, center_y - box_height // 2)
    front_bottom_left = (center_x - box_width // 2, center_y + box_height // 2)
    front_bottom_right = (center_x + box_width // 2, center_y + box_height // 2)
    
    # Köşe noktaları (arka yüz)
    back_left = (front_left[0] + depth_offset_x, front_left[1] - depth_offset_y)
    back_right = (front_right[0] + depth_offset_x, front_right[1] - depth_offset_y)
    back_bottom_left = (front_bottom_left[0] + depth_offset_x, front_bottom_left[1] - depth_offset_y)
    back_bottom_right = (front_bottom_right[0] + depth_offset_x, front_bottom_right[1] - depth_offset_y)
    
    # Kutu rengi (açık kahverengi)
    box_color = (210, 180, 140)  # Açık kahverengi
    darker_color = (180, 150, 110)  # Daha koyu ton
    darkest_color = (150, 120, 90)  # En koyu ton
    
    # Arka yüz (en koyu)
    draw.polygon([
        back_left, back_right, back_bottom_right, back_bottom_left
    ], fill=darkest_color)
    
    # Üst yüz (orta ton)
    draw.polygon([
        front_left, front_right, back_right, back_left
    ], fill=darker_color)
    
    # Sağ yüz (orta ton)
    draw.polygon([
        front_right, front_bottom_right, back_bottom_right, back_right
    ], fill=darker_color)
    
    # Ön yüz (en açık)
    draw.rectangle([
        front_left, front_bottom_right
    ], fill=box_color)
    
    # Barkod etiketi (beyaz dikdörtgen)
    label_width = box_width * 0.6
    label_height = box_height * 0.25
    label_x = center_x - label_width // 2
    label_y = center_y - box_height // 2 + box_height * 0.15
    
    # Etiket arka planı
    draw.rectangle([
        (label_x, label_y),
        (label_x + label_width, label_y + label_height)
    ], fill=(255, 255, 255))
    
    # Barkod çizgileri
    bar_count = 8
    bar_width = label_width / (bar_count * 2)
    bar_spacing = bar_width
    
    for i in range(bar_count):
        bar_x = label_x + (i * bar_width * 2) + bar_spacing
        bar_height_vary = label_height * (0.6 + (i % 3) * 0.15)
        bar_y_offset = (label_height - bar_height_vary) / 2
        
        draw.rectangle([
            (bar_x, label_y + bar_y_offset),
            (bar_x + bar_width, label_y + bar_y_offset + bar_height_vary)
        ], fill=(0, 0, 0))

def create_icon():
    """Ebebek icon'unu oluşturur - Login sayfasındaki 3D kutu tasarımını kullanır"""
    # Icon boyutları
    size = 256
    # Koyu lacivert arka plan
    bg_color = (15, 23, 42)  # #0f172a
    img = Image.new('RGB', (size, size), color=bg_color)
    
    # Köşeleri yuvarlatılmış kare container
    margin = 10
    corner_radius = 25
    
    # Gradient arka plan için
    gradient_img = Image.new('RGB', (size, size), color=bg_color)
    gradient_draw = ImageDraw.Draw(gradient_img)
    
    # Gradient arka plan (mavi -> turuncu)
    # Login sayfasındaki renkler: #0072ce (mavi) -> #ff8200 (turuncu)
    start_color = (0, 114, 206)      # Mavi #0072ce
    end_color = (255, 130, 0)        # Turuncu #ff8200
    
    # Diagonal gradient (135 derece - sol üstten sağ alta)
    for y in range(size):
        for x in range(size):
            # Diagonal mesafe hesapla
            diagonal_ratio = (x + y) / (size * 2)
            r = int(start_color[0] + (end_color[0] - start_color[0]) * diagonal_ratio)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * diagonal_ratio)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * diagonal_ratio)
            gradient_draw.point((x, y), fill=(r, g, b))
    
    # Yuvarlatılmış köşeler için mask oluştur
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle(
        [(margin, margin), (size - margin, size - margin)],
        radius=corner_radius,
        fill=255
    )
    
    # Koyu lacivert arka plana gradient'i yuvarlatılmış şekilde uygula
    final_img = Image.new('RGB', (size, size), color=bg_color)
    final_img.paste(gradient_img, (0, 0), mask)
    
    draw = ImageDraw.Draw(final_img)
    
    # 3D kutu çiz (ortada, daha büyük)
    box_size = size * 0.45
    center_x = size // 2 - 16  # Biraz daha sola kaydır
    center_y = size // 2  # Tam ortada
    
    draw_3d_box(draw, center_x, center_y, box_size, angle=20)
    
    # Icon'u kaydet
    icon_path = "icon.ico"
    # ICO formatı için çoklu boyut oluştur
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    
    # ICO dosyası olarak kaydet
    final_img.save(icon_path, format='ICO', sizes=[(s, s) for s, _ in sizes])
    print(f"✓ Icon başarıyla oluşturuldu: {icon_path}")
    
    # PNG olarak da kaydet (görselleştirme için)
    final_img.save("icon.png", format='PNG')
    print(f"✓ PNG önizleme oluşturuldu: icon.png")

if __name__ == "__main__":
    try:
        create_icon()
    except ImportError:
        print("Pillow (PIL) paketi bulunamadı. Yüklemek için: pip install Pillow")
    except Exception as e:
        print(f"Hata: {e}")
        import traceback
        traceback.print_exc()


