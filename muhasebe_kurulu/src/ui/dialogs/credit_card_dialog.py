from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QComboBox, QMessageBox, QSpinBox)
from PyQt5.QtGui import QFont, QDoubleValidator
from PyQt5.QtCore import Qt
from src.services.credit_card_service import CreditCardService


class CreditCardDialog(QDialog):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.init_ui()
    
    def init_ui(self):
        """UI başlat"""
        self.setWindowTitle("Yeni Kredi Kartı Ekle")
        self.setMinimumSize(560, 620)
        self.resize(600, 640)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                font-size: 10pt;
                color: #333;
                padding-bottom: 2px;
            }
            QLineEdit, QComboBox, QSpinBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                font-size: 10pt;
                min-height: 28px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                border: 2px solid #9C27B0;
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
        layout.setSpacing(12)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Başlık
        title = QLabel("💳 Yeni Kredi Kartı")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Kart Adı
        layout.addWidget(QLabel("Kart Adı *"))
        self.txt_card_name = QLineEdit()
        self.txt_card_name.setPlaceholderText("İş Bankası Platinum")
        layout.addWidget(self.txt_card_name)
        
        # Banka Adı
        layout.addWidget(QLabel("Banka Adı *"))
        self.txt_bank_name = QLineEdit()
        self.txt_bank_name.setPlaceholderText("İş Bankası")
        layout.addWidget(self.txt_bank_name)
        
        # Kart Sahibi
        layout.addWidget(QLabel("Kart Sahibi *"))
        self.txt_card_holder = QLineEdit()
        self.txt_card_holder.setPlaceholderText("AHMET YILMAZ")
        layout.addWidget(self.txt_card_holder)
        
        # Son 4 Hane
        layout.addWidget(QLabel("Son 4 Hane *"))
        self.txt_last4 = QLineEdit()
        self.txt_last4.setPlaceholderText("1234")
        self.txt_last4.setMaxLength(4)
        layout.addWidget(self.txt_last4)
        
        # Kart Limiti
        layout.addWidget(QLabel("Kart Limiti (₺) *"))
        self.txt_limit = QLineEdit()
        self.txt_limit.setPlaceholderText("0.00")
        validator = QDoubleValidator(0.0, 999999999.99, 2)
        validator.setNotation(QDoubleValidator.StandardNotation)
        self.txt_limit.setValidator(validator)
        layout.addWidget(self.txt_limit)
        
        # Hesap Kesim Günü
        day_layout = QHBoxLayout()
        day_layout.addWidget(QLabel("Kesim Günü:"))
        self.spin_closing = QSpinBox()
        self.spin_closing.setRange(1, 31)
        self.spin_closing.setValue(15)
        day_layout.addWidget(self.spin_closing)
        
        day_layout.addWidget(QLabel("Ödeme Günü:"))
        self.spin_due = QSpinBox()
        self.spin_due.setRange(1, 31)
        self.spin_due.setValue(22)
        day_layout.addWidget(self.spin_due)
        layout.addLayout(day_layout)
        
        # Butonlar
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("💾 Kaydet")
        btn_save.setStyleSheet("background-color: #4CAF50; color: white;")
        btn_save.clicked.connect(self.save_card)
        btn_layout.addWidget(btn_save)
        
        btn_cancel = QPushButton("❌ İptal")
        btn_cancel.setStyleSheet("background-color: #f44336; color: white;")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        
        layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def save_card(self):
        """Kartı kaydet"""
        # Validasyon
        card_name = self.txt_card_name.text().strip()
        bank_name = self.txt_bank_name.text().strip()
        card_holder = self.txt_card_holder.text().strip()
        last4 = self.txt_last4.text().strip()
        limit_text = self.txt_limit.text().strip()
        
        if not card_name:
            QMessageBox.warning(self, "Uyarı", "Lütfen kart adı giriniz!")
            return
        
        if not bank_name:
            QMessageBox.warning(self, "Uyarı", "Lütfen banka adı giriniz!")
            return
        
        if not card_holder:
            QMessageBox.warning(self, "Uyarı", "Lütfen kart sahibi giriniz!")
            return
        
        if not last4 or len(last4) != 4:
            QMessageBox.warning(self, "Uyarı", "Lütfen son 4 hane giriniz (4 rakam)!")
            return
        
        if not limit_text:
            QMessageBox.warning(self, "Uyarı", "Lütfen kart limiti giriniz!")
            return
        
        try:
            card_limit = float(limit_text.replace(',', '.'))
        except ValueError:
            QMessageBox.warning(self, "Uyarı", "Geçersiz limit formatı!")
            return
        
        if card_limit <= 0:
            QMessageBox.warning(self, "Uyarı", "Kart limiti sıfırdan büyük olmalıdır!")
            return
        
        # Kaydet
        try:
            success, msg = CreditCardService.create_card(
                user_id=self.user_id,
                card_name=card_name,
                card_number_last4=last4,
                card_holder=card_holder,
                bank_name=bank_name,
                card_limit=card_limit,
                closing_day=self.spin_closing.value(),
                due_day=self.spin_due.value()
            )
            
            if success:
                QMessageBox.information(self, "Başarılı", "Kredi kartı eklendi!")
                self.accept()
            else:
                QMessageBox.critical(self, "Hata", msg)
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kart eklenirken hata: {str(e)}")
