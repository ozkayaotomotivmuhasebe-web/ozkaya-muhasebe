#!/usr/bin/env python3
"""Test uygulaması"""

import sys
print("1. Python başladı")

try:
    from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
    from PyQt5.QtCore import Qt
    print("2. PyQt5 importu başarılı")
except Exception as e:
    print(f"HATA PyQt5: {e}")
    sys.exit(1)

try:
    from src.database.db import init_db
    print("3. Database modülü import başarılı")
except Exception as e:
    print(f"HATA Database: {e}")
    sys.exit(1)

try:
    init_db()
    print("4. Database başlatıldı")
except Exception as e:
    print(f"HATA DB init: {e}")
    sys.exit(1)

try:
    class SimpleWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Muhasebe Sistemi - Test")
            self.setGeometry(100, 100, 400, 300)
            label = QLabel("Sistem başarıyla başladı! ✓")
            self.setCentralWidget(label)
    
    print("5. PyQt5 penceresi oluşturuluyor...")
    app = QApplication(sys.argv)
    window = SimpleWindow()
    window.show()
    
    print("6. Pencerepencere gösteriliyor...")
    sys.exit(app.exec_())
    
except Exception as e:
    print(f"HATA GUI: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
