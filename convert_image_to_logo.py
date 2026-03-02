"""
Resim dosyasını ÖZKAYA logosu olarak dönüştür
"""

from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageOps
import os
import sys

def convert_image_to_logo(image_path, output_logo="logo.png", output_ico="ICON.ico"):
    """Resim dosyasını logo ve ICO formatına dönüştür - İyileştirilmiş versiyon"""
    
    if not os.path.exists(image_path):
        print(f"❌ HATA: {image_path} bulunamadı!")
        return False
    
    print(f"✓ Resim yükleniyor: {image_path}")
    
    # Resmi aç
    img = Image.open(image_path)
    
    # RGBA'ya dönüştür (şeffaflık için)
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Görseli kırpmadan sığdır (bir tık küçük): 512 içinde 420x420 güvenli alan
    img = ImageOps.contain(img, (420, 420), Image.Resampling.LANCZOS)
    
    # Kontrastı artır (daha net görünmesi için)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.3)
    
    # Parlaklığı artır
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(1.2)
    
    # Netliği artır
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(1.5)
    
    # Şeffaf arka plan oluştur
    bg_size = 512
    background = Image.new('RGBA', (bg_size, bg_size), (255, 255, 255, 0))
    
    # Beyaz glow efekti için çoklu katman
    glow = Image.new('RGBA', (bg_size, bg_size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(glow)
    
    # Hafif beyaz glow
    offset_x = (bg_size - img.width) // 2
    offset_y = (bg_size - img.height) // 2
    for i in range(10, 0, -1):
        alpha = int(30 * (i / 10))
        expand = i * 2
        glow_layer = Image.new('RGBA', (bg_size, bg_size), (255, 255, 255, 0))
        glow_draw = ImageDraw.Draw(glow_layer)
        glow_draw.ellipse([offset_x - expand, offset_y - expand, 
                          offset_x + img.width + expand, offset_y + img.height + expand], 
                         fill=(255, 255, 255, alpha))
        background = Image.alpha_composite(background, glow_layer)
    
    # Logoyu ortala ve yapıştır
    background.paste(img, (offset_x, offset_y), img)
    img_final = background
    
    # PNG olarak kaydet
    img_final.save(output_logo, 'PNG')
    print(f"✓ {output_logo} oluşturuldu (512x512) - Geliştirilmiş versiyon")
    
    # ICO dosyası oluştur (çoklu boyutlar)
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    images = []
    
    for size in sizes:
        images.append(img_final.resize(size, Image.Resampling.LANCZOS))
    
    # ICO olarak kaydet
    images[0].save(
        output_ico,
        format='ICO',
        sizes=[(img.size) for img in images]
    )
    
    print(f"✓ {output_ico} oluşturuldu (Daha net ve okunabilir)")
    sizes_str = ', '.join([f'{s[0]}x{s[1]}' for s in sizes])
    print(f"  Boyutlar: {sizes_str}")
    
    return True

def main():
    print("="*60)
    print("RESIM LOGO DÖNÜŞTÜRÜCÜ")
    print("="*60)
    print("")
    
    # Komut satırından dosya alındı mı?
    if len(sys.argv) > 1:
        image_file = sys.argv[1]
    else:
        # Mevcut klasörde resim dosyalarını ara
        jpg_files = [f for f in os.listdir('.') if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif'))]
        
        if jpg_files:
            print("Klasörde bulunan resim dosyaları:")
            for i, f in enumerate(jpg_files, 1):
                print(f"  {i}. {f}")
            
            if len(jpg_files) == 1:
                image_file = jpg_files[0]
                print(f"\n✓ Otomatik seçildi: {image_file}")
            else:
                choice = input("\nKullanılacak resmin numarasını girin (1-{}): ".format(len(jpg_files)))
                try:
                    image_file = jpg_files[int(choice) - 1]
                except:
                    print("❌ Geçersiz seçim!")
                    return
        else:
            print("❌ Klasörde resim dosyası bulunamadı!")
            print("\nLütfen resim dosyasını klasöre kopyalayın:")
            print("  • ÖZKAYA.png, logo.jpg vb.")
            return
    
    print("")
    
    # Resmi logo olarak dönüştür
    if convert_image_to_logo(image_file):
        print("")
        print("="*60)
        print("✓ LOGO BAŞARILI DÖNÜŞTÜRÜLDÜ!")
        print("="*60)
        print("")
        print("Şimdi build_exe.bat çalıştırarak yeni EXE oluşturun")
        print("")
    else:
        print("\n❌ Logo dönüştürme başarısız!")

if __name__ == "__main__":
    main()
