from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QLabel, QLineEdit, QComboBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class InvoiceWidget(QWidget):
    """Fatura listesi widget'ı"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Arayüz öğelerini başlat"""
        layout = QVBoxLayout()
        
        # Başlık
        title = QLabel("Fatura Listesi")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Filtreler
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Tip:"))
        combo_tip = QComboBox()
        combo_tip.addItems(["Tümü", "Gelen", "Giden"])
        filter_layout.addWidget(combo_tip)
        
        filter_layout.addWidget(QLabel("Durum:"))
        combo_durum = QComboBox()
        combo_durum.addItems(["Tümü", "Taslak", "Gönderilen", "Ödemesi Yapılmış", "Kısmen Ödenen", "İptal"])
        filter_layout.addWidget(combo_durum)
        
        layout.addLayout(filter_layout)
        
        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Fatura No", "Tarih", "Cari", "Tutar", "Vergi", "Toplam", "Durum"
        ])
        self.table.setColumnWidth(0, 120)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 100)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 100)
        self.table.setColumnWidth(6, 100)
        
        layout.addWidget(self.table)
        
        # Butonlar
        btn_layout = QHBoxLayout()
        
        btn_yeni = QPushButton("+ Yeni Fatura")
        btn_layout.addWidget(btn_yeni)
        
        btn_duzen = QPushButton("✏️ Düzenle")
        btn_layout.addWidget(btn_duzen)
        
        btn_sil = QPushButton("🗑️ Sil")
        btn_layout.addWidget(btn_sil)
        
        btn_pdf = QPushButton("📄 PDF İndir")
        btn_layout.addWidget(btn_pdf)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)


class CariWidget(QWidget):
    """Cari hesaplar widget'ı"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Arayüz öğelerini başlat"""
        layout = QVBoxLayout()
        
        # Başlık
        title = QLabel("Cari Hesapları")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Filtreler
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Tip:"))
        combo_tip = QComboBox()
        combo_tip.addItems(["Tümü", "Müşteri", "Tedarikçi", "Diğer"])
        filter_layout.addWidget(combo_tip)
        
        filter_layout.addWidget(QLabel("Ara:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari adı veya vergi no'su ile ara...")
        filter_layout.addWidget(self.search_input)
        
        layout.addLayout(filter_layout)
        
        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Ad", "Tip", "Vergi No", "Email", "Telefon", "Bakiye"
        ])
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 150)
        self.table.setColumnWidth(4, 120)
        self.table.setColumnWidth(5, 100)
        
        layout.addWidget(self.table)
        
        # Butonlar
        btn_layout = QHBoxLayout()
        
        btn_yeni = QPushButton("+ Yeni Cari")
        btn_layout.addWidget(btn_yeni)
        
        btn_duzen = QPushButton("✏️ Düzenle")
        btn_layout.addWidget(btn_duzen)
        
        btn_sil = QPushButton("🗑️ Sil")
        btn_layout.addWidget(btn_sil)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)


class BankWidget(QWidget):
    """Banka hesapları widget'ı"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Arayüz öğelerini başlat"""
        layout = QVBoxLayout()
        
        # Başlık
        title = QLabel("Banka Hesapları")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Banka", "Hesap No", "IBAN", "Bakiye", "Para Birimi", "Durum"
        ])
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 200)
        self.table.setColumnWidth(3, 120)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 100)
        
        layout.addWidget(self.table)
        
        # Butonlar
        btn_layout = QHBoxLayout()
        
        btn_yeni = QPushButton("+ Yeni Hesap")
        btn_layout.addWidget(btn_yeni)
        
        btn_islem = QPushButton("💰 İşlem Gir")
        btn_layout.addWidget(btn_islem)
        
        btn_duzen = QPushButton("✏️ Düzenle")
        btn_layout.addWidget(btn_duzen)
        
        btn_sil = QPushButton("🗑️ Sil")
        btn_layout.addWidget(btn_sil)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
