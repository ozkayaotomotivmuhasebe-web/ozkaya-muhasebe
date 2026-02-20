from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                           QPushButton, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication
from src.services.auth_service import AuthService
import config

class LoginDialog(QDialog):
    """Giriş penceresi - Premium tasarım"""
    
    def __init__(self):
        super().__init__()
        self.user = None
        self.init_ui()
    
    def init_ui(self):
        """Arayüz öğelerini başlat"""
        self.setWindowTitle(config.APP_NAME)
        self.setGeometry(0, 0, 390, 650)
        self.center_window()
        self.setModal(True)
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # Ana stil
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(24, 40, 24, 40)
        main_layout.setSpacing(0)
        
        # ÖZKAYA Başlığı
        logo_title = QLabel("ÖZKAYA")
        logo_title.setFont(QFont("Segoe UI", 56, QFont.Bold))
        logo_title.setStyleSheet("color: #667eea;")
        logo_title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(logo_title)
        
        subtitle = QLabel("Muhasebe Sistemi")
        subtitle.setFont(QFont("Segoe UI", 16, QFont.Light))
        subtitle.setStyleSheet("color: #888888;")
        subtitle.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(subtitle)
        
        main_layout.addSpacing(25)
        
        # Hoş Geldiniz
        title = QLabel("Hoş Geldiniz")
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setStyleSheet("color: #333333; margin-bottom: 5px;")
        main_layout.addWidget(title)
        
        subtitle2 = QLabel("Hesabınıza giriş yaparak başlayın")
        subtitle2.setFont(QFont("Segoe UI", 12))
        subtitle2.setStyleSheet("color: #888888; margin-bottom: 30px;")
        main_layout.addWidget(subtitle2)
        
        # Kullanıcı Adı
        main_layout.addWidget(QLabel(" Kullanıcı Adı <span style=\"color:#d32f2f\">*</span>"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Kullanıcı adınızı girin")
        self.username_input.setMinimumHeight(45)
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 15px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 12pt;
                background-color: white;
                selection-background-color: #667eea;
            }
            QLineEdit:focus {
                border: 2px solid #667eea;
                background-color: #f0f4ff;
            }
        """)
        main_layout.addWidget(self.username_input)
        main_layout.addSpacing(15)
        
        # Şifre
        main_layout.addWidget(QLabel(" Şifre <span style=\"color:#d32f2f\">*</span>"))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Şifrenizi girin")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(45)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 15px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 12pt;
                background-color: white;
                selection-background-color: #667eea;
            }
            QLineEdit:focus {
                border: 2px solid #667eea;
                background-color: #f0f4ff;
            }
        """)
        main_layout.addWidget(self.password_input)
        main_layout.addSpacing(30)
        
        # Giriş Butonu
        btn_giris = QPushButton("Giriş Yap")
        btn_giris.setMinimumHeight(50)
        btn_giris.setFont(QFont("Segoe UI", 12, QFont.Bold))
        btn_giris.setCursor(Qt.PointingHandCursor)
        btn_giris.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5568d3, stop:1 #6a3f91);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4a5ac8, stop:1 #5d3880);
            }
        """)
        btn_giris.clicked.connect(self.login)
        main_layout.addWidget(btn_giris)
        
        main_layout.addStretch()
        
        # Alt bilgi - ÖZKAYA
        info_label = QLabel("© 2026 ÖZKAYA Muhasebe Sistemi")
        info_label.setFont(QFont("Segoe UI", 9))
        info_label.setStyleSheet("color: #aaaaaa;")
        info_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(info_label)
        
        self.setLayout(main_layout)
    
    def center_window(self):
        """Pencereyi ortala"""
        screen = QApplication.primaryScreen()
        screen_rect = screen.availableGeometry()
        x = (screen_rect.width() - 390) // 2
        y = (screen_rect.height() - 650) // 2
        self.move(x, y)
    
    def login(self):
        """Giriş işlemi"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Uyarı", "Kullanıcı adı ve şifre gerekli!")
            return
        
        user = AuthService.authenticate(username, password)
        if user:
            self.user = user
            self.accept()
        else:
            QMessageBox.critical(self, "Hata", " Kullanıcı adı veya şifre yanlış!")
            self.password_input.clear()
            self.username_input.setFocus()
    
    def keyPressEvent(self, event):
        """Enter tuşu ile giriş"""
        if event.key() == Qt.Key_Return:
            self.login()
        super().keyPressEvent(event)
