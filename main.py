import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from src.database.db import init_db, close_db
from src.ui.dialogs.login_dialog import LoginDialog
from src.ui.main_window import MainWindow
from src.services.auth_service import AuthService
from src.services.admin_service import AdminService
from src.utils.app_icon import get_app_icon
from src.utils.updater import check_and_update
import config


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
        QHeaderView::section { padding: 6px; font-size: 9pt; }
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

            # Güncelleme kontrolü (arka planda, 2 sn sonra)
            check_and_update(main_window)

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
