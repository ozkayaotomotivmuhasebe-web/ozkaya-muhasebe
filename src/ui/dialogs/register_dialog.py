from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                           QPushButton, QMessageBox, QFrame, QScrollArea)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QApplication
from src.services.auth_service import AuthService
from src.utils.app_icon import get_app_icon
import config

class RegisterDialog(QDialog):
    """Kayıt penceresi - Premium tasarım"""
    
    def __init__(self):
        super().__init__()
        self.username = ""
        app_icon = get_app_icon()
        if not app_icon.isNull():
            self.setWindowIcon(app_icon)
        self.init_ui()
    
    def init_ui(self):
        """Arayüz öğelerini başlat"""
        self.setWindowTitle("Yeni Kayıt - " + config.APP_NAME)
        self.setGeometry(0, 0, 900, 650)
        self.center_window()
        self.setModal(True)
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
        """)
        
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sol taraf - Dekoratif
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Sağ taraf - Form
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 1)
        
        self.setLayout(main_layout)
    
    def center_window(self):
        """Pencereyi ortala"""
        screen = QApplication.primaryScreen()
        screen_rect = screen.availableGeometry()
        x = (screen_rect.width() - 900) // 2
        y = (screen_rect.height() - 650) // 2
        self.move(x, y)
    
    def create_left_panel(self) -> QFrame:
        """Sol panel - Premium stil"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border: none;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 80, 50, 80)
        layout.setSpacing(20)
        
        # ÖZKAYA Logo
        logo_title = QLabel("ÖZKAYA")
        logo_title.setFont(QFont("Segoe UI", 44, QFont.Bold))
        logo_title.setStyleSheet("color: white;")
        logo_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_title)
        
        subtitle = QLabel("Muhasebe Sistemi")
        subtitle.setFont(QFont("Segoe UI", 16, QFont.Light))
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.9);")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(30)
        
        # Özellikler
        features = [
            ("🚀", "Hızlı", "Sistem en hızlı muhasebe\nçözümüdür"),
            ("🔒", "Güvenli", "Tüm verileriniz\nşifrelidir"),
            ("📊", "Profesyonel", "Detaylı raporlar\nve analizler")
        ]
        
        for icon, title, desc in features:
            frame = QFrame()
            frame.setStyleSheet("""
                QFrame {
                    background-color: rgba(255, 255, 255, 0.1);
                    border-radius: 10px;
                    border: 2px solid rgba(255, 255, 255, 0.2);
                }
            """)
            frame.setMinimumHeight(70)
            
            frame_layout = QVBoxLayout()
            frame_layout.setContentsMargins(15, 10, 15, 10)
            frame_layout.setSpacing(5)
            
            header_layout = QHBoxLayout()
            icon_label = QLabel(icon)
            icon_label.setFont(QFont("Arial", 20))
            header_layout.addWidget(icon_label)
            
            title_label = QLabel(title)
            title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
            title_label.setStyleSheet("color: white;")
            header_layout.addWidget(title_label)
            header_layout.addStretch()
            
            frame_layout.addLayout(header_layout)
            
            desc_label = QLabel(desc)
            desc_label.setFont(QFont("Segoe UI", 10))
            desc_label.setStyleSheet("color: rgba(255, 255, 255, 0.8);")
            frame_layout.addWidget(desc_label)
            
            frame.setLayout(frame_layout)
            layout.addWidget(frame)
        
        layout.addStretch()
        panel.setLayout(layout)
        return panel
    
    def create_right_panel(self) -> QFrame:
        """Sağ panel - Kayıt formu"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: none;
            }
        """)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        content = QFrame()
        content.setStyleSheet("background-color: #f8f9fa;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(0)
        
        # Başlık
        title = QLabel("Hesap Oluştur")
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setStyleSheet("color: #333333; margin-bottom: 5px;")
        layout.addWidget(title)
        
        subtitle = QLabel("Muhasebe yönetimine başlamak için hesap açın")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #888888; margin-bottom: 30px;")
        layout.addWidget(subtitle)
        
        # Form alanları
        fields = [
            ("👤", "Ad Soyad <span style=\"color:#d32f2f\">*</span>", "self.full_name_input", "Adınız ve soyadınız"),
            ("📧", "Email <span style=\"color:#d32f2f\">*</span>", "self.email_input", "Email adresiniz"),
            ("👤", "Kullanıcı Adı <span style=\"color:#d32f2f\">*</span>", "self.username_input", "Kullanıcı adı (en az 3 karakter)"),
            ("🔒", "Şifre <span style=\"color:#d32f2f\">*</span>", "self.password_input", "Güçlü bir şifre (en az 6 karakter)"),
            ("🔒", "Şifre Onayı <span style=\"color:#d32f2f\">*</span>", "self.password_confirm", "Şifrenizi tekrar girin")
        ]
        
        inputs = {}
        for icon, label, var_name, placeholder in fields:
            layout.addWidget(QLabel(f"{icon} {label}"))
            
            input_field = QLineEdit()
            input_field.setPlaceholderText(placeholder)
            input_field.setMinimumHeight(42)
            
            if "şifre" in label.lower():
                input_field.setEchoMode(QLineEdit.Password)
            
            input_field.setStyleSheet("""
                QLineEdit {
                    padding: 10px 12px;
                    border: 2px solid #e0e0e0;
                    border-radius: 6px;
                    font-size: 11pt;
                    background-color: white;
                    selection-background-color: #667eea;
                }
                QLineEdit:focus {
                    border: 2px solid #667eea;
                    background-color: #f0f4ff;
                }
            """)
            
            layout.addWidget(input_field)
            layout.addSpacing(12)
            
            inputs[var_name] = input_field
        
        # Değişkenlere ata
        self.full_name_input = inputs["self.full_name_input"]
        self.email_input = inputs["self.email_input"]
        self.username_input = inputs["self.username_input"]
        self.password_input = inputs["self.password_input"]
        self.password_confirm = inputs["self.password_confirm"]
        
        layout.addSpacing(10)
        
        # Butonlar
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        # Kayıt Butonu
        btn_kayit = QPushButton("📝 Hesap Oluştur")
        btn_kayit.setMinimumHeight(48)
        btn_kayit.setFont(QFont("Segoe UI", 11, QFont.Bold))
        btn_kayit.setCursor(Qt.PointingHandCursor)
        btn_kayit.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                border-radius: 6px;
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
        btn_kayit.clicked.connect(self.register)
        btn_layout.addWidget(btn_kayit)
        
        # İptal Butonu
        btn_iptal = QPushButton("❌ İptal")
        btn_iptal.setMinimumHeight(48)
        btn_iptal.setFont(QFont("Segoe UI", 11, QFont.Bold))
        btn_iptal.setCursor(Qt.PointingHandCursor)
        btn_iptal.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #667eea;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f0f4ff;
                border: 2px solid #667eea;
            }
            QPushButton:pressed {
                background-color: #e8ecff;
            }
        """)
        btn_iptal.clicked.connect(self.reject)
        btn_layout.addWidget(btn_iptal)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        content.setLayout(layout)
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        panel.setLayout(main_layout)
        
        return panel
    
    def register(self):
        """Kayıt işlemi"""
        full_name = self.full_name_input.text().strip()
        email = self.email_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text()
        password_confirm = self.password_confirm.text()
        
        # Validasyon
        if not all([full_name, email, username, password]):
            QMessageBox.warning(self, "Uyarı", "⚠️ Tüm alanları doldurunuz!")
            return
        
        if len(username) < 3:
            QMessageBox.warning(self, "Uyarı", 
                "⚠️ Kullanıcı adı en az 3 karakterden oluşmalıdır!")
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, "Uyarı", 
                "⚠️ Şifre en az 6 karakterden oluşmalıdır!")
            return
        
        if password != password_confirm:
            QMessageBox.warning(self, "Uyarı", 
                "⚠️ Şifreler eşleşmiyor!")
            self.password_confirm.clear()
            self.password_input.clear()
            return
        
        if '@' not in email:
            QMessageBox.warning(self, "Uyarı", 
                "⚠️ Geçerli bir email adresi girin!")
            return
        
        # Kayıt git
        if AuthService.register_user(username, email, password, full_name):
            self.username = username
            self.accept()
        else:
            QMessageBox.critical(self, "Hata", 
                "❌ Kullanıcı adı veya email zaten kayıtlı!")
