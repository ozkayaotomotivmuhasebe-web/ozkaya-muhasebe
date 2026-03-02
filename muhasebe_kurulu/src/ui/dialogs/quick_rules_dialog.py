from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                           QTableWidget, QTableWidgetItem, QSpinBox, QMessageBox,
                           QGroupBox, QFormLayout, QLineEdit, QComboBox, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QIcon
import re


class QuickRulesDialog(QDialog):
    """Hızlı işlem kuralları - Pattern matching ve transformasyonlar"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rules = []
        
        self.setWindowTitle("⚡ Hızlı İşlem Kuralları")
        self.setGeometry(100, 100, 1000, 500)
        self.setMinimumSize(1000, 500)
        self.setModal(True)
        self.init_ui()
    
    def init_ui(self):
        """Arayüz elemanlarını oluştur"""
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Başlık
        title = QLabel("⚡ Hızlı İşlem Kuralları")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        layout.addWidget(title)
        
        info = QLabel("İşlem adında belirli kelimeler görünce, müşteri ve kategorisi otomatik atansın")
        info.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(info)
        layout.addSpacing(10)
        
        # Yeni kural ekleme
        add_rule_group = QGroupBox("Yeni Kural Ekle")
        add_rule_layout = QFormLayout()
        
        self.pattern_input = QLineEdit()
        self.pattern_input.setPlaceholderText("Örn: AMAZON, elektrik, ödeme")
        add_rule_layout.addRow("🔍 Pattern (Regex veya Basit Text):", self.pattern_input)
        
        self.action_input = QLineEdit()
        self.action_input.setPlaceholderText("Örn: Amazon.com")
        add_rule_layout.addRow("👤 Atanacak Müşteri Adı (İsteğe bağlı):", self.action_input)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["-- değiştirme yok --", "GELIR", "GIDER"])
        add_rule_layout.addRow("💼 İşlem Tipi:", self.type_combo)
        
        self.category_combo = QComboBox()
        self.category_combo.addItems(["-- değiştirme yok --", "NAKIT", "BANKA", "KREDI_KARTI"])
        add_rule_layout.addRow("📊 Kategori:", self.category_combo)
        
        btn_add = QPushButton("➕ Kural Ekle")
        btn_add.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1976D2; }
        """)
        btn_add.clicked.connect(self.add_rule)
        add_rule_layout.addRow("", btn_add)
        
        add_rule_group.setLayout(add_rule_layout)
        layout.addWidget(add_rule_group)
        layout.addSpacing(10)
        
        # Kurallar tablosu
        table_label = QLabel("Tanımlanan Kurallar:")
        table_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        layout.addWidget(table_label)
        
        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(5)
        self.rules_table.setHorizontalHeaderLabels([
            "Pattern", "Müşteri", "Tip", "Kategori", "İşlem"
        ])
        self.rules_table.verticalHeader().setVisible(False)
        self.rules_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.rules_table.setColumnWidth(0, 200)
        self.rules_table.setColumnWidth(4, 80)
        layout.addWidget(self.rules_table)
        
        # Butonlar
        btn_layout = QHBoxLayout()
        
        btn_ok = QPushButton("✅ Kuralları Onayla")
        btn_ok.setMinimumHeight(40)
        btn_ok.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        btn_ok.clicked.connect(self.accept)
        btn_layout.addWidget(btn_ok)
        
        btn_cancel = QPushButton("❌ İptal")
        btn_cancel.setMinimumHeight(40)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #757575; }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def add_rule(self):
        """Yeni kural ekle"""
        pattern = self.pattern_input.text().strip()
        action = self.action_input.text().strip()
        rule_type = self.type_combo.currentText()
        category = self.category_combo.currentText()
        
        if not pattern:
            QMessageBox.warning(self, "Uyarı", "Lütfen pattern girin!")
            return
        
        # Pattern'i test et
        try:
            re.compile(pattern, re.IGNORECASE)
        except re.error:
            # Regex değilse basit text olarak kabul et
            pattern = re.escape(pattern)
        
        rule = {
            'pattern': pattern,
            'customer': action,
            'type': rule_type if rule_type != "-- değiştirme yok --" else None,
            'category': category if category != "-- değiştirme yok --" else None,
        }
        
        self.rules.append(rule)
        self.refresh_table()
        
        # Input'ları temizle
        self.pattern_input.clear()
        self.action_input.clear()
        self.type_combo.setCurrentIndex(0)
        self.category_combo.setCurrentIndex(0)
        self.pattern_input.setFocus()
    
    def refresh_table(self):
        """Tabloyu kurallarla güncelle"""
        self.rules_table.setRowCount(len(self.rules))
        
        for row_idx, rule in enumerate(self.rules):
            # Pattern
            pattern_item = QTableWidgetItem(rule['pattern'][:50])
            pattern_item.setFlags(pattern_item.flags() & ~Qt.ItemIsEditable)
            self.rules_table.setItem(row_idx, 0, pattern_item)
            
            # Müşteri
            customer_item = QTableWidgetItem(rule['customer'] or "-")
            customer_item.setFlags(customer_item.flags() & ~Qt.ItemIsEditable)
            self.rules_table.setItem(row_idx, 1, customer_item)
            
            # Tip
            type_item = QTableWidgetItem(rule['type'] or "-")
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            self.rules_table.setItem(row_idx, 2, type_item)
            
            # Kategori
            category_item = QTableWidgetItem(rule['category'] or "-")
            category_item.setFlags(category_item.flags() & ~Qt.ItemIsEditable)
            self.rules_table.setItem(row_idx, 3, category_item)
            
            # Sil butonu
            btn_delete = QPushButton("🗑️ Sil")
            btn_delete.setMaximumWidth(80)
            btn_delete.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 5px;
                }
                QPushButton:hover { background-color: #da190b; }
            """)
            btn_delete.clicked.connect(lambda checked, r=row_idx: self.delete_rule(r))
            self.rules_table.setCellWidget(row_idx, 4, btn_delete)
    
    def delete_rule(self, row_idx):
        """Kuralı sil"""
        if 0 <= row_idx < len(self.rules):
            del self.rules[row_idx]
            self.refresh_table()
    
    def apply_rules(self, transaction_name, default_type=None):
        """İşlem adını kurallarla eşleştir ve dönüşüm uygula"""
        result = {
            'customer': None,
            'type': default_type,
            'category': None,
        }
        
        for rule in self.rules:
            try:
                if re.search(rule['pattern'], transaction_name, re.IGNORECASE):
                    if rule['customer']:
                        result['customer'] = rule['customer']
                    if rule['type']:
                        result['type'] = rule['type']
                    if rule['category']:
                        result['category'] = rule['category']
                    break  # İlk matching kuralı kullan
            except:
                pass
        
        return result


# Teste için
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = QuickRulesDialog()
    if dialog.exec_():
        print("Rules:", dialog.rules)
