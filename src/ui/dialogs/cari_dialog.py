from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QComboBox, QMessageBox, QTextEdit)
from PyQt5.QtGui import QFont, QDoubleValidator
from PyQt5.QtCore import Qt
from src.services.cari_service import CariService


class CariDialog(QDialog):
    def __init__(self, user_id, parent=None, cari_id=None):
        super().__init__(parent)
        self.user_id = user_id
        self.cari_id = cari_id
        self.is_edit_mode = cari_id is not None
        self.init_ui()
        if self.is_edit_mode:
            self.load_cari()
    
    def init_ui(self):
        """UI başlat"""
        self.setWindowTitle("Cari Hesap Düzenle" if self.is_edit_mode else "Yeni Cari Hesap Ekle")
        self.setMinimumSize(550, 550)
        self.resize(550, 550)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                font-size: 10pt;
                color: #333;
            }
            QLineEdit, QComboBox, QTextEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                font-size: 10pt;
                min-height: 32px;
            }
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
                border: 2px solid #FF9800;
            }
            QPushButton {
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                font-size: 11pt;
                font-weight: bold;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Başlık
        title = QLabel("📋 Cari Hesap Düzenle" if self.is_edit_mode else "📋 Yeni Cari Hesap")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Cari Adı
        layout.addWidget(QLabel("Cari Adı <span style=\"color:#d32f2f\">*</span>"))
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("ABC Şirket")
        layout.addWidget(self.txt_name)
        
        # Cari Tipi
        layout.addWidget(QLabel("Cari Tipi <span style=\"color:#d32f2f\">*</span>"))
        self.combo_type = QComboBox()
        self.combo_type.addItems(["MÜŞTERİ", "TEDARİKÇİ", "HER İKİSİ"])
        layout.addWidget(self.combo_type)
        
        # Telefon
        layout.addWidget(QLabel("Telefon"))
        self.txt_phone = QLineEdit()
        self.txt_phone.setPlaceholderText("05551234567")
        layout.addWidget(self.txt_phone)
        
        # E-posta
        layout.addWidget(QLabel("E-posta"))
        self.txt_email = QLineEdit()
        self.txt_email.setPlaceholderText("info@example.com")
        layout.addWidget(self.txt_email)
        
        # Adres
        layout.addWidget(QLabel("Adres"))
        self.txt_address = QTextEdit()
        self.txt_address.setPlaceholderText("Adres")
        self.txt_address.setMaximumHeight(80)
        layout.addWidget(self.txt_address)
        
        # Başlangıç Bakiyesi
        layout.addWidget(QLabel("Başlangıç Bakiye"))
        self.txt_balance = QLineEdit()
        self.txt_balance.setText("0.00")
        validator = QDoubleValidator(-999999999.99, 999999999.99, 2)
        validator.setNotation(QDoubleValidator.StandardNotation)
        self.txt_balance.setValidator(validator)
        layout.addWidget(self.txt_balance)
        
        # Butonlar
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("💾 Güncelle" if self.is_edit_mode else "💾 Kaydet")
        btn_save.setStyleSheet("background-color: #4CAF50; color: white;")
        btn_save.clicked.connect(self.save_cari)
        btn_layout.addWidget(btn_save)
        
        btn_cancel = QPushButton("❌ İptal")
        btn_cancel.setStyleSheet("background-color: #f44336; color: white;")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        
        layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        self.adjustSize()
        self.setMinimumSize(self.sizeHint())
    
    def load_cari(self):
        """Mevcut cariyi yükle"""
        try:
            cari = CariService.get_cari(self.cari_id)
            if cari:
                self.txt_name.setText(cari.name or "")
                self.combo_type.setCurrentText(cari.cari_type or "MÜŞTERİ")
                self.txt_phone.setText(cari.phone or "")
                self.txt_email.setText(cari.email or "")
                self.txt_address.setText(cari.address or "")
                self.txt_balance.setText(f"{cari.balance:.2f}")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Cari yüklenemedi: {str(e)}")

    def save_cari(self):
        """Cari kaydet/güncelle"""
        # Validasyon
        name = self.txt_name.text().strip()
        cari_type = self.combo_type.currentText()
        phone = self.txt_phone.text().strip()
        email = self.txt_email.text().strip()
        address = self.txt_address.toPlainText().strip()
        balance_text = self.txt_balance.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Uyarı", "Lütfen cari adı giriniz!")
            return
        
        try:
            balance = float(balance_text.replace(',', '.'))
        except ValueError:
            QMessageBox.warning(self, "Uyarı", "Geçersiz bakiye formatı!")
            return
        
        # Kaydet
        try:
            if self.is_edit_mode:
                success, msg = CariService.update_cari(
                    self.cari_id,
                    name=name,
                    cari_type=cari_type,
                    phone=phone or None,
                    email=email or None,
                    address=address or None,
                    balance=balance
                )
            else:
                success, msg = CariService.create_cari(
                    user_id=self.user_id,
                    name=name,
                    cari_type=cari_type,
                    phone=phone or None,
                    email=email or None,
                    address=address or None,
                    balance=balance
                )
            
            if success:
                QMessageBox.information(
                    self,
                    "Başarılı",
                    "Cari hesap güncellendi!" if self.is_edit_mode else "Cari hesap eklendi!"
                )
                self.accept()
            else:
                QMessageBox.critical(self, "Hata", msg)
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Cari eklenirken hata: {str(e)}")
