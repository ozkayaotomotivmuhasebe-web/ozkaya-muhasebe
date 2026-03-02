from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QComboBox, QMessageBox, QSpinBox)
from PyQt5.QtGui import QFont, QDoubleValidator
from PyQt5.QtCore import Qt
from src.services.credit_card_service import CreditCardService


class CreditCardDialog(QDialog):
    def __init__(self, user_id, parent=None, card_id=None):
        super().__init__(parent)
        self.user_id = user_id
        self.card_id = card_id
        self.is_edit_mode = card_id is not None
        self.current_debt = 0.0
        self.init_ui()
        if self.is_edit_mode:
            self.load_card()
    
    def init_ui(self):
        """UI başlat"""
        self.setWindowTitle("Kredi Kartı Düzenle" if self.is_edit_mode else "Yeni Kredi Kartı Ekle")
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
        title = QLabel("💳 Kredi Kartı Düzenle" if self.is_edit_mode else "💳 Yeni Kredi Kartı")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Kart Adı
        layout.addWidget(QLabel("Kart Adı <span style=\"color:#d32f2f\">*</span>"))
        self.txt_card_name = QLineEdit()
        self.txt_card_name.setPlaceholderText("İş Bankası Platinum")
        layout.addWidget(self.txt_card_name)
        
        # Banka Adı
        layout.addWidget(QLabel("Banka Adı <span style=\"color:#d32f2f\">*</span>"))
        self.txt_bank_name = QLineEdit()
        self.txt_bank_name.setPlaceholderText("İş Bankası")
        layout.addWidget(self.txt_bank_name)
        
        # Kart Sahibi
        layout.addWidget(QLabel("Kart Sahibi <span style=\"color:#d32f2f\">*</span>"))
        self.txt_card_holder = QLineEdit()
        self.txt_card_holder.setPlaceholderText("AHMET YILMAZ")
        layout.addWidget(self.txt_card_holder)
        
        # Son 4 Hane
        layout.addWidget(QLabel("Son 4 Hane <span style=\"color:#d32f2f\">*</span>"))
        self.txt_last4 = QLineEdit()
        self.txt_last4.setPlaceholderText("1234")
        self.txt_last4.setMaxLength(4)
        layout.addWidget(self.txt_last4)
        
        # Kart Limiti
        layout.addWidget(QLabel("Kart Limiti (₺) <span style=\"color:#d32f2f\">*</span>"))
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
        btn_save = QPushButton("💾 Güncelle" if self.is_edit_mode else "💾 Kaydet")
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
        self.adjustSize()
        self.setMinimumSize(self.sizeHint())
    
    def load_card(self):
        """Mevcut kartı yükle"""
        try:
            card = CreditCardService.get_card_by_id(self.card_id)
            if card:
                self.txt_card_name.setText(card.card_name or "")
                self.txt_bank_name.setText(card.bank_name or "")
                self.txt_card_holder.setText(card.card_holder or "")
                self.txt_last4.setText(card.card_number_last4 or "")
                self.txt_limit.setText(f"{card.card_limit:.2f}")
                self.spin_closing.setValue(card.closing_day or 1)
                self.spin_due.setValue(card.due_day or 15)
                self.current_debt = card.current_debt or 0.0
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kart yüklenemedi: {str(e)}")

    def save_card(self):
        """Kartı kaydet/güncelle"""
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

        if self.is_edit_mode and card_limit < self.current_debt:
            QMessageBox.warning(self, "Uyarı", "Kart limiti mevcut borçtan küçük olamaz!")
            return
        
        # Kaydet
        try:
            if self.is_edit_mode:
                success, msg = CreditCardService.update_card(
                    self.card_id,
                    card_name=card_name,
                    card_number_last4=last4,
                    card_holder=card_holder,
                    bank_name=bank_name,
                    card_limit=card_limit,
                    closing_day=self.spin_closing.value(),
                    due_day=self.spin_due.value()
                )
            else:
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
                QMessageBox.information(
                    self,
                    "Başarılı",
                    "Kredi kartı güncellendi!" if self.is_edit_mode else "Kredi kartı eklendi!"
                )
                self.accept()
            else:
                QMessageBox.critical(self, "Hata", msg)
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kart eklenirken hata: {str(e)}")
