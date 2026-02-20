"""
Resim dosyasını ÖZKAYA logosu olarak dönüştür
"""

from PIL import Image
import os
import sys

def convert_image_to_logo(image_path, output_logo="logo.png", output_ico="ICON.ico"):
    """Resim dosyasını logo ve ICO formatına dönüştür"""
    
    if not os.path.exists(image_path):
        print(f"❌ HATA: {image_path} bulunamadı!")
        return False
    
    print(f"✓ Resim yükleniyor: {image_path}")
    
    # Resmi aç
    img = Image.open(image_path)
    
    # RGBA'ya dönüştür (şeffaflık için)
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # 512x512 boyutuna yeniden boyutlandır (en iyi kalite için)
    img_large = img.resize((512, 512), Image.Resampling.LANCZOS)
    
    # PNG olarak kaydet
    img_large.save(output_logo, 'PNG')
    print(f"✓ {output_logo} oluşturuldu (512x512)")
    
    # ICO dosyası oluştur (çoklu boyutlar)
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    images = []
    
    for size in sizes:
        images.append(img.resize(size, Image.Resampling.LANCZOS))
    
    # ICO olarak kaydet
    images[0].save(
        output_ico,
        format='ICO',
        sizes=[(img.size) for img in images]
    )
    
    print(f"✓ {output_ico} oluşturuldu")
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
