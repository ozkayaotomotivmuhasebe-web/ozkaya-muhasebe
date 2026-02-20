"""
ÖZKAYA Muhasebe Sistemi - Premium Logo Oluşturucu
Modern ve profesyonel tasarım
"""

from PIL import Image, ImageDraw, ImageFont
import math

def create_logo():
    """ÖZKAYA logosu oluştur - Sadece yazı"""
    
    # Yüksek kalite logo
    size = 512
    img = Image.new('RGB', (size, size), (255, 255, 255))
    draw = ImageDraw.Draw(img, 'RGBA')
    
    # Gradient arka plan - Mavi tonları
    for y in range(size):
        # Mavi gradientı
        r = int(25 + (60 - 25) * (y / size))
        g = int(80 + (160 - 80) * (y / size))
        b = int(160 + (220 - 160) * (y / size))
        draw.rectangle([(0, y), (size, y+1)], fill=(r, g, b))
    
    # ÖZKAYA yazısı - Uygun boyut
    try:
        font_large = ImageFont.truetype("C:\\Windows\\Fonts\\arialbd.ttf", 120)
    except:
        try:
            font_large = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 120)
        except:
            font_large = ImageFont.load_default()
    
    # ÖZKAYA yazısı
    text = "ÖZKAYA"
    
    # Yazı konumunu ortala
    bbox = draw.textbbox((0, 0), text, font=font_large)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    text_x = (size - text_width) // 2
    text_y = (size - text_height) // 2 - 20
    
    # Yazı gölgesi (shadow)
    shadow_offset = 3
    draw.text(
        (text_x + shadow_offset, text_y + shadow_offset),
        text,
        font=font_large,
        fill=(0, 0, 0, 150)
    )
    
    # Ana yazı - Beyaz
    draw.text(
        (text_x, text_y),
        text,
        font=font_large,
        fill=(255, 255, 255)
    )
    
    # PNG olarak kaydet
    png_path = "logo.png"
    img.save(png_path, 'PNG')
    print(f"✓ {png_path} oluşturuldu (512x512)")
    
    # ICO dosyası oluştur
    create_ico_from_image(img, "ICON.ico")
    
    return png_path

def convert_to_ico(png_path, ico_path="ICON.ico"):
    """Resimden ICO dosyası oluştur"""
    
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    
    img = Image.open(png_path)
    
    images = []
    for size in sizes:
        images.append(img.resize(size, Image.Resampling.LANCZOS))
    
    images[0].save(
        ico_path,
        format='ICO',
        sizes=[(img.size) for img in images]
    )
    
    print(f"✓ {ico_path} oluşturuldu")
    print(f"  Boyutlar: {', '.join([f'{s[0]}x{s[1]}' for s in sizes])}")

def create_ico_from_image(img, ico_path="ICON.ico"):
    """Resimden ICO dosyası oluştur"""
    
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    
    images = []
    for size in sizes:
        images.append(img.resize(size, Image.Resampling.LANCZOS))
    
    images[0].save(
        ico_path,
        format='ICO',
        sizes=[(img.size) for img in images]
    )
    
    print(f"✓ {ico_path} oluşturuldu")
    sizes_str = ', '.join([f'{s[0]}x{s[1]}' for s in sizes])
    print(f"  Boyutlar: {sizes_str}")

def create_app_icon():
    """Icon oluştur"""
    
    print("="*60)
    print("ÖZKAYA PREMIUM LOGO OLUŞTURUCU")
    print("="*60)
    print("")
    
    print("Premium ÖZKAYA logosu oluşturuluyor...")
    print("(Boyutlar: 512x512, ICO ve PNG formatları)")
    print("")
    
    create_logo()
    
    print("")
    print("="*60)
    print("✓ LOGO BAŞARILI OLUŞTURULDU!")
    print("="*60)
    print("")
    print("Oluşturulan dosyalar:")
    print("  • logo.png - Logonuzu görmek için açabilirsiniz")
    print("  • ICON.ico - Uygulamaya ait simge")
    print("")
    print("Şimdi build_exe.bat çalıştırarak yeni EXE oluşturun")
    print("")

if __name__ == "__main__":
    ico_path = create_app_icon()
