from PIL import Image, ImageDraw, ImageFont

# Yüksek çözünürlük icon (512x512)
img = Image.new('RGB', (512, 512), color=(0, 51, 102))  # Mavi arka plan
draw = ImageDraw.Draw(img)

# Font yükle
try:
    font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 140)
except:
    font = ImageFont.load_default()

# Yazı ekle
text = "ÖZKAYA"
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
x = (512 - text_width) // 2
y = (512 - text_height) // 2

# Beyaz yazı
draw.text((x, y), text, fill=(255, 255, 255), font=font)

# ICO formatına kaydet
img.save('ICON.ico')
print("✓ ICON.ico oluşturuldu")
