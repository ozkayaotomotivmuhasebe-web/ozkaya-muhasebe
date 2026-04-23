import sys
import os

# Windows'ta UTF-8 encoding'i aktif et
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from PyQt5.QtWidgets import QApplication, QMessageBox, QStyleFactory
from PyQt5.QtCore import Qt, QTimer
from src.database.db import init_db, close_db
from src.ui.dialogs.login_dialog import LoginDialog
from src.ui.main_window import MainWindow
from src.services.auth_service import AuthService
from src.services.admin_service import AdminService
from src.utils.app_icon import get_app_icon
from src.utils.updater import check_and_update
import config

# High-DPI desteği — QApplication oluşturulmadan önce ayarlanmalı
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


def create_admin_account():
    """Admin hesabı oluştur"""
    try:
        user = AuthService.authenticate("admin", "admin123")
        if not user:
            # AdminService ile admin rolü ile oluştur
            user, msg = AdminService.create_user(
                "admin", 
                "admin@ozkaya.com", 
                "admin123", 
                "Yönetici",
                role='admin'
            )
            if user:
                print("✓ Admin hesabı oluşturuldu: admin / admin123")
            else:
                print(f"Admin hesabı oluşturma hatası: {msg}")
    except Exception as e:
        print(f"Admin hesabı oluşturma hatası: {e}")


def main():
    """Uygulamayı başlat"""
    
    # Veritabanını başlat
    try:
        init_db()
        create_admin_account()
    except Exception as e:
        print(f"Veritabanı başlatma hatası: {e}")
        sys.exit(1)
    
    # PyQt5 uygulamasını oluştur
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))  # EXE'de tutarlı buton render
    app_icon = get_app_icon()
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)
    app.setStyleSheet("""
        QWidget { font-size: 10pt; }
        QLabel { font-size: 10pt; }
        QLineEdit, QComboBox, QDateEdit, QTextEdit, QSpinBox, QDoubleSpinBox {
            min-height: 30px;
            padding: 6px 8px;
            font-size: 10pt;
        }
        QPushButton {
            min-height: 30px;
            padding: 6px 10px;
            font-size: 10pt;
        }
        QHeaderView::section { padding: 6px; font-size: 10pt; font-weight: bold; }
        QTableWidget { font-size: 10pt; }
    """)
    
    try:
        # Giriş dialog'unu göster
        login_dialog = LoginDialog()
        
        if login_dialog.exec_():
            # Ana pencereyi aç
            user = login_dialog.user
            main_window = MainWindow(user)
            main_window.show()

            # Güncelleme kontrolü (event loop başladıktan 3 sn sonra)
            QTimer.singleShot(3000, lambda: check_and_update(main_window))

            sys.exit(app.exec_())
        else:
            print("Giriş iptal edildi")
            sys.exit(0)
    
    except Exception as e:
        QMessageBox.critical(None, "Hata", f"Uygulama başlatılamadı:\n{e}")
        print(f"Hata: {e}")
        sys.exit(1)
    
    finally:
        close_db()


if __name__ == "__main__":
    main()
