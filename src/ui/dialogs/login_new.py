from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                           QPushButton, QMessageBox, QCheckBox, QFrame)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QPixmap
from PyQt5.QtWidgets import QSize
from src.services.auth_service import AuthService
import config

class LoginDialog(QDialog):
    """Giriş pence
resi - Modern tasarım"""
    
    def __init__(self):
        super().__init__()
        self.user = None
        self.init_ui()
    
    def init_ui(self):
        """Arayüz öğelerini başlat"""
        self.setWindowTitle(config.APP_NAME)
        self.setGeometry(400, 250, 500, 350)
        self.setModal(True)
        self.setStyleSheet("""
            QDialog { background-color: #f5f5f5; }
            QLineEdit { 
                padding: 8px; 
                border: 2px solid #ddd;
                border-radius: 4px;
                font-size: 11pt;
            }
            QPushButton {
                padding: 10px;
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover { background-color: #1976D2; }
            QLabel { font-size: 11pt; }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Başlık
        title = QLabel("Muhasebe Sistemi")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Giriş Yapın")
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #666;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(20)
        
        # Username
        layout.addWidget(QLabel("📧 Kullanıcı Adı: <span style=\"color:#d32f2f\">*</span>"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Kullanıcı adınızı girin")
        layout.addWidget(self.username_input)
        
        # Password
        layout.addWidget(QLabel("🔒 Şifre: <span style=\"color:#d32f2f\">*</span>"))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Şifrenizi girin")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)
        
        # Butonlar
        btn_layout = QHBoxLayout()
        
        btn_giris = QPushButton("Giriş Yap")
        btn_giris.setMinimumHeight(40)
        btn_giris.clicked.connect(self.login)
        btn_layout.addWidget(btn_giris)
        
        btn_kayit = QPushButton("Yeni Kayıt")
        btn_kayit.setMinimumHeight(40)
        btn_kayit.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                padding: 10px;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        btn_kayit.clicked.connect(self.show_register)
        btn_layout.addWidget(btn_kayit)
        
        layout.addSpacing(10)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        self.username_input.setFocus()
    
    def login(self):
        """Giriş işlemi"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Hata", "Kullanıcı adı ve şifre gerekli!")
            return
        
        user = AuthService.authenticate(username, password)
        if user:
            self.user = user
            self.accept()
        else:
            QMessageBox.critical(self, "Hata", "Kullanıcı adı veya şifre yanlış!")
            self.password_input.clear()
    
    def show_register(self):
        """Kayıt penceresini aç"""
        from .register_dialog import RegisterDialog
        dialog = RegisterDialog()
        if dialog.exec_():
            QMessageBox.information(self, "Başarılı", "Kayıt başarıyla tamamlandı!\nLütfen giriş yapın.")
            self.username_input.setText(dialog.username)
            self.password_input.setFocus()
