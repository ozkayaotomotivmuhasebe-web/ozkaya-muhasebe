"""
ÖNIZLEME SCRIPTI — Kira Takip Modülü (4 Sekme)
Projeye hiçbir şey eklemez. Çalıştır: python preview_kira_takip.py
"""
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QLabel, QPushButton, QComboBox,
    QHeaderView, QFrame, QDialog, QFormLayout, QLineEdit, QDateEdit,
    QDoubleSpinBox, QTextEdit, QMenu, QMessageBox, QTabWidget, QColorDialog
)
from PyQt5.QtCore import Qt, QDate, QPoint
from PyQt5.QtGui import QFont, QColor, QBrush
from datetime import date, datetime

AYLAR = ["OCAK", "SUBAT", "MART", "NISAN", "MAYIS", "HAZIRAN", "TEMMUZ", "AGUSTOS", "EYLUL", "EKIM", "KASIM", "ARALIK"]
AYLAR_TR = ["OCAK", "ŞUBAT", "MART", "NİSAN", "MAYIS", "HAZİRAN", "TEMMUZ", "AĞUSTOS", "EYLÜL", "EKİM", "KASIM", "ARALIK"]

C_ODENDI   = QColor("#c8f7c5")
C_ODENMEDI = QColor("#ffd6d6")
C_KISMI    = QColor("#fff3cd")
C_DISARI   = QColor("#ebebeb")
C_ROW_ODD  = QColor("#fff8fc")
C_ROW_EVEN = QColor("#ffffff")

# ─── TORBALI KİRA ────────────────────────────────────────────────────────────
TK_CONTRACTS = [
    {"id":  1,"kiraci":"TORBALI-TIBET BAYRAKTAROGLU",  "bas":"01.04.2025","bit":"01.04.2026","tutar":23000},
    {"id":  2,"kiraci":"TORBALI-ALI YEKTA KILICARSLAN","bas":"27.04.2025","bit":"27.04.2026","tutar":24000},
    {"id":  3,"kiraci":"TORBALI-LEVENT ATAY",           "bas":"12.07.2024","bit":"12.07.2026","tutar":24000},
    {"id":  4,"kiraci":"TORBALI-SAHIN YIGIT",           "bas":"20.09.2024","bit":"20.09.2025","tutar":20000},
    {"id":  5,"kiraci":"FATMA AKBAS",                   "bas":"01.10.2025","bit":"01.10.2026","tutar":31000},
    {"id":  6,"kiraci":"TORBALI-CEVZA SINANLAR(B BLOK)","bas":"18.10.2024","bit":"18.10.2025","tutar":27000},
    {"id":  7,"kiraci":"MEHMET IHSAN ERKUS",            "bas":"03.01.2025","bit":"03.01.2026","tutar":25000},
    {"id":  8,"kiraci":"AHMET KURU",                    "bas":"27.08.2025","bit":"27.08.2026","tutar":25000},
    {"id":  9,"kiraci":"RAMAZAN CAN YAKAPINAR",         "bas":"15.05.2025","bit":"15.05.2026","tutar":26000},
    {"id": 10,"kiraci":"YAHYA ELDENIZ(DAIRE 7)",        "bas":"01.05.2025","bit":"01.05.2026","tutar":22000},
    {"id": 11,"kiraci":"EMRE DEMIRAY",                  "bas":"22.05.2025","bit":"22.05.2026","tutar":26000},
    {"id": 12,"kiraci":"AYSE KAYA",                     "bas":"27.06.2025","bit":"27.06.2026","tutar":20000},
    {"id": 13,"kiraci":"PELIN KATRANCI",                "bas":"01.07.2025","bit":"01.07.2026","tutar":20000},
    {"id": 14,"kiraci":"SINEM ARICAN",                  "bas":"15.07.2025","bit":"15.07.2026","tutar":24000},
    {"id": 15,"kiraci":"AHMET KATKO",                   "bas":"20.08.2025","bit":"20.08.2026","tutar":25000},
    {"id": 16,"kiraci":"OZLEM KARADOGAN",               "bas":"25.08.2025","bit":"25.08.2026","tutar":25000},
    {"id": 17,"kiraci":"CEMAL UGUR",                    "bas":"03.09.2025","bit":"03.09.2026","tutar":23500},
    {"id": 18,"kiraci":"MURAT MAMUK",                   "bas":"01.10.2025","bit":"01.10.2026","tutar":24000},
    {"id": 19,"kiraci":"MAHMUT AKIN",                   "bas":"01.10.2025","bit":"01.10.2026","tutar":26000},
    {"id": 20,"kiraci":"FILIZ SATIR",                   "bas":"01.10.2025","bit":"01.10.2026","tutar":23500},
    {"id": 21,"kiraci":"BULENT AY",                     "bas":"05.10.2025","bit":"05.10.2026","tutar":25000},
    {"id": 22,"kiraci":"KADIR GURBUZ",                  "bas":"06.11.2025","bit":"06.11.2026","tutar":23000},
    {"id": 23,"kiraci":"NILUFER SEN",                   "bas":"13.10.2025","bit":"13.10.2026","tutar":24000},
    {"id": 24,"kiraci":"TORBALI-OMER TEKIN",            "bas":"21.03.2025","bit":"21.04.2026","tutar":24000},
]
TK_PAYMENTS = {
    1:{1:"ODENDI",2:"ODENDI"}, 2:{1:"ODENDI",2:"ODENDI"}, 3:{1:"ODENDI",2:"ODENDI"},
    6:{1:"ODENDI",2:"ODENDI"}, 8:{1:"ODENDI",2:"ODENDI"}, 9:{1:"ODENDI",2:"ODENDI"},
    11:{1:"ODENDI"}, 13:{1:"ODENDI"}, 17:{1:"ODENDI"}, 18:{1:"ODENDI"},
    19:{1:"ODENDI",2:"ODENDI"}, 20:{1:"ODENDI",2:"ODENDI",3:"ODENDI"},
    21:{1:"ODENDI"}, 22:{1:"ODENDI",2:"ODENDI"}, 23:{1:"ODENDI",2:"ODENDI"},
    24:{1:"ODENDI",2:"ODENDI",3:"ODENDI",4:"KISMI:10.000 KALDI",
        5:"ODENMEDI",6:"ODENMEDI",7:"ODENMEDI",9:"KISMI:80BIN ATTI"},
}

# ─── TORBALI AIDAT ───────────────────────────────────────────────────────────
TA_CONTRACTS = [
    {"id":  1,"kiraci":"TORBALI-TIBET BAYRAKTAROGLU",   "bas":"01.04.2024","bit":"01.04.2025","tutar":2000},
    {"id":  2,"kiraci":"TORBALI-ALI YEKTA KILICARSLAN", "bas":"27.04.2024","bit":"27.04.2025","tutar":2000},
    {"id":  3,"kiraci":"TORBALI-LEVENT ATAY",            "bas":"12.07.2025","bit":"12.07.2026","tutar":2000},
    {"id":  4,"kiraci":"TORBALI-SAHIN YIGIT",            "bas":"27.09.2025","bit":"27.09.2026","tutar":2000},
    {"id":  5,"kiraci":"AHMET KURU",                     "bas":"27.08.2025","bit":"27.08.2026","tutar":2000},
    {"id":  6,"kiraci":"FERID YONTEIM",                  "bas":"01.10.2024","bit":"01.10.2025","tutar":2000},
    {"id":  7,"kiraci":"FATMA AKBAS",                    "bas":"01.10.2024","bit":"01.10.2025","tutar":2000},
    {"id":  8,"kiraci":"TORBALI-CEVZA SINANLAR(B BLOK)", "bas":"18.10.2024","bit":"18.10.2025","tutar":2000},
    {"id":  9,"kiraci":"MEHMET IHSAN ERKUS",             "bas":"10.12.2024","bit":"10.12.2025","tutar":2000},
    {"id": 10,"kiraci":"BURCU YALCI(DAIRE 11)",          "bas":"01.05.2025","bit":"01.05.2026","tutar":2000},
    {"id": 11,"kiraci":"YAHYA ELDENIZ(DAIRE 7)",         "bas":"01.05.2025","bit":"01.05.2026","tutar":2000},
    {"id": 12,"kiraci":"RAMAZAN CAN YAKAPINAR",          "bas":"15.05.2025","bit":"15.05.2026","tutar":2000},
    {"id": 13,"kiraci":"EMRE DEMIRAY",                   "bas":"22.05.2025","bit":"22.05.2026","tutar":2000},
    {"id": 14,"kiraci":"AYSE KAYA",                      "bas":"27.06.2025","bit":"27.06.2026","tutar":2000},
    {"id": 15,"kiraci":"PELIN KATRANCI",                 "bas":"01.07.2025","bit":"01.07.2026","tutar":2000},
    {"id": 16,"kiraci":"SINEM ARICAN",                   "bas":"15.07.2025","bit":"15.07.2026","tutar":2000},
    {"id": 17,"kiraci":"SULEYMAN DEMIR",                 "bas":"13.08.2025","bit":"13.08.2026","tutar":2000},
    {"id": 18,"kiraci":"AHMET KATKO",                    "bas":"20.08.2025","bit":"20.08.2026","tutar":2000},
    {"id": 19,"kiraci":"OZLEM KARADOGAN",                "bas":"25.08.2025","bit":"25.08.2026","tutar":2000},
    {"id": 20,"kiraci":"CEMAL UGUR",                     "bas":"03.09.2025","bit":"03.09.2026","tutar":2000},
    {"id": 21,"kiraci":"MURAT MAMUK",                    "bas":"01.10.2025","bit":"01.10.2026","tutar":2000},
    {"id": 22,"kiraci":"MAHMUT AKIN",                    "bas":"01.10.2025","bit":"01.10.2026","tutar":2000},
    {"id": 23,"kiraci":"FILIZ SATIR",                    "bas":"01.10.2025","bit":"01.10.2026","tutar":2000},
    {"id": 24,"kiraci":"BULENT AY",                      "bas":"05.10.2025","bit":"05.10.2026","tutar":2000},
    {"id": 25,"kiraci":"KADIR GURBUZ",                   "bas":"06.11.2025","bit":"06.11.2026","tutar":2000},
    {"id": 26,"kiraci":"NILUFER SEN",                    "bas":"13.10.2025","bit":"13.10.2026","tutar":2000},
]
TA_PAYMENTS = {
    3:{1:"ODENDI",2:"ODENDI"}, 8:{1:"ODENDI",2:"ODENDI"},
    13:{1:"ODENDI"}, 22:{1:"ODENDI",2:"ODENDI"},
    23:{1:"ODENDI",2:"ODENDI",3:"ODENDI"}, 24:{1:"ODENDI"},
    25:{1:"ODENDI",2:"ODENDI"}, 26:{1:"ODENDI",2:"ODENDI"},
}

# ─── DUKKANLAR ───────────────────────────────────────────────────────────────
DK_CONTRACTS = [
    {"id":1,"kiraci":"1.SANAYI DURUKAN DEMIREL TORBA TOLGA BEY","odeme_gunu":"HER AYIN 1I",         "bas":"13.01.2025","bit":"13.01.2026","tutar":45000},
    {"id":2,"kiraci":"HALKPINAR UPSOLDI BATTERY GUNLUKOY",       "odeme_gunu":"HER AYIN 1 VE 5 ARASI","bas":"01.02.2025","bit":"01.02.2026","tutar":47000},
    {"id":3,"kiraci":"HALKPINAR KUASAR",                         "odeme_gunu":"HER AYIN 20SI",        "bas":"01.02.2025","bit":"01.03.2026","tutar":48000},
    {"id":4,"kiraci":"OMY ELEKTRIK",                             "odeme_gunu":"",                     "bas":"30.06.2023","bit":"10.01.2027","tutar":33000},
    {"id":5,"kiraci":"1.SAL. SIT. DURUKAN USTYAT ARDA KAZIOGLU", "odeme_gunu":"HER AYIN 1I",         "bas":"15.05.2025","bit":"15.05.2026","tutar":20000},
    {"id":6,"kiraci":"HALKAPARK-TIMAY YURDAKUL OTO.",            "odeme_gunu":"HER AYIN 1 VE 5 ARASI","bas":"01.06.2025","bit":"01.06.2026","tutar":28000},
    {"id":7,"kiraci":"KARAGBAGLAR SICIL-ALPARSLA TASARIM",       "odeme_gunu":"HER AYIN 1 VE 5 ARASI","bas":"01.12.2025","bit":"01.12.2026","tutar":18000},
    {"id":8,"kiraci":"DEYTIRK OTOMOTIV / VAY MOTORLU ARACLAR",   "odeme_gunu":"yeni sozlesme",        "bas":"01.12.2025","bit":"01.12.2026","tutar":15000},
    {"id":9,"kiraci":"(ORTAK GIDER)",                            "odeme_gunu":"",                     "bas":"01.01.2025","bit":"31.12.2026","tutar": 4250},
    {"id":10,"kiraci":"DEPO",                                    "odeme_gunu":"",                     "bas":"27.11.2025","bit":"27.11.2026","tutar": 6000},
]
DK_PAYMENTS = {
    1:{1:"ODENDI",2:"ODENDI"}, 2:{1:"ODENDI"},
    4:{1:"ODENDI",2:"ODENDI",3:"ODENDI"},
    5:{1:"ODENDI",2:"ODENDI"}, 6:{1:"ODENDI",2:"ODENDI"},
    7:{1:"ODENDI",2:"ODENDI",3:"ODENDI"}, 10:{1:"ODENDI"},
}

# ─── GAZIANTEP ───────────────────────────────────────────────────────────────
GZ_CONTRACTS = [
    {"id": 1,"kiraci":"ALA ALI (KAT:3) [GAZIANTEP]",               "odeme_gunu":"HER AYIN BINDE","bas":"01.01.2025","bit":"01.01.2026","tutar":12000},
    {"id": 2,"kiraci":"HAZIM SHAMTA (KAT:4) [GAZIANTEP]",          "odeme_gunu":"HER AYIN BINDE","bas":"01.01.2025","bit":"01.01.2026","tutar": 8000},
    {"id": 3,"kiraci":"ADDOLBASIL HAC HALIL(TERAS) [GAZIANTEP]",   "odeme_gunu":"HER AYIN BINDE","bas":"01.01.2025","bit":"01.01.2026","tutar": 9000},
    {"id": 4,"kiraci":"NEVRAS ELBERIK (KAT:2 D:4) [GAZIANTEP]",   "odeme_gunu":"HER AYIN BINDE","bas":"01.01.2025","bit":"01.01.2026","tutar":12000},
    {"id": 5,"kiraci":"MEHMET ALI USTUNODA (KAT:3) [GAZIANTEP]",  "odeme_gunu":"HER AYIN BINDE","bas":"01.01.2025","bit":"01.01.2026","tutar":12000},
    {"id": 6,"kiraci":"HASAN FROL (HILAL SITESI) [GAZIANTEP]",    "odeme_gunu":"HER AYIN BINDE","bas":"01.01.2025","bit":"01.06.2026","tutar":17000},
    {"id": 7,"kiraci":"AMIMAR MILO (KAT:1) [GAZIANTEP]",          "odeme_gunu":"HER AYIN BINDE","bas":"01.03.2025","bit":"01.01.2026","tutar":12000},
    {"id": 8,"kiraci":"AHMET ALBAKKAR (KAT:1) [GAZIANTEP]",       "odeme_gunu":"HER AYIN BINDE","bas":"01.01.2025","bit":"01.01.2026","tutar":12000},
    {"id": 9,"kiraci":"MAHMUD MENSHEFI (ZEMIN KAT) [GAZIANTEP]",  "odeme_gunu":"HER AYIN BINDE","bas":"01.01.2025","bit":"01.01.2026","tutar": 8000},
    {"id":10,"kiraci":"ALA ALI (AMBAR) [GAZIANTEP]",              "odeme_gunu":"HER AYIN BINDE","bas":"01.12.2023","bit":"01.12.2024","tutar": 5500},
    {"id":11,"kiraci":"ILHAN ERCE (KAT:3 DOLOPER APT) [GAZIANTEP]","odeme_gunu":"HER AYIN BINDE","bas":"01.01.2025","bit":"01.01.2026","tutar":15000},
]
GZ_PAYMENTS = {6:{1:"KISMI:COKDU"}}

# ─── DEMO ÖDEME DETAYLARI (gerçek projede işlemler DB'sinden gelir) ──────────
TK_ODEME_DETAY = {
    1: {1:{"tarih":"03.01.2026","banka":"Ziraat Bankası","aciklama":"EFT"},
        2:{"tarih":"05.02.2026","banka":"Ziraat Bankası","aciklama":"EFT"}},
    2: {1:{"tarih":"02.01.2026","banka":"İş Bankası","aciklama":"Havale"},
        2:{"tarih":"04.02.2026","banka":"İş Bankası","aciklama":"Havale"}},
    3: {1:{"tarih":"12.01.2026","banka":"Garanti BBVA","aciklama":"EFT"},
        2:{"tarih":"10.02.2026","banka":"Garanti BBVA","aciklama":"EFT"}},
    6: {1:{"tarih":"15.01.2026","banka":"Akbank","aciklama":"Nakit"},
        2:{"tarih":"18.02.2026","banka":"Akbank","aciklama":"Nakit"}},
    8: {1:{"tarih":"27.01.2026","banka":"Yapı Kredi","aciklama":"EFT"},
        2:{"tarih":"27.02.2026","banka":"Yapı Kredi","aciklama":"EFT"}},
    9: {1:{"tarih":"16.01.2026","banka":"Ziraat Bankası","aciklama":"Havale"},
        2:{"tarih":"17.02.2026","banka":"Ziraat Bankası","aciklama":"Havale"}},
    11:{1:{"tarih":"22.01.2026","banka":"Halkbank","aciklama":"EFT"}},
    13:{1:{"tarih":"02.01.2026","banka":"İş Bankası","aciklama":"EFT"}},
    17:{1:{"tarih":"05.01.2026","banka":"Akbank","aciklama":"Nakit"}},
    18:{1:{"tarih":"03.01.2026","banka":"Vakıfbank","aciklama":"EFT"}},
    19:{1:{"tarih":"03.01.2026","banka":"Garanti BBVA","aciklama":"Havale"},
        2:{"tarih":"04.02.2026","banka":"Garanti BBVA","aciklama":"Havale"}},
    20:{1:{"tarih":"01.01.2026","banka":"Ziraat Bankası","aciklama":"EFT"},
        2:{"tarih":"02.02.2026","banka":"Ziraat Bankası","aciklama":"EFT"},
        3:{"tarih":"01.03.2026","banka":"Ziraat Bankası","aciklama":"EFT"}},
    21:{1:{"tarih":"06.01.2026","banka":"İş Bankası","aciklama":"Havale"}},
    22:{1:{"tarih":"07.01.2026","banka":"Akbank","aciklama":"EFT"},
        2:{"tarih":"06.02.2026","banka":"Akbank","aciklama":"EFT"}},
    23:{1:{"tarih":"14.01.2026","banka":"Garanti BBVA","aciklama":"EFT"},
        2:{"tarih":"13.02.2026","banka":"Garanti BBVA","aciklama":"EFT"}},
    24:{1:{"tarih":"21.01.2026","banka":"Yapı Kredi","aciklama":"EFT"},
        2:{"tarih":"20.02.2026","banka":"Yapı Kredi","aciklama":"EFT"},
        3:{"tarih":"21.03.2026","banka":"Yapı Kredi","aciklama":"EFT"},
        4:{"tarih":"","banka":"","aciklama":"10.000 TL eksiği var"}},
}
TA_ODEME_DETAY = {
    3: {1:{"tarih":"14.01.2026","banka":"Garanti BBVA","aciklama":"EFT"},
        2:{"tarih":"13.02.2026","banka":"Garanti BBVA","aciklama":"EFT"}},
    8: {1:{"tarih":"18.01.2026","banka":"Akbank","aciklama":"Nakit"},
        2:{"tarih":"19.02.2026","banka":"Akbank","aciklama":"Nakit"}},
    13:{1:{"tarih":"22.01.2026","banka":"Halkbank","aciklama":"EFT"}},
    22:{1:{"tarih":"03.01.2026","banka":"Ziraat","aciklama":"EFT"},
        2:{"tarih":"04.02.2026","banka":"Ziraat","aciklama":"EFT"}},
    23:{1:{"tarih":"01.01.2026","banka":"İş Bankası","aciklama":"EFT"},
        2:{"tarih":"02.02.2026","banka":"İş Bankası","aciklama":"EFT"},
        3:{"tarih":"01.03.2026","banka":"İş Bankası","aciklama":"EFT"}},
    24:{1:{"tarih":"06.01.2026","banka":"Yapı Kredi","aciklama":"Havale"}},
    25:{1:{"tarih":"07.01.2026","banka":"Akbank","aciklama":"EFT"},
        2:{"tarih":"06.02.2026","banka":"Akbank","aciklama":"EFT"}},
    26:{1:{"tarih":"14.01.2026","banka":"Garanti BBVA","aciklama":"EFT"},
        2:{"tarih":"13.02.2026","banka":"Garanti BBVA","aciklama":"EFT"}},
}
DK_ODEME_DETAY = {
    1: {1:{"tarih":"02.01.2026","banka":"Ziraat Bankası","aciklama":"EFT"},
        2:{"tarih":"03.02.2026","banka":"Ziraat Bankası","aciklama":"EFT"}},
    2: {1:{"tarih":"04.01.2026","banka":"İş Bankası","aciklama":"EFT"}},
    4: {1:{"tarih":"05.01.2026","banka":"Akbank","aciklama":"Nakit"},
        2:{"tarih":"04.02.2026","banka":"Akbank","aciklama":"Nakit"},
        3:{"tarih":"03.03.2026","banka":"Akbank","aciklama":"Nakit"}},
    5: {1:{"tarih":"15.01.2026","banka":"Yapı Kredi","aciklama":"EFT"},
        2:{"tarih":"14.02.2026","banka":"Yapı Kredi","aciklama":"EFT"}},
    6: {1:{"tarih":"03.01.2026","banka":"Garanti BBVA","aciklama":"Havale"},
        2:{"tarih":"02.02.2026","banka":"Garanti BBVA","aciklama":"Havale"}},
    7: {1:{"tarih":"03.01.2026","banka":"Vakıfbank","aciklama":"EFT"},
        2:{"tarih":"02.02.2026","banka":"Vakıfbank","aciklama":"EFT"},
        3:{"tarih":"01.03.2026","banka":"Vakıfbank","aciklama":"EFT"}},
    10:{1:{"tarih":"27.01.2026","banka":"Nakit","aciklama":"Elden"}},
}
GZ_ODEME_DETAY = {}


# ──────────────────────────────────────────────────────────────────────────────
class PaymentNoteDialog(QDialog):
    def __init__(self, kiraci, ay_adi, mevcut="", parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{kiraci} - {ay_adi}")
        self.setMinimumWidth(380)
        lay = QVBoxLayout(self); lay.setContentsMargins(16,16,16,16)
        lay.addWidget(QLabel(f"<b>{kiraci}</b> - {ay_adi} için not:"))
        self.note = QTextEdit(); self.note.setText(mevcut); self.note.setMaximumHeight(100)
        lay.addWidget(self.note)
        h = QHBoxLayout()
        c = QPushButton("İptal"); c.clicked.connect(self.reject)
        s = QPushButton("Kaydet"); s.clicked.connect(self.accept)
        s.setStyleSheet("background:#2196f3;color:white;padding:5px 16px;border-radius:4px;")
        h.addStretch(); h.addWidget(c); h.addWidget(s)
        lay.addLayout(h)
    def get_note(self): return self.note.toPlainText().strip()


class OdemeDetayDialog(QDialog):
    """Ödeme kaydederken tarih + banka bilgisi girmek için."""
    def __init__(self, kiraci, ay_adi, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Ödeme Detayı — {ay_adi}")
        self.setMinimumWidth(370)
        lay = QFormLayout(self); lay.setContentsMargins(18,18,18,18); lay.setVerticalSpacing(10)
        self.tarih = QDateEdit(); self.tarih.setCalendarPopup(True); self.tarih.setDisplayFormat("dd.MM.yyyy")
        self.tarih.setDate(QDate.currentDate())
        lay.addRow("Ödeme Tarihi:", self.tarih)
        self.banka = QLineEdit(); self.banka.setPlaceholderText("Ziraat, İş Bankası, Nakit...")
        lay.addRow("Banka / Ödeme Yeri:", self.banka)
        self.aciklama = QLineEdit(); self.aciklama.setPlaceholderText("EFT, Havale, Nakit...")
        lay.addRow("Açıklama:", self.aciklama)
        btns = QHBoxLayout()
        atla = QPushButton("Atla"); atla.clicked.connect(self.reject)
        atla.setStyleSheet("background:#9e9e9e;color:white;padding:5px 16px;border-radius:4px;")
        kaydet = QPushButton("Kaydet"); kaydet.clicked.connect(self.accept)
        kaydet.setStyleSheet("background:#4caf50;color:white;padding:5px 16px;border-radius:4px;")
        btns.addStretch(); btns.addWidget(atla); btns.addWidget(kaydet)
        lay.addRow(btns)

    def get_data(self):
        return {"tarih": self.tarih.date().toString("dd.MM.yyyy"),
                "banka": self.banka.text().strip(),
                "aciklama": self.aciklama.text().strip()}


class KiraciDokumDialog(QDialog):
    """Kiracının tüm ödeme dökümü: tarih, banka, tutar."""
    def __init__(self, kiraci, contract, payments, odeme_detay, year, hdr_color, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Kiracı Dökümü — {kiraci}")
        self.setMinimumWidth(920); self.setMinimumHeight(560)
        lay = QVBoxLayout(self); lay.setContentsMargins(16,16,16,16); lay.setSpacing(8)

        # ─── Ödeme gününü tespit et ───────────────────────────────────────────
        import re as _re
        bas_dt = datetime.strptime(contract["bas"],"%d.%m.%Y").date()
        bit_dt = datetime.strptime(contract["bit"],"%d.%m.%Y").date()
        tutar  = contract.get("tutar", 0)
        og_txt = contract.get("odeme_gunu", "")
        pay_day = None
        if og_txt:
            nums = _re.findall(r'\d+', og_txt)
            if nums: pay_day = int(nums[0])
        if pay_day is not None:
            pay_day = max(1, min(pay_day, 28))   # güvenli aralık

        today = date.today()

        # ─── Başlık satırı ───────────────────────────────────────────────────
        hl = QHBoxLayout()
        tl = QLabel(f"<b style='font-size:13pt'>{kiraci}</b>")
        tl.setStyleSheet(f"color:{hdr_color};")
        hl.addWidget(tl); hl.addStretch()
        og_goster = og_txt if og_txt else f"Her ayın {pay_day}i"
        info = QLabel(
            f"Sözleşme: {contract.get('bas','?')} – {contract.get('bit','?')}"
            f"&nbsp;&nbsp;|&nbsp;&nbsp;Ödeme Günü: <b>{og_goster}</b>"
            f"&nbsp;&nbsp;|&nbsp;&nbsp;Aylık: <b>₺{tutar:,.0f}</b>".replace(",",".")
        )
        info.setStyleSheet("color:#444;font-size:10pt;"); hl.addWidget(info)
        lay.addLayout(hl)

        # ─── Gecikme uyarı banner ─────────────────────────────────────────────
        gecikme_rows = []  # doldurulacak

        # ─── Tablo ───────────────────────────────────────────────────────────
        tbl = QTableWidget(); tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        tbl.verticalHeader().setVisible(False); tbl.setSelectionBehavior(QTableWidget.SelectRows)
        tbl.setStyleSheet(
            f"QTableWidget{{gridline-color:#ddd;font-size:10pt;background:white;}}"
            f"QHeaderView::section{{background:{hdr_color};color:white;font-weight:bold;"
            f"padding:5px;border:none;}}"
        )
        tbl.setColumnCount(7)
        tbl.setHorizontalHeaderLabels(
            ["AY","BEKLENEN TARİH","DURUM","ÖDEME TARİHİ","BANKA / ÖDEME YERİ","TUTAR","AÇIKLAMA"]
        )

        rows = []
        for ay in range(1,13):
            mst = date(year,ay,1)
            in_c = (bas_dt <= date(year,ay,28)) and (bit_dt >= mst)
            if not in_c: continue
            rows.append((ay, payments.get(ay,"ODENMEDI"), odeme_detay.get(ay,{})))

        C_GECIKME = QColor("#ff5252")   # parlak kırmızı

        tbl.setRowCount(len(rows))
        toplam_odenen = 0.0; toplam_bekleyen = 0.0; gecikme_sayisi = 0
        for row,(ay,durum,detay) in enumerate(rows):
            ay_adi = AYLAR_TR[ay-1]

            # Beklenen ödeme tarihi — sadece ödeme günü belli ise hesapla
            if pay_day is not None:
                try:
                    beklenen_dt = date(year, ay, pay_day)
                except ValueError:
                    import calendar
                    son_gun = calendar.monthrange(year,ay)[1]
                    beklened_dt = date(year, ay, min(pay_day, son_gun))
                    beklenen_dt = beklened_dt
                beklenen_txt = beklenen_dt.strftime("%d.%m.%Y")
                gecikti = (durum == "ODENMEDI") and (beklenen_dt < today)
            else:
                beklenen_dt = None
                beklenen_txt = "—"
                gecikti = False

            if durum == "ODENDI":
                durum_txt = "✅ Ödendi"; bg = C_ODENDI
                tarih = detay.get("tarih","—") or "—"
                banka = detay.get("banka","—") or "—"
                aciklama = detay.get("aciklama","")
                tutar_txt = "₺{:,.0f}".format(tutar).replace(",","."); toplam_odenen += tutar
            elif gecikti:
                durum_txt = "🔴 GECİKMİŞ"; bg = C_GECIKME
                tarih = banka = "—"; aciklama = f"{(today - beklenen_dt).days} gün geçti"
                tutar_txt = "₺{:,.0f}".format(tutar).replace(",","."); toplam_bekleyen += tutar
                gecikme_sayisi += 1
            elif durum == "ODENMEDI":
                durum_txt = "❌ Ödenmedi"; bg = C_ODENMEDI
                tarih = banka = "—"; aciklama = "Henüz bekleniyor"
                tutar_txt = "—"; toplam_bekleyen += tutar
            elif durum.startswith("KISMI:"):
                durum_txt = "⚠️ Kısmi/Not"; bg = C_KISMI
                tarih = detay.get("tarih","—") or "—"
                banka = detay.get("banka","—") or "—"
                aciklama = durum[6:]
                tutar_txt = "₺{:,.0f}".format(tutar).replace(",",".")
            else:
                durum_txt = "—"; bg = C_DISARI
                tarih = banka = "—"; aciklama = ""; tutar_txt = "—"

            for col,txt in enumerate([ay_adi, beklenen_txt, durum_txt, tarih, banka, tutar_txt, aciklama]):
                it = QTableWidgetItem(txt); it.setBackground(QBrush(bg))
                it.setTextAlignment((Qt.AlignRight if col==5 else Qt.AlignCenter)|Qt.AlignVCenter)
                if gecikti:
                    it.setForeground(QBrush(QColor("white")))
                    f = QFont(); f.setBold(True); it.setFont(f)
                tbl.setItem(row, col, it)
            tbl.setRowHeight(row, 30)

        tbl.resizeColumnsToContents()
        tbl.setColumnWidth(4, max(tbl.columnWidth(4), 165))
        tbl.setColumnWidth(6, max(tbl.columnWidth(6), 160))

        # Gecikme banner (tablonun üstünde göster)
        if gecikme_sayisi > 0:
            warn = QLabel(f"  ⚠️  Bu kiracının {gecikme_sayisi} ay ödemesi gecikmiş! Toplam: ₺{toplam_bekleyen:,.0f}".replace(",","."))
            warn.setStyleSheet(
                "background:#d32f2f;color:white;font-weight:bold;font-size:11pt;"
                "padding:8px 14px;border-radius:5px;"
            )
            warn.setAlignment(Qt.AlignCenter)
            lay.addWidget(warn)

        lay.addWidget(tbl)

        # ─── Özet bar ────────────────────────────────────────────────────────
        ozet_style = "font-size:11pt;padding:8px 14px;border-radius:5px;"
        if gecikme_sayisi > 0:
            ozet_style += "background:#fff3e0;"
        else:
            ozet_style += "background:#e8f5e9;"
        ozet = QLabel(
            f"<b>Toplam Ödenen:</b> ₺{toplam_odenen:,.0f}"
            f"&nbsp;&nbsp;|&nbsp;&nbsp;<b>Bekleyen/Gecikmiş:</b> ₺{toplam_bekleyen:,.0f}".replace(",",".")
        )
        ozet.setStyleSheet(ozet_style)
        lay.addWidget(ozet)

        close_btn = QPushButton("Kapat")
        close_btn.setStyleSheet("background:#607d8b;color:white;padding:7px 22px;border-radius:5px;font-size:10pt;")
        close_btn.clicked.connect(self.accept)
        hb = QHBoxLayout(); hb.addStretch(); hb.addWidget(close_btn)
        lay.addLayout(hb)


class ContractDialog(QDialog):
    def __init__(self, has_odeme_gunu=False, contract=None, parent=None):
        super().__init__(parent)
        self.has_og = has_odeme_gunu
        edit_mode = contract is not None
        self.setWindowTitle("Kiracı Düzenle" if edit_mode else "Yeni Kiracı Ekle")
        self.setMinimumWidth(440)
        lay = QFormLayout(self); lay.setVerticalSpacing(10); lay.setContentsMargins(20,20,20,20)
        self.kiraci_edit = QLineEdit()
        self.kiraci_edit.setPlaceholderText("Kiracı tam adı")
        if edit_mode: self.kiraci_edit.setText(contract.get("kiraci",""))
        lay.addRow("Kiracı Adı:", self.kiraci_edit)
        self.odeme_edit = QLineEdit()
        self.odeme_edit.setPlaceholderText("HER AYIN 1İ, HER AYIN 5İ gibi (boş bırakılabilir)")
        if edit_mode: self.odeme_edit.setText(contract.get("odeme_gunu",""))
        lay.addRow("Ödeme Günü:", self.odeme_edit)
        h = QHBoxLayout()
        self.bas = QDateEdit(); self.bas.setCalendarPopup(True); self.bas.setDisplayFormat("dd.MM.yyyy")
        self.bit = QDateEdit(); self.bit.setCalendarPopup(True); self.bit.setDisplayFormat("dd.MM.yyyy")
        if edit_mode:
            from datetime import datetime as _dt
            self.bas.setDate(QDate.fromString(contract["bas"],"dd.MM.yyyy"))
            self.bit.setDate(QDate.fromString(contract["bit"],"dd.MM.yyyy"))
        else:
            self.bas.setDate(QDate.currentDate()); self.bit.setDate(QDate.currentDate().addYears(1))
        h.addWidget(self.bas); h.addWidget(QLabel("—")); h.addWidget(self.bit)
        lay.addRow("Sözleşme Tarihi:", h)
        self.tutar_edit = QDoubleSpinBox(); self.tutar_edit.setRange(0,9999999)
        self.tutar_edit.setSingleStep(500); self.tutar_edit.setSuffix(" TL"); self.tutar_edit.setDecimals(0)
        if edit_mode: self.tutar_edit.setValue(contract.get("tutar",0))
        lay.addRow("Aylık Tutar:", self.tutar_edit)
        btn = QHBoxLayout()
        ci = QPushButton("İptal"); ci.clicked.connect(self.reject)
        si = QPushButton("Kaydet"); si.clicked.connect(self.accept)
        si.setStyleSheet("background:#4caf50;color:white;padding:6px 18px;border-radius:4px;")
        ci.setStyleSheet("background:#9e9e9e;color:white;padding:6px 18px;border-radius:4px;")
        btn.addStretch(); btn.addWidget(ci); btn.addWidget(si)
        lay.addRow(btn)

    def get_data(self):
        d = {
            "kiraci": self.kiraci_edit.text().strip(),
            "bas":    self.bas.date().toString("dd.MM.yyyy"),
            "bit":    self.bit.date().toString("dd.MM.yyyy"),
            "tutar":  float(self.tutar_edit.value()),
        }
        d["odeme_gunu"] = self.odeme_edit.text().strip()
        return d


class TahsilatWidget(QWidget):
    def __init__(self, title, hdr_color, contracts, payments, has_odeme_gunu=False,
                 demo_year=2026, odeme_detay=None):
        super().__init__()
        self.title        = title
        self.hdr_color    = hdr_color
        self.year         = demo_year
        self.contracts    = list(contracts)
        self.payments     = {k: dict(v) for k, v in payments.items()}
        self.has_og       = has_odeme_gunu
        self.yil_nots     = {}   # {contract_id: "not metni"}
        self.odeme_detay  = {k: dict(v) for k, v in (odeme_detay or {}).items()}  # {cid: {ay: {tarih,banka,aciklama}}}
        self._build(); self._load()

    def _build(self):
        lay = QVBoxLayout(self); lay.setContentsMargins(8,8,8,8); lay.setSpacing(6)

        # Ust bar
        top = QHBoxLayout()
        lbl = QLabel(self.title); lbl.setFont(QFont("Arial",12,QFont.Bold))
        lbl.setStyleSheet(f"color:{self.hdr_color};padding:2px;"); top.addWidget(lbl)
        top.addStretch()
        top.addWidget(QLabel("Yil:"))
        self.yc = QComboBox()
        for y in range(2023,2028): self.yc.addItem(str(y))
        self.yc.setCurrentText(str(self.year)); self.yc.setFixedWidth(75)
        self.yc.currentTextChanged.connect(lambda t: self._year_chg(t))
        top.addWidget(self.yc)
        ab = QPushButton("+ Kiracı Ekle")
        ab.setStyleSheet(f"background:{self.hdr_color};color:white;font-weight:bold;padding:5px 12px;border-radius:5px;")
        ab.clicked.connect(self._add); top.addWidget(ab)
        lay.addLayout(top)

        # KPI
        kr = QHBoxLayout()
        self.kpis = {}
        for k,v,c in [("toplam","—","#3f51b5"),("odendi","—","#4caf50"),
                       ("bekliyor","—","#f44336"),("gelir","—","#ff9800"),("kalan","—","#c62828")]:
            f = QFrame(); f.setStyleSheet(f"QFrame{{background:{c};border-radius:7px;padding:3px;}}")
            lv = QVBoxLayout(f); lv.setContentsMargins(10,6,10,6)
            vl = QLabel(v); vl.setFont(QFont("Arial",16,QFont.Bold))
            vl.setStyleSheet("color:white;"); vl.setAlignment(Qt.AlignCenter)
            names = {"toplam":"Toplam Kiracı","odendi":"Bu Ay Ödedi",
                     "bekliyor":"Bu Ay Bekliyor","gelir":"Bu Ay Tahsilat",
                     "kalan":"Bu Ay Kalan Tahsilat"}
            tl = QLabel(names[k]); tl.setStyleSheet("color:rgba(255,255,255,.85);font-size:9pt;")
            tl.setAlignment(Qt.AlignCenter)
            lv.addWidget(vl); lv.addWidget(tl); f.vl = vl; self.kpis[k] = f; kr.addWidget(f)
        lay.addLayout(kr)

        # Banner
        bn = QFrame(); bn.setStyleSheet("background:#e3f2fd;border:1px solid #90caf9;border-radius:5px;")
        bl = QHBoxLayout(bn); bl.setContentsMargins(10,5,10,5)
        bl.addWidget(QLabel("<b>Otomatik Eşleşme:</b> İşlemler sekmesinden gelir eklendiginde kiracı adı eşleşirse otomatik ÖDENDİ işaretle r."))
        sb = QPushButton("Simüle Et")
        sb.setStyleSheet("background:#1976d2;color:white;padding:3px 10px;border-radius:4px;font-size:9pt;")
        sb.clicked.connect(self._sim); bl.addWidget(sb)
        lay.addWidget(bn)

        # Tablo
        self.tbl = QTableWidget()
        self.tbl.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tbl.customContextMenuRequested.connect(self._ctx)
        self.tbl.cellDoubleClicked.connect(self._on_dbl_click)
        self.tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl.setAlternatingRowColors(False)
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.horizontalHeader().setDefaultSectionSize(90)
        self.tbl.horizontalHeader().setResizeContentsPrecision(-1)
        hc = self.hdr_color
        self.tbl.setStyleSheet(
            f"QTableWidget{{gridline-color:#ddd;font-size:9pt;}}"
            f"QHeaderView::section{{background:{hc};color:white;font-weight:bold;padding:4px 2px;border:1px solid {hc};}}"
        )
        lay.addWidget(self.tbl)

        # Legend
        lg = QHBoxLayout()
        for col,txt in[(C_ODENDI,"Ödendi"),(C_ODENMEDI,"Ödenmedi"),(C_KISMI,"Not/Kısmi"),(C_DISARI,"Sözleşme Dışı")]:
            bx = QFrame(); bx.setFixedSize(14,14)
            bx.setStyleSheet(f"background:{col.name()};border:1px solid #aaa;border-radius:2px;")
            lg.addWidget(bx)
            ll = QLabel(txt); ll.setStyleSheet("font-size:9pt;margin-right:10px;"); lg.addWidget(ll)
        lg.addStretch()
        lg.addWidget(QLabel("Hücreye sağ tıklayın: Durumu değiştir / Not ekle"))
        lay.addLayout(lg)

    def _load(self):
        cols = ["KİRACI", "BAŞLANGIÇ", "BİTİŞ", "ÖDEME GÜNÜ", "AYLIK TUTAR"] + AYLAR_TR + ["GENEL NOT"]
        self.tbl.setColumnCount(len(cols))
        self.tbl.setHorizontalHeaderLabels(cols)
        self.tbl.setRowCount(len(self.contracts))

        od=0; bk=0; th=0.0; kalan=0.0; cm=date.today().month
        for row,c in enumerate(self.contracts):
            cid=c["id"]; pays=self.payments.get(cid,{})
            ki=QTableWidgetItem(c["kiraci"]); ki.setFont(QFont("Arial",9,QFont.Bold))
            ki.setData(Qt.UserRole, {"cid": cid, "tip": "kiraci_row"})
            self.tbl.setItem(row,0,ki)
            self.tbl.setItem(row,1,QTableWidgetItem(c["bas"]))
            self.tbl.setItem(row,2,QTableWidgetItem(c["bit"]))
            self.tbl.setItem(row,3,QTableWidgetItem(c.get("odeme_gunu","")))
            ti=QTableWidgetItem("TL{:,.0f}".format(c["tutar"]).replace(",",".").replace("TL","₺"))
            ti.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter); self.tbl.setItem(row,4,ti)
            co=2

            bas=datetime.strptime(c["bas"],"%d.%m.%Y").date()
            bit=datetime.strptime(c["bit"],"%d.%m.%Y").date()
            ms=co+3
            for mi in range(12):
                col=ms+mi; ay=mi+1
                mst=date(self.year,ay,1)
                in_c=(bas<=date(self.year,ay,28))and(bit>=mst)
                if not in_c:
                    it=QTableWidgetItem(""); it.setBackground(QBrush(C_DISARI)); it.setFlags(Qt.ItemIsEnabled)
                    self.tbl.setItem(row,col,it); continue
                d=pays.get(ay,"ODENMEDI")
                this_month = (ay==cm and self.year==date.today().year)
                if d=="ODENDI":   txt,bg="ÖDENDİ",C_ODENDI;   od+=1 if this_month else 0; th+=c["tutar"] if this_month else 0
                elif d=="ODENMEDI": txt,bg="ÖDENMEDİ",C_ODENMEDI; bk+=1 if this_month else 0; kalan+=c["tutar"] if this_month else 0
                elif d.startswith("KISMI:"): txt,bg=d[6:],C_KISMI
                else: txt,bg="",C_ODENMEDI
                it=QTableWidgetItem(txt); it.setBackground(QBrush(bg))
                it.setTextAlignment(Qt.AlignCenter|Qt.AlignVCenter)
                it.setData(Qt.UserRole,{"cid":cid,"ay":ay,"durum":d})
                self.tbl.setItem(row,col,it)

            # Yil sonu notu sutunu
            not_col = ms + 12
            not_txt = self.yil_nots.get(cid, "")
            not_it = QTableWidgetItem(not_txt)
            not_it.setBackground(QBrush(QColor("#e8eaf6")))
            not_it.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            not_it.setData(Qt.UserRole, {"cid": cid, "tip": "yil_notu"})
            self.tbl.setItem(row, not_col, not_it)

            bbg=C_ROW_ODD if row%2==0 else C_ROW_EVEN
            for c2 in range(ms):
                it2=self.tbl.item(row,c2)
                if it2: it2.setBackground(QBrush(bbg))
            self.tbl.setRowHeight(row,27)

        # Tum satirlar eklendikten sonra yaziya gore boyutlan
        self.tbl.resizeColumnsToContents()
        # Kiraci sutunu en az 200px olsun
        if self.tbl.columnWidth(0) < 200:
            self.tbl.setColumnWidth(0, 200)

        self.kpis["toplam"].vl.setText(str(len(self.contracts)))
        self.kpis["odendi"].vl.setText(str(od))
        self.kpis["bekliyor"].vl.setText(str(bk))
        self.kpis["gelir"].vl.setText("TL{:,.0f}".format(th).replace(",",".").replace("TL","₺"))
        self.kpis["kalan"].vl.setText("TL{:,.0f}".format(kalan).replace(",",".").replace("TL","₺"))

    def _ctx(self,pos):
        it=self.tbl.itemAt(pos)
        if not it: return
        d=it.data(Qt.UserRole)
        if not d: return
        m=QMenu(self)
        m.setStyleSheet(f"QMenu{{font-size:10pt;}}QMenu::item:selected{{background:{self.hdr_color};color:white;}}")

        # Kiraci satiri sag tik
        if d.get("tip") == "kiraci_row":
            cid=d["cid"]
            cr=next((c for c in self.contracts if c["id"]==cid),None)
            if not cr: return
            m.addAction("📊  Döküm Aç").triggered.connect(lambda: self._dokum(cid))
            m.addSeparator()
            m.addAction("✅  Bu Ay Ödendi İşaretle").triggered.connect(lambda: self._set_odendi(cid, date.today().month))
            m.addSeparator()
            m.addAction("✏️  Kiracı / Sözleşme Düzenle").triggered.connect(lambda: self._edit_contract(cid))
            m.addAction("🗑️  Kiracıyı Listeden Kaldır").triggered.connect(lambda: self._del_contract(cid))
            m.exec_(self.tbl.viewport().mapToGlobal(pos))
            return

        # Yil sonu notu hucresi mi?
        if d.get("tip") == "yil_notu":
            cid=d["cid"]
            cr=next((c for c in self.contracts if c["id"]==cid),None)
            if not cr: return
            mv=self.yil_nots.get(cid,"")
            m.addAction("📝  Genel Not Ekle / Düzenle").triggered.connect(lambda:self._yil_not(cid,cr["kiraci"],mv))
            if mv:
                m.addAction("🗑️  Notu Sil").triggered.connect(lambda:self._yil_not_sil(cid))
            m.exec_(self.tbl.viewport().mapToGlobal(pos))
            return

        # Normal ay hucresi
        cid=d["cid"]; ay=d["ay"]; dur=d["durum"]
        cr=next((c for c in self.contracts if c["id"]==cid),None)
        if not cr: return
        if dur!="ODENDI": m.addAction("Ödendi Olarak İşaretle").triggered.connect(lambda:self._set_odendi(cid,ay))
        if dur!="ODENMEDI": m.addAction("Ödenmedi Olarak İşaretle").triggered.connect(lambda:self._set(cid,ay,"ODENMEDI"))
        m.addSeparator()
        mv=dur[6:] if dur.startswith("KISMI:") else ""
        m.addAction("📝  Not Ekle / Düzenle").triggered.connect(lambda:self._note(cid,ay,cr["kiraci"],mv))
        m.exec_(self.tbl.viewport().mapToGlobal(pos))

    def _set(self,cid,ay,d): self.payments.setdefault(cid,{})[ay]=d; self._load()

    def _set_odendi(self, cid, ay):
        """Ödendi işaretle + opsiyonel tarih/banka detayı gir."""
        cr = next((c for c in self.contracts if c["id"]==cid), None)
        if not cr: return
        dlg = OdemeDetayDialog(cr["kiraci"], AYLAR_TR[ay-1], self)
        if dlg.exec_() == QDialog.Accepted:
            det = dlg.get_data()
            self.odeme_detay.setdefault(cid, {})[ay] = det
        self.payments.setdefault(cid, {})[ay] = "ODENDI"; self._load()

    def _dokum(self, cid):
        """Kiracının tam ödeme dökümünü aç."""
        try:
            cr = next((c for c in self.contracts if c["id"]==cid), None)
            if not cr: return
            dlg = KiraciDokumDialog(
                cr["kiraci"], cr,
                self.payments.get(cid, {}),
                self.odeme_detay.get(cid, {}),
                self.year, self.hdr_color, self
            )
            dlg.exec_()
        except Exception as e:
            import traceback
            QMessageBox.critical(self, "Hata", f"{type(e).__name__}: {e}\n\n{traceback.format_exc()}")

    def _on_dbl_click(self, row, col):
        """Kiracı adına çift tıklayınca döküm aç."""
        if col == 0:
            it = self.tbl.item(row, 0)
            if it:
                d = it.data(Qt.UserRole)
                if d and d.get("tip") == "kiraci_row":
                    self._dokum(d["cid"])

    def _yil_not(self,cid,kiraci,mevcut):
        dlg=PaymentNoteDialog(kiraci,"Genel Not",mevcut,self)
        if dlg.exec_()==QDialog.Accepted:
            n=dlg.get_note()
            if n: self.yil_nots[cid]=n
            elif cid in self.yil_nots: del self.yil_nots[cid]
            self._load()

    def _yil_not_sil(self,cid):
        if cid in self.yil_nots: del self.yil_nots[cid]
        self._load()

    def _note(self,cid,ay,kr,mv):
        dlg=PaymentNoteDialog(kr,AYLAR_TR[ay-1],mv,self)
        if dlg.exec_()==QDialog.Accepted:
            n=dlg.get_note()
            self.payments.setdefault(cid,{})[ay]=f"KISMI:{n}" if n else "ODENMEDI"; self._load()

    def _year_chg(self,t): self.year=int(t); self._load()

    def _add(self):
        dlg=ContractDialog(has_odeme_gunu=self.has_og, parent=self)
        if dlg.exec_()==QDialog.Accepted:
            data = dlg.get_data()
            if not data["kiraci"]:
                return
            new_id = max((c["id"] for c in self.contracts), default=0) + 1
            data["id"] = new_id
            self.contracts.append(data)
            self._load()

    def _edit_contract(self, cid):
        cr = next((c for c in self.contracts if c["id"]==cid), None)
        if not cr: return
        dlg = ContractDialog(has_odeme_gunu=self.has_og, contract=cr, parent=self)
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            if not data["kiraci"]: return
            # Guncelle
            cr.update(data)
            self._load()

    def _del_contract(self, cid):
        cr = next((c for c in self.contracts if c["id"]==cid), None)
        if not cr: return
        ret = QMessageBox.question(
            self, "Kiracı Kaldır",
            f"<b>{cr['kiraci']}</b> listeden kaldırılsın mı?\n"
            "Tüm ödeme kayıtları da silinir.",
            QMessageBox.Yes | QMessageBox.No
        )
        if ret == QMessageBox.Yes:
            self.contracts = [c for c in self.contracts if c["id"] != cid]
            self.payments.pop(cid, None)
            self.yil_nots.pop(cid, None)
            self._load()

    def _sim(self):
        import random
        # Mart ayında ödenmemiş ilk kiracıyı bul
        tgt = None
        for c in self.contracts:
            if self.payments.get(c["id"],{}).get(3) != "ODENDI": tgt = c; break
        if not tgt:
            QMessageBox.information(self,"Simülasyon","Tüm Mart ödemeleri işaretli."); return

        beklenen = tgt["tutar"]
        # Demo: %70 ihtimalle tam ödeme, %30 ihtimalle 2000-8000 TL eksik
        if random.random() < 0.70:
            gelen = beklenen
        else:
            gelen = beklenen - random.choice([2000, 3000, 5000, 8000])

        fark = beklenen - gelen

        if fark <= 0:
            # Tam ödeme
            durum_yaz = "ODENDI"
            sonuc_txt = "✅ Tutar tam — ÖDENDİ olarak işaretlendi."
            renk_emoji = "✅"
        else:
            # Eksik ödeme
            kalan_fmt = "{:,.0f}".format(fark).replace(",",".")
            durum_yaz = f"KISMI:{kalan_fmt} TL KALDI"
            sonuc_txt = (f"⚠️ Eksik ödeme! Beklenen: ₺{beklenen:,.0f}  →  "
                         f"Gelen: ₺{gelen:,.0f}  →  Fark: ₺{fark:,.0f}\n"
                         f"Hücreye «{kalan_fmt} TL KALDI» yazıldı.").replace(",",".")
            renk_emoji = "⚠️"

        gelen_fmt  = "{:,.0f}".format(gelen).replace(",",".")
        beklen_fmt = "{:,.0f}".format(beklenen).replace(",",".")

        QMessageBox.information(self,"Otomatik Eşleşme",
            f"Banka işlemleri sekmesinden yeni gelir tespit edildi:\n\n"
            f"  Müşteri      : {tgt['kiraci']}\n"
            f"  Gelen Tutar  : ₺{gelen_fmt}\n"
            f"  Beklenen     : ₺{beklen_fmt}\n"
            f"  Ay           : MART  |  Tarih: {date.today().strftime('%d.%m.%Y')}\n\n"
            f"{sonuc_txt}")

        self.payments.setdefault(tgt["id"],{})[3] = durum_yaz
        self._load()


TAB_COLORS = [
    "#c2185b","#7b1fa2","#1565c0","#2e7d32",
    "#e65100","#00695c","#4527a0","#ad1457",
    "#0277bd","#558b2f","#6a1520","#1a237e",
]


class TabNameDialog(QDialog):
    """Sekme adı ve başlık düzenleme dialogu."""
    def __init__(self, tab_name="", title="", color="#1565c0", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sekme Ayarları")
        self.setMinimumWidth(420)
        lay = QFormLayout(self); lay.setContentsMargins(20,20,20,20); lay.setVerticalSpacing(10)

        self.tab_edit = QLineEdit(tab_name)
        self.tab_edit.setPlaceholderText("Sekme çubuğundaki kısa ad (örn: İZMİR KİRA)")
        lay.addRow("Sekme Adı:", self.tab_edit)

        self.title_edit = QLineEdit(title)
        self.title_edit.setPlaceholderText("Sayfanın üst başlığı (örn: 2026 YILI İZMİR KİRALARI)")
        lay.addRow("Sayfa Başlığı:", self.title_edit)

        # Renk seçici
        self._color = color
        self.color_btn = QPushButton()
        self.color_btn.setFixedHeight(30)
        self._set_color_btn(color)
        self.color_btn.clicked.connect(self._pick_color)
        lay.addRow("Renk:", self.color_btn)

        btns = QHBoxLayout()
        ci = QPushButton("İptal"); ci.clicked.connect(self.reject)
        ci.setStyleSheet("background:#9e9e9e;color:white;padding:6px 18px;border-radius:4px;")
        si = QPushButton("Kaydet"); si.clicked.connect(self._save)
        si.setStyleSheet("background:#4caf50;color:white;padding:6px 18px;border-radius:4px;")
        btns.addStretch(); btns.addWidget(ci); btns.addWidget(si)
        lay.addRow(btns)

    def _set_color_btn(self, color):
        self._color = color
        self.color_btn.setText(color)
        self.color_btn.setStyleSheet(
            f"background:{color};color:white;font-weight:bold;border-radius:4px;"
        )

    def _pick_color(self):
        c = QColorDialog.getColor(QColor(self._color), self, "Renk Seç")
        if c.isValid():
            self._set_color_btn(c.name())

    def _save(self):
        if not self.tab_edit.text().strip():
            QMessageBox.warning(self, "Uyarı", "Sekme adı boş olamaz.")
            return
        self.accept()

    def get_data(self):
        return {
            "tab_name": self.tab_edit.text().strip().upper(),
            "title":    self.title_edit.text().strip() or self.tab_edit.text().strip().upper(),
            "color":    self._color,
        }


class PreviewWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OZKAYA Muhasebe - Kira Takip (ONIZLEME)")
        self.setGeometry(60,40,1400,780)
        self.setStyleSheet("QMainWindow{background:#f5f5f5;}")

        banner=QLabel("  ÖNİZLEME MODU - Projeye hiçbir şey eklenmedi. Beğendiyseniz 'projeye ekle' deyin.")
        banner.setStyleSheet("background:#ff9800;color:white;font-weight:bold;font-size:10pt;padding:6px 14px;")
        banner.setAlignment(Qt.AlignCenter)

        # ── Sekme toolbar ──────────────────────────────────────────────────────
        tb = QHBoxLayout(); tb.setContentsMargins(6,4,6,4); tb.setSpacing(6)
        tb.addStretch()
        add_btn = QPushButton("＋ Yeni Sekme Ekle")
        add_btn.setStyleSheet(
            "background:#43a047;color:white;font-weight:bold;padding:4px 14px;"
            "border-radius:5px;font-size:9pt;"
        )
        add_btn.clicked.connect(self._add_tab)
        self._rename_btn = QPushButton("✏️ Sekmeyi Düzenle")
        self._rename_btn.setStyleSheet(
            "background:#1976d2;color:white;padding:4px 12px;"
            "border-radius:5px;font-size:9pt;"
        )
        self._rename_btn.clicked.connect(self._rename_tab)
        self._del_btn = QPushButton("🗑️ Sekmeyi Sil")
        self._del_btn.setStyleSheet(
            "background:#e53935;color:white;padding:4px 12px;"
            "border-radius:5px;font-size:9pt;"
        )
        self._del_btn.clicked.connect(self._delete_tab)
        tb.addWidget(self._rename_btn)
        tb.addWidget(self._del_btn)
        tb.addWidget(add_btn)
        tb_frame = QWidget(); tb_frame.setLayout(tb)
        tb_frame.setStyleSheet("background:#eceff1;border-bottom:1px solid #cfd8dc;")

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(
            "QTabBar::tab{padding:8px 16px;font-size:10pt;font-weight:bold;min-width:120px;}"
            "QTabBar::tab:selected{background:white;}"
        )
        # Sağ tık ile hızlı menü
        self.tabs.tabBar().setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabs.tabBar().customContextMenuRequested.connect(self._tab_ctx_menu)

        # Başlangıç sekmeleri
        self.tabs.addTab(TahsilatWidget("2026 YILI TORBALI KİRA TAHİSILATLARI","#c2185b",TK_CONTRACTS,TK_PAYMENTS,odeme_detay=TK_ODEME_DETAY),"TORBALI KİRA")
        self.tabs.addTab(TahsilatWidget("2026 YILI GELEN AİDATLAR","#7b1fa2",TA_CONTRACTS,TA_PAYMENTS,odeme_detay=TA_ODEME_DETAY),"TORBALI AİDAT")
        self.tabs.addTab(TahsilatWidget("2026 YILI DÜKKAN / İŞYERİ KİRALARI","#1565c0",DK_CONTRACTS,DK_PAYMENTS,odeme_detay=DK_ODEME_DETAY),"DÜKKANLAR")
        self.tabs.addTab(TahsilatWidget("2026 YILI GAZİANTEP KİRALARI","#2e7d32",GZ_CONTRACTS,GZ_PAYMENTS,odeme_detay=GZ_ODEME_DETAY),"GAZİANTEP")

        cw = QWidget(); lv = QVBoxLayout(cw)
        lv.setContentsMargins(0,0,0,0); lv.setSpacing(0)
        lv.addWidget(banner)
        lv.addWidget(tb_frame)
        lv.addWidget(self.tabs)
        self.setCentralWidget(cw)

    # ── Sekme işlemleri ────────────────────────────────────────────────────────
    def _next_color(self):
        used = set()
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if hasattr(w, "hdr_color"): used.add(w.hdr_color)
        for c in TAB_COLORS:
            if c not in used: return c
        return TAB_COLORS[self.tabs.count() % len(TAB_COLORS)]

    def _add_tab(self):
        color = self._next_color()
        dlg = TabNameDialog("", "", color, self)
        if dlg.exec_() != QDialog.Accepted: return
        d = dlg.get_data()
        widget = TahsilatWidget(d["title"], d["color"], [], {})
        self.tabs.addTab(widget, d["tab_name"])
        self.tabs.setCurrentIndex(self.tabs.count()-1)

    def _rename_tab(self):
        idx = self.tabs.currentIndex()
        if idx < 0: return
        w = self.tabs.widget(idx)
        dlg = TabNameDialog(
            self.tabs.tabText(idx),
            getattr(w, "title", ""),
            getattr(w, "hdr_color", "#1565c0"),
            self
        )
        if dlg.exec_() != QDialog.Accepted: return
        d = dlg.get_data()
        self.tabs.setTabText(idx, d["tab_name"])
        w.title = d["title"]
        w.hdr_color = d["color"]
        # Başlık ve renk etiketi güncelle
        for lbl in w.findChildren(QLabel):
            if hasattr(lbl, "font") and lbl.font().bold() and lbl.text() == getattr(w, "_old_title", None):
                break
        # _load ile tabloyu yenile (renk/başlık günceli için)
        w._load()

    def _delete_tab(self):
        idx = self.tabs.currentIndex()
        if idx < 0: return
        tab_name = self.tabs.tabText(idx)
        ret = QMessageBox.question(
            self, "Sekmeyi Sil",
            f"<b>{tab_name}</b> sekmesi silinsin mi?\n"
            "İçindeki tüm kiracı ve ödeme kayıtları kaybolur.",
            QMessageBox.Yes | QMessageBox.No
        )
        if ret == QMessageBox.Yes:
            self.tabs.removeTab(idx)

    def _tab_ctx_menu(self, pos):
        idx = self.tabs.tabBar().tabAt(pos)
        if idx < 0: return
        self.tabs.setCurrentIndex(idx)
        m = QMenu(self)
        m.setStyleSheet("QMenu{font-size:10pt;}QMenu::item:selected{background:#1976d2;color:white;}")
        m.addAction("✏️  Sekmeyi Düzenle / Yeniden Adlandır").triggered.connect(self._rename_tab)
        m.addSeparator()
        m.addAction("🗑️  Sekmeyi Sil").triggered.connect(self._delete_tab)
        m.exec_(self.tabs.tabBar().mapToGlobal(pos))


def main():
    app=QApplication(sys.argv); app.setStyle("Fusion")
    w=PreviewWindow(); w.show(); sys.exit(app.exec_())

if __name__=="__main__":
    main()