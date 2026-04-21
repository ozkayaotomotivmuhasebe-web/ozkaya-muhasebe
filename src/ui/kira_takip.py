"""
Kira Takip Modülü — Ana uygulama içi widget.
Veri: data/kira_takip_data.json (per-user: data/kira_takip_data_{user_id}.json)
"""
import json, re as _re
from pathlib import Path
from datetime import date, datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTabBar,
    QTableWidget, QTableWidgetItem, QLabel, QPushButton, QComboBox,
    QFrame, QDialog, QFormLayout, QLineEdit, QDateEdit,
    QDoubleSpinBox, QTextEdit, QMenu, QMessageBox, QColorDialog,
    QAbstractItemView,
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QBrush

# ── Sabitler ────────────────────────────────────────────────────────────────
AYLAR_TR = ["OCAK","ŞUBAT","MART","NİSAN","MAYIS","HAZİRAN",
            "TEMMUZ","AĞUSTOS","EYLÜL","EKİM","KASIM","ARALIK"]

C_ODENDI   = QColor("#c8f7c5")
C_ODENMEDI = QColor("#ffd6d6")
C_KISMI    = QColor("#fff3cd")
C_DISARI   = QColor("#ebebeb")
C_ROW_ODD  = QColor("#fff8fc")
C_ROW_EVEN = QColor("#ffffff")

TAB_COLORS = [
    "#c2185b","#7b1fa2","#1565c0","#2e7d32",
    "#e65100","#00695c","#4527a0","#ad1457",
    "#0277bd","#558b2f","#6a1520","#1a237e",
]

DATA_DIR = Path("data")

# ── Yeniden Boyutlandırılabilir Sekme Çubuğu ────────────────────────────────
class ResizableTabBar(QTabBar):
    """Sağ kenardan sürükleyerek yeniden boyutlandırılabilir sekme çubuğu."""
    widthsChanged = pyqtSignal()
    EDGE = 7  # px — sağ kenar algılama eşiği

    def __init__(self, parent=None):
        super().__init__(parent)
        self._custom_widths: dict = {}  # {index: width_px}
        self._drag_idx = -1
        self._drag_start_x = 0
        self._drag_start_w = 0
        self.setMouseTracking(True)

    def tabSizeHint(self, index):
        hint = super().tabSizeHint(index)
        if index in self._custom_widths:
            hint.setWidth(self._custom_widths[index])
        return hint

    def minimumTabSizeHint(self, index):
        hint = super().minimumTabSizeHint(index)
        if index in self._custom_widths:
            hint.setWidth(min(self._custom_widths[index], hint.width()))
        return hint

    def _edge_tab(self, pos):
        for i in range(self.count()):
            r = self.tabRect(i)
            if abs(pos.x() - r.right()) <= self.EDGE and r.top() <= pos.y() <= r.bottom():
                return i
        return -1

    def mousePressEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            idx = self._edge_tab(ev.pos())
            if idx >= 0:
                self._drag_idx = idx
                self._drag_start_x = ev.globalX()
                self._drag_start_w = self.tabRect(idx).width()
                ev.accept()
                return
        super().mousePressEvent(ev)

    def mouseMoveEvent(self, ev):
        if self._drag_idx >= 0:
            delta = ev.globalX() - self._drag_start_x
            new_w = max(60, self._drag_start_w + delta)
            self._custom_widths[self._drag_idx] = new_w
            # setIconSize, Qt'nin iç layoutTabs()'ını zorla tetikler
            self.setIconSize(self.iconSize())
            ev.accept()
            return
        edge = self._edge_tab(ev.pos())
        self.setCursor(Qt.SizeHorCursor if edge >= 0 else Qt.ArrowCursor)
        super().mouseMoveEvent(ev)

    def mouseReleaseEvent(self, ev):
        if self._drag_idx >= 0 and ev.button() == Qt.LeftButton:
            self._drag_idx = -1
            self.widthsChanged.emit()
            ev.accept()
            return
        super().mouseReleaseEvent(ev)

    def get_widths_by_name(self) -> dict:
        """Sekme adı → genişlik sözlüğü döner (JSON kaydetmek için)."""
        return {self.tabText(i): w for i, w in self._custom_widths.items()}

    def apply_widths_by_name(self, name_widths: dict):
        """Sekme adı → genişlik sözlüğünden genişlikleri uygular."""
        self._custom_widths.clear()
        for i in range(self.count()):
            name = self.tabText(i)
            if name in name_widths:
                self._custom_widths[i] = int(name_widths[name])
        self.updateGeometry()
        self.update()


# ── Yardımcı Dialoglar ───────────────────────────────────────────────────────

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
        h.addStretch(); h.addWidget(c); h.addWidget(s); lay.addLayout(h)

    def get_note(self): return self.note.toPlainText().strip()


class OdemeDetayDialog(QDialog):
    def __init__(self, kiraci, ay_adi, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Ödeme Detayı — {ay_adi}")
        self.setMinimumWidth(370)
        lay = QFormLayout(self); lay.setContentsMargins(18,18,18,18); lay.setVerticalSpacing(10)
        self.tarih = QDateEdit(); self.tarih.setCalendarPopup(True)
        self.tarih.setDisplayFormat("dd.MM.yyyy"); self.tarih.setDate(QDate.currentDate())
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
        btns.addStretch(); btns.addWidget(atla); btns.addWidget(kaydet); lay.addRow(btns)

    def get_data(self):
        return {"tarih": self.tarih.date().toString("dd.MM.yyyy"),
                "banka": self.banka.text().strip(),
                "aciklama": self.aciklama.text().strip()}


class KiraciDokumDialog(QDialog):
    def __init__(self, kiraci, contract, payments, odeme_detay, year, hdr_color, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Kiracı Dökümü — {kiraci}")
        self.setMinimumWidth(920); self.setMinimumHeight(560)
        lay = QVBoxLayout(self); lay.setContentsMargins(16,16,16,16); lay.setSpacing(8)

        bas_dt = datetime.strptime(contract["bas"], "%d.%m.%Y").date()
        tutar  = contract.get("tutar", 0)
        og_txt = contract.get("odeme_gunu", "")
        pay_day = None
        if og_txt:
            nums = _re.findall(r'\d+', og_txt)
            if nums: pay_day = int(nums[0])
        if pay_day is not None:
            pay_day = max(1, min(pay_day, 28))
        today = date.today()

        hl = QHBoxLayout()
        tl = QLabel(f"<b style='font-size:13pt'>{kiraci}</b>")
        tl.setStyleSheet(f"color:{hdr_color};")
        hl.addWidget(tl); hl.addStretch()
        og_goster = og_txt if og_txt else "—"
        info = QLabel(
            f"Sözleşme: {contract.get('bas','?')} – {contract.get('bit','?')}"
            f"&nbsp;&nbsp;|&nbsp;&nbsp;Ödeme Günü: <b>{og_goster}</b>"
            f"&nbsp;&nbsp;|&nbsp;&nbsp;Aylık: <b>₺{tutar:,.0f}</b>".replace(",",".")
        )
        info.setStyleSheet("color:#444;font-size:10pt;"); hl.addWidget(info)
        lay.addLayout(hl)

        tbl = QTableWidget(); tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        tbl.verticalHeader().setVisible(False); tbl.setSelectionBehavior(QTableWidget.SelectRows)
        tbl.setStyleSheet(
            f"QTableWidget{{gridline-color:#ddd;font-size:10pt;background:white;}}"
            f"QHeaderView::section{{background:{hdr_color};color:white;font-weight:bold;padding:5px;border:none;}}"
        )
        tbl.setColumnCount(7)
        tbl.setHorizontalHeaderLabels(
            ["AY","BEKLENEN TARİH","DURUM","ÖDEME TARİHİ","BANKA / ÖDEME YERİ","TUTAR","AÇIKLAMA"]
        )

        rows = []
        for ay in range(1, 13):
            mst = date(year, ay, 1)
            in_c = (bas_dt <= date(year, ay, 28)) and \
                   (datetime.strptime(contract["bit"], "%d.%m.%Y").date() >= mst)
            if not in_c: continue
            rows.append((ay, payments.get(ay, "ODENMEDI"), odeme_detay.get(ay, {})))

        C_GECIKME = QColor("#ff5252")
        tbl.setRowCount(len(rows))
        toplam_odenen = 0.0; toplam_bekleyen = 0.0; gecikme_sayisi = 0

        for row, (ay, durum, detay) in enumerate(rows):
            ay_adi = AYLAR_TR[ay - 1]
            if pay_day is not None:
                try:
                    beklenen_dt = date(year, ay, pay_day)
                except ValueError:
                    import calendar
                    beklenen_dt = date(year, ay, min(pay_day, calendar.monthrange(year, ay)[1]))
                beklenen_txt = beklenen_dt.strftime("%d.%m.%Y")
                gecikti = (durum == "ODENMEDI") and (beklenen_dt < today)
            else:
                beklenen_dt = None; beklenen_txt = "—"; gecikti = False

            if durum == "ODENDI":
                durum_txt = "✅ Ödendi"; bg = C_ODENDI
                tarih = detay.get("tarih","—") or "—"; banka = detay.get("banka","—") or "—"
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
                tarih = detay.get("tarih","—") or "—"; banka = detay.get("banka","—") or "—"
                aciklama = durum[6:]; tutar_txt = "₺{:,.0f}".format(tutar).replace(",",".")
            else:
                durum_txt = "—"; bg = C_DISARI; tarih = banka = "—"; aciklama = ""; tutar_txt = "—"

            for col, txt in enumerate([ay_adi, beklenen_txt, durum_txt, tarih, banka, tutar_txt, aciklama]):
                it = QTableWidgetItem(txt); it.setBackground(QBrush(bg))
                it.setTextAlignment((Qt.AlignRight if col == 5 else Qt.AlignCenter) | Qt.AlignVCenter)
                if gecikti:
                    it.setForeground(QBrush(QColor("white")))
                    f = QFont(); f.setBold(True); it.setFont(f)
                tbl.setItem(row, col, it)
            tbl.setRowHeight(row, 30)

        tbl.resizeColumnsToContents()
        tbl.setColumnWidth(4, max(tbl.columnWidth(4), 165))
        tbl.setColumnWidth(6, max(tbl.columnWidth(6), 160))

        if gecikme_sayisi > 0:
            warn = QLabel(f"  ⚠️  Bu kiracının {gecikme_sayisi} ay ödemesi gecikmiş! "
                          f"Toplam: ₺{toplam_bekleyen:,.0f}".replace(",","."))
            warn.setStyleSheet("background:#d32f2f;color:white;font-weight:bold;font-size:11pt;"
                               "padding:8px 14px;border-radius:5px;")
            warn.setAlignment(Qt.AlignCenter)
            lay.addWidget(warn)

        lay.addWidget(tbl)

        ozet_style = "font-size:11pt;padding:8px 14px;border-radius:5px;"
        ozet_style += "background:#fff3e0;" if gecikme_sayisi > 0 else "background:#e8f5e9;"
        ozet = QLabel(
            f"<b>Toplam Ödenen:</b> ₺{toplam_odenen:,.0f}"
            f"&nbsp;&nbsp;|&nbsp;&nbsp;<b>Bekleyen/Gecikmiş:</b> ₺{toplam_bekleyen:,.0f}".replace(",",".")
        )
        ozet.setStyleSheet(ozet_style); lay.addWidget(ozet)

        close_btn = QPushButton("Kapat")
        close_btn.setStyleSheet("background:#607d8b;color:white;padding:7px 22px;border-radius:5px;font-size:10pt;")
        close_btn.clicked.connect(self.accept)
        hb = QHBoxLayout(); hb.addStretch(); hb.addWidget(close_btn); lay.addLayout(hb)


class ContractDialog(QDialog):
    def __init__(self, contract=None, parent=None):
        super().__init__(parent)
        edit_mode = contract is not None
        self.setWindowTitle("Kiracı Düzenle" if edit_mode else "Yeni Kiracı Ekle")
        self.setMinimumWidth(440)
        lay = QFormLayout(self); lay.setVerticalSpacing(10); lay.setContentsMargins(20,20,20,20)
        self.kiraci_edit = QLineEdit(); self.kiraci_edit.setPlaceholderText("Kiracı tam adı")
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
        self.konu_edit = QLineEdit()
        self.konu_edit.setPlaceholderText("örn: kira  |  aidat  |  depo (zorunlu)")
        if edit_mode: self.konu_edit.setText(contract.get("aciklama_kw", "kira"))
        else: self.konu_edit.setText("kira")
        lay.addRow("İşlem Konusu:", self.konu_edit)
        btn = QHBoxLayout()
        ci = QPushButton("İptal"); ci.clicked.connect(self.reject)
        si = QPushButton("Kaydet"); si.clicked.connect(self.accept)
        si.setStyleSheet("background:#4caf50;color:white;padding:6px 18px;border-radius:4px;")
        ci.setStyleSheet("background:#9e9e9e;color:white;padding:6px 18px;border-radius:4px;")
        btn.addStretch(); btn.addWidget(ci); btn.addWidget(si); lay.addRow(btn)

    def get_data(self):
        return {
            "kiraci":      self.kiraci_edit.text().strip(),
            "bas":         self.bas.date().toString("dd.MM.yyyy"),
            "bit":         self.bit.date().toString("dd.MM.yyyy"),
            "tutar":       float(self.tutar_edit.value()),
            "odeme_gunu":  self.odeme_edit.text().strip(),
            "aciklama_kw": self.konu_edit.text().strip().lower() or "kira",
        }


class TabNameDialog(QDialog):
    def __init__(self, tab_name="", title="", color="#1565c0", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sekme Ayarları"); self.setMinimumWidth(420)
        lay = QFormLayout(self); lay.setContentsMargins(20,20,20,20); lay.setVerticalSpacing(10)
        self.tab_edit = QLineEdit(tab_name)
        self.tab_edit.setPlaceholderText("Sekme çubuğundaki kısa ad (örn: İZMİR KİRA)")
        lay.addRow("Sekme Adı:", self.tab_edit)
        self.title_edit = QLineEdit(title)
        self.title_edit.setPlaceholderText("Sayfanın üst başlığı")
        lay.addRow("Sayfa Başlığı:", self.title_edit)
        self._color = color
        self.color_btn = QPushButton(); self.color_btn.setFixedHeight(30)
        self._set_color_btn(color); self.color_btn.clicked.connect(self._pick_color)
        lay.addRow("Renk:", self.color_btn)
        btns = QHBoxLayout()
        ci = QPushButton("İptal"); ci.clicked.connect(self.reject)
        ci.setStyleSheet("background:#9e9e9e;color:white;padding:6px 18px;border-radius:4px;")
        si = QPushButton("Kaydet"); si.clicked.connect(self._save)
        si.setStyleSheet("background:#4caf50;color:white;padding:6px 18px;border-radius:4px;")
        btns.addStretch(); btns.addWidget(ci); btns.addWidget(si); lay.addRow(btns)

    def _set_color_btn(self, color):
        self._color = color; self.color_btn.setText(color)
        self.color_btn.setStyleSheet(
            f"background:{color};color:white;font-weight:bold;border-radius:4px;"
        )

    def _pick_color(self):
        c = QColorDialog.getColor(QColor(self._color), self, "Renk Seç")
        if c.isValid(): self._set_color_btn(c.name())

    def _save(self):
        if not self.tab_edit.text().strip():
            QMessageBox.warning(self, "Uyarı", "Sekme adı boş olamaz."); return
        self.accept()

    def get_data(self):
        return {
            "tab_name": self.tab_edit.text().strip(),
            "title":    self.title_edit.text().strip() or self.tab_edit.text().strip(),
            "color":    self._color,
        }


# ── Ana Tahsilat Widget ──────────────────────────────────────────────────────

class TahsilatWidget(QWidget):
    def __init__(self, title, hdr_color, contracts, payments,
                 year=None, odeme_detay=None, yil_nots=None, on_change=None, create_tx_cb=None,
                 user_id=0, tab_name=""):
        super().__init__()
        self.title       = title
        self.hdr_color   = hdr_color
        self.year        = year or date.today().year
        self.contracts   = list(contracts)
        self.payments    = {int(k): {int(m): v for m, v in mv.items()}
                            for k, mv in payments.items()} if payments else {}
        self.odeme_detay = {int(k): {int(m): v for m, v in mv.items()}
                            for k, mv in (odeme_detay or {}).items()}
        self.yil_nots    = {int(k): v for k, v in (yil_nots or {}).items()}
        self.on_change   = on_change   # callback → parent saves JSON
        self.create_tx_cb = create_tx_cb  # callback → DB işlem kaydı oluştur
        self.user_id     = user_id
        self._tab_name   = tab_name
        self._build(); self._load()

    def _notify(self):
        if self.on_change: self.on_change()

    def to_dict(self):
        """Mevcut durumu JSON-serileştirilebilir dict'e çevirir."""
        return {
            "title":      self.title,
            "hdr_color":  self.hdr_color,
            "year":       self.year,
            "contracts":  self.contracts,
            "payments":   {str(k): {str(m): v for m, v in mv.items()}
                           for k, mv in self.payments.items()},
            "odeme_detay":{str(k): {str(m): v for m, v in mv.items()}
                           for k, mv in self.odeme_detay.items()},
            "yil_nots":   {str(k): v for k, v in self.yil_nots.items()},
        }

    def _build(self):
        lay = QVBoxLayout(self); lay.setContentsMargins(8,8,8,8); lay.setSpacing(6)

        _title_fs   = 13
        _kpi_val_fs = 16
        _kpi_lbl_fs = 10
        _btn_fs     = 10

        # Üst bar
        top = QHBoxLayout()
        lbl = QLabel(self.title); lbl.setFont(QFont("Arial", _title_fs, QFont.Bold))
        lbl.setStyleSheet(f"color:{self.hdr_color};padding:2px;"); top.addWidget(lbl)
        top.addStretch()
        top.addWidget(QLabel("Yıl:"))
        self.yc = QComboBox()
        for y in range(2023, date.today().year + 3): self.yc.addItem(str(y))
        self.yc.setCurrentText(str(self.year)); self.yc.setFixedWidth(75)
        self.yc.currentTextChanged.connect(lambda t: self._year_chg(t))
        top.addWidget(self.yc)
        ab = QPushButton("+ Kiracı Ekle")
        ab.setStyleSheet(f"background:{self.hdr_color};color:white;font-weight:bold;"
                         f"padding:5px 12px;border-radius:5px;font-size:{_btn_fs}pt;")
        ab.clicked.connect(self._add); top.addWidget(ab)
        lay.addLayout(top)

        # KPI paneli
        kr = QHBoxLayout(); self.kpis = {}
        for k, v, c in [("toplam","—","#3f51b5"),("odendi","—","#4caf50"),
                         ("bekliyor","—","#f44336"),("gelir","—","#ff9800"),
                         ("kalan","—","#c62828")]:
            f = QFrame(); f.setStyleSheet(f"QFrame{{background:{c};border-radius:7px;padding:3px;}}")
            lv = QVBoxLayout(f); lv.setContentsMargins(10,6,10,6)
            vl = QLabel(v); vl.setFont(QFont("Arial", _kpi_val_fs, QFont.Bold))
            vl.setStyleSheet("color:white;"); vl.setAlignment(Qt.AlignCenter)
            nm = {"toplam":"Toplam Kiracı","odendi":"Bu Ay Ödedi","bekliyor":"Bu Ay Bekliyor",
                  "gelir":"Bu Ay Tahsilat","kalan":"Bu Ay Kalan Tahsilat"}
            tl = QLabel(nm[k]); tl.setStyleSheet(f"color:rgba(255,255,255,.85);font-size:{_kpi_lbl_fs}pt;")
            tl.setAlignment(Qt.AlignCenter)
            lv.addWidget(vl); lv.addWidget(tl); f.vl = vl; self.kpis[k] = f; kr.addWidget(f)
        lay.addLayout(kr)

        # Tablo
        self.tbl = QTableWidget()
        self.tbl.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tbl.customContextMenuRequested.connect(self._ctx)
        self.tbl.cellDoubleClicked.connect(self._on_dbl_click)
        self.tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl.setAlternatingRowColors(False)
        self.tbl.verticalHeader().setVisible(False)
        from PyQt5.QtWidgets import QHeaderView
        hdr = self.tbl.horizontalHeader()
        hdr.setDefaultSectionSize(100)
        hdr.setMinimumSectionSize(70)
        hdr.setDefaultAlignment(Qt.AlignCenter)
        hdr.setMinimumHeight(36)
        hdr.setSectionResizeMode(QHeaderView.Interactive)
        hdr.setFont(QFont("Arial", 10, QFont.Bold))
        self.tbl.setSizeAdjustPolicy(QAbstractItemView.AdjustToContents)
        self.tbl.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        hc = self.hdr_color
        self.tbl.setStyleSheet(
            f"QTableWidget{{gridline-color:#ddd;font-size:10pt;}}"
            f"QHeaderView::section{{background:{hc};color:white;font-weight:bold;"
            f"font-size:10pt;padding:4px 6px;border:1px solid {hc};"
            f"min-height:36px;}}"
        )
        lay.addWidget(self.tbl)

        # Renk açıklaması
        lg = QHBoxLayout()
        for col, txt in [(C_ODENDI,"Ödendi"),(C_ODENMEDI,"Ödenmedi"),
                         (C_KISMI,"Not/Kısmi"),(C_DISARI,"Sözleşme Dışı")]:
            bx = QFrame(); bx.setFixedSize(14,14)
            bx.setStyleSheet(f"background:{col.name()};border:1px solid #aaa;border-radius:2px;")
            lg.addWidget(bx)
            ll = QLabel(txt); ll.setStyleSheet("font-size:9pt;margin-right:10px;"); lg.addWidget(ll)
        lg.addStretch()
        lg.addWidget(QLabel("Hücreye sağ tıklayın: Durumu değiştir / Not ekle"))
        lay.addLayout(lg)

    def _load(self):
        cols = ["KİRACI","BAŞLANGIÇ","BİTİŞ","ÖDEME GÜNÜ","AYLIK TUTAR"] + AYLAR_TR + ["GENEL NOT"]
        self.tbl.setColumnCount(len(cols))
        self.tbl.setHorizontalHeaderLabels(cols)
        self.tbl.setRowCount(len(self.contracts))

        od=0; bk=0; th=0.0; kalan=0.0; cm=date.today().month
        for row, c in enumerate(self.contracts):
            cid = c["id"]; pays = self.payments.get(cid, {})
            ki = QTableWidgetItem(c["kiraci"]); ki.setFont(QFont("Arial",9,QFont.Bold))
            ki.setData(Qt.UserRole, {"cid": cid, "tip": "kiraci_row"})
            self.tbl.setItem(row, 0, ki)
            self.tbl.setItem(row, 1, QTableWidgetItem(c["bas"]))
            self.tbl.setItem(row, 2, QTableWidgetItem(c["bit"]))
            self.tbl.setItem(row, 3, QTableWidgetItem(c.get("odeme_gunu","")))
            ti = QTableWidgetItem("₺{:,.0f}".format(c["tutar"]).replace(",","."))
            ti.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
            self.tbl.setItem(row, 4, ti)
            co = 2  # used for month-start offset calc below

            bas = datetime.strptime(c["bas"],"%d.%m.%Y").date()
            bit = datetime.strptime(c["bit"],"%d.%m.%Y").date()
            ms = 5  # months start at col 5
            for mi in range(12):
                col = ms + mi; ay = mi + 1
                mst = date(self.year, ay, 1)
                in_c = (bas <= date(self.year, ay, 28)) and (bit >= mst)
                if not in_c:
                    it = QTableWidgetItem(""); it.setBackground(QBrush(C_DISARI))
                    it.setFlags(Qt.ItemIsEnabled); self.tbl.setItem(row, col, it); continue
                d = pays.get(ay, "ODENMEDI")
                this_month = (ay == cm and self.year == date.today().year)
                if d == "ODENDI":
                    txt, bg = "ÖDENDİ", C_ODENDI
                    od += 1 if this_month else 0; th += c["tutar"] if this_month else 0
                elif d == "ODENMEDI":
                    txt, bg = "ÖDENMEDİ", C_ODENMEDI
                    bk += 1 if this_month else 0; kalan += c["tutar"] if this_month else 0
                elif d.startswith("KISMI:"):
                    txt, bg = d[6:], C_KISMI
                    if this_month:
                        import re as _re
                        _km = _re.search(r'Odenen[:\s]+([\d.,]+)', d[6:], _re.IGNORECASE)
                        if _km:
                            _paid = float(_km.group(1).replace(".", "").replace(",", "."))
                            th    += _paid
                            kalan += max(0.0, c["tutar"] - _paid)
                        else:
                            kalan += c["tutar"]
                else:
                    txt, bg = "", C_ODENMEDI
                it = QTableWidgetItem(txt); it.setBackground(QBrush(bg))
                it.setTextAlignment(Qt.AlignCenter|Qt.AlignVCenter)
                it.setData(Qt.UserRole, {"cid": cid, "ay": ay, "durum": d})
                self.tbl.setItem(row, col, it)

            not_col = ms + 12
            not_it = QTableWidgetItem(self.yil_nots.get(cid,""))
            not_it.setBackground(QBrush(QColor("#e8eaf6")))
            not_it.setTextAlignment(Qt.AlignLeft|Qt.AlignVCenter)
            not_it.setData(Qt.UserRole, {"cid": cid, "tip": "yil_notu"})
            self.tbl.setItem(row, not_col, not_it)

            bbg = C_ROW_ODD if row % 2 == 0 else C_ROW_EVEN
            for c2 in range(ms):
                it2 = self.tbl.item(row, c2)
                if it2: it2.setBackground(QBrush(bbg))
            self.tbl.setRowHeight(row, 30)

        self._fit_columns()
        self.kpis["toplam"].vl.setText(str(len(self.contracts)))
        self.kpis["odendi"].vl.setText(str(od))
        self.kpis["bekliyor"].vl.setText(str(bk))
        self.kpis["gelir"].vl.setText("₺{:,.0f}".format(th).replace(",","."))
        self.kpis["kalan"].vl.setText("₺{:,.0f}".format(kalan).replace(",","."))

    # ── Context menu ─────────────────────────────────────────────────────────
    def _ctx(self, pos):
        it = self.tbl.itemAt(pos)
        if not it: return
        d = it.data(Qt.UserRole)
        if not d: return
        m = QMenu(self)
        m.setStyleSheet(f"QMenu{{font-size:10pt;}}QMenu::item:selected{{background:{self.hdr_color};color:white;}}")

        if d.get("tip") == "kiraci_row":
            cid = d["cid"]
            m.addAction("📊  Döküm Aç").triggered.connect(lambda: self._dokum(cid))
            m.addSeparator()
            m.addAction("✅  Bu Ay Ödendi İşaretle").triggered.connect(
                lambda: self._set_odendi(cid, date.today().month))
            m.addSeparator()
            m.addAction("✏️  Kiracı / Sözleşme Düzenle").triggered.connect(
                lambda: self._edit_contract(cid))
            m.addAction("🗑️  Kiracıyı Listeden Kaldır").triggered.connect(
                lambda: self._del_contract(cid))
            m.exec_(self.tbl.viewport().mapToGlobal(pos)); return

        if d.get("tip") == "yil_notu":
            cid = d["cid"]
            cr = next((c for c in self.contracts if c["id"] == cid), None)
            if not cr: return
            mv = self.yil_nots.get(cid,"")
            m.addAction("📝  Genel Not Ekle / Düzenle").triggered.connect(
                lambda: self._yil_not(cid, cr["kiraci"], mv))
            if mv: m.addAction("🗑️  Notu Sil").triggered.connect(lambda: self._yil_not_sil(cid))
            m.exec_(self.tbl.viewport().mapToGlobal(pos)); return

        cid = d["cid"]; ay = d["ay"]; dur = d["durum"]
        cr = next((c for c in self.contracts if c["id"] == cid), None)
        if not cr: return
        if dur != "ODENDI":
            m.addAction("Ödendi Olarak İşaretle").triggered.connect(lambda: self._set_odendi(cid,ay))
        if dur != "ODENMEDI":
            m.addAction("Ödenmedi Olarak İşaretle").triggered.connect(lambda: self._set(cid,ay,"ODENMEDI"))
        m.addSeparator()
        mv = dur[6:] if dur.startswith("KISMI:") else ""
        m.addAction("📝  Not Ekle / Düzenle").triggered.connect(
            lambda: self._note(cid,ay,cr["kiraci"],mv))
        m.exec_(self.tbl.viewport().mapToGlobal(pos))

    # ── İşlem metodları ──────────────────────────────────────────────────────
    def _set(self, cid, ay, d):
        self.payments.setdefault(cid,{})[ay] = d; self._load(); self._notify()

    def _set_odendi(self, cid, ay):
        cr = next((c for c in self.contracts if c["id"] == cid), None)
        if not cr: return
        dlg = OdemeDetayDialog(cr["kiraci"], AYLAR_TR[ay-1], self)
        odeme_bilgi = None
        if dlg.exec_() == QDialog.Accepted:
            odeme_bilgi = dlg.get_data()
            self.odeme_detay.setdefault(cid,{})[ay] = odeme_bilgi
        self.payments.setdefault(cid,{})[ay] = "ODENDI"; self._load(); self._notify()
        # Otomatik DB işlem kaydı oluştur
        if self.create_tx_cb:
            try:
                self.create_tx_cb(
                    cr["kiraci"], ay, float(cr.get("tutar", 0)),
                    odeme_bilgi, cr.get("aciklama_kw", "kira")
                )
            except Exception:
                pass

    def _dokum(self, cid):
        try:
            cr = next((c for c in self.contracts if c["id"] == cid), None)
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
            QMessageBox.critical(self,"Hata",f"{type(e).__name__}: {e}\n\n{traceback.format_exc()}")

    def _on_dbl_click(self, row, col):
        if col == 0:
            it = self.tbl.item(row, 0)
            if it:
                d = it.data(Qt.UserRole)
                if d and d.get("tip") == "kiraci_row":
                    self._dokum(d["cid"])

    def _yil_not(self, cid, kiraci, mevcut):
        dlg = PaymentNoteDialog(kiraci,"Genel Not",mevcut,self)
        if dlg.exec_() == QDialog.Accepted:
            n = dlg.get_note()
            if n: self.yil_nots[cid] = n
            elif cid in self.yil_nots: del self.yil_nots[cid]
            self._load(); self._notify()

    def _yil_not_sil(self, cid):
        self.yil_nots.pop(cid, None); self._load(); self._notify()

    def _note(self, cid, ay, kr, mv):
        dlg = PaymentNoteDialog(kr, AYLAR_TR[ay-1], mv, self)
        if dlg.exec_() == QDialog.Accepted:
            n = dlg.get_note()
            self.payments.setdefault(cid,{})[ay] = f"KISMI:{n}" if n else "ODENMEDI"
            self._load(); self._notify()

    def _year_chg(self, t):
        self.year = int(t); self._load(); self._notify()

    def _fit_columns(self):
        """Sütunları viewport genişliğine oransal olarak dağıt."""
        if not hasattr(self, "tbl") or self.tbl.columnCount() < 18:
            return
        avail = self.tbl.viewport().width()
        if avail <= 0:
            return
        # Oransal sabit genişlikler
        c_kiraci = max(130, int(avail * 0.13))
        c_date   = max(68,  int(avail * 0.061))
        c_tutar  = max(75,  int(avail * 0.068))
        c_not    = max(80,  int(avail * 0.07))
        # Ay sütunları için kalan alan
        fixed = c_kiraci + c_date * 3 + c_tutar + c_not
        c_ay  = max(58, int((avail - fixed) / 12))
        self.tbl.setColumnWidth(0, c_kiraci)
        for col in range(1, 4):
            self.tbl.setColumnWidth(col, c_date)
        self.tbl.setColumnWidth(4, c_tutar)
        for col in range(5, 17):
            self.tbl.setColumnWidth(col, c_ay)
        self.tbl.setColumnWidth(17, c_not)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "tbl"):
            self._fit_columns()

    def _add(self):
        dlg = ContractDialog(parent=self)
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            if not data["kiraci"]: return
            data["id"] = max((c["id"] for c in self.contracts), default=0) + 1
            self.contracts.append(data); self._load(); self._notify()

    def _edit_contract(self, cid):
        cr = next((c for c in self.contracts if c["id"] == cid), None)
        if not cr: return
        dlg = ContractDialog(contract=cr, parent=self)
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            if not data["kiraci"]: return
            cr.update(data); self._load(); self._notify()

    def _del_contract(self, cid):
        cr = next((c for c in self.contracts if c["id"] == cid), None)
        if not cr: return
        ret = QMessageBox.question(
            self,"Kiracı Kaldır",
            f"<b>{cr['kiraci']}</b> listeden kaldırılsın mı?\nTüm ödeme kayıtları da silinir.",
            QMessageBox.Yes | QMessageBox.No
        )
        if ret == QMessageBox.Yes:
            # Çöp kutusuna kaydet
            try:
                kiraci_data = {
                    "tab_name": self._tab_name,
                    "contract": cr,
                    "payments": {str(cid): {str(m): v for m, v in self.payments.get(cid, {}).items()}},
                    "odeme_detay": {str(cid): {str(m): v for m, v in self.odeme_detay.get(cid, {}).items()}},
                    "yil_nots": {str(cid): self.yil_nots[cid]} if cid in self.yil_nots else {},
                }
                label = f"Kiracı: {cr['kiraci']} | {self._tab_name} | {cr.get('bas','')} - {cr.get('bit','')}"
                from src.services.recycle_bin_service import RecycleBinService
                RecycleBinService._add(self.user_id, 'kira_kiraci', None, label, kiraci_data)
            except Exception as _e:
                print(f"Çöp kutusu kayıt hatası: {_e}")
            self.contracts = [c for c in self.contracts if c["id"] != cid]
            self.payments.pop(cid, None); self.yil_nots.pop(cid, None)
            self._load(); self._notify()


# ── Ana Kira Takip Widget (ana pencereye eklenir) ───────────────────────────

class KiraTakipWidget(QWidget):
    """
    Ana uygulamaya eklenen kira takip sekmesi.
    Veri data/kira_takip_data_{user_id}.json dosyasından yüklenir/kaydedilir.
    """
    def __init__(self, user_id: int = 0, parent=None):
        super().__init__(parent)
        self.user_id  = user_id
        self.data_file = DATA_DIR / f"kira_takip_data_{user_id}.json"
        self._build()
        self._load_from_file()
        self._sync_from_transactions()

    # ── Dosya kayıt / yükle ──────────────────────────────────────────────────
    def _save(self):
        """Tüm sekme verilerini JSON'a yazar."""
        DATA_DIR.mkdir(exist_ok=True)
        tabs_data = []
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if isinstance(w, TahsilatWidget):
                tabs_data.append({
                    "tab_name": self.tabs.tabText(i),
                    **w.to_dict(),
                })
        tab_widths = {}
        tb = self.tabs.tabBar()
        if isinstance(tb, ResizableTabBar):
            tab_widths = tb.get_widths_by_name()
        try:
            self.data_file.write_text(
                json.dumps({"tabs": tabs_data, "tab_widths": tab_widths},
                           ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        except Exception as e:
            print(f"[KiraTakip] Kayıt hatası: {e}")

    def _load_from_file(self):
        if not self.data_file.exists():
            return  # Boş başlar
        try:
            data = json.loads(self.data_file.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[KiraTakip] Yükleme hatası: {e}"); return

        for td in data.get("tabs", []):
            w = TahsilatWidget(
                title      = td.get("title",""),
                hdr_color  = td.get("hdr_color","#1565c0"),
                contracts  = td.get("contracts",[]),
                payments   = td.get("payments",{}),
                year       = td.get("year", date.today().year),
                odeme_detay= td.get("odeme_detay",{}),
                yil_nots   = td.get("yil_nots",{}),
                on_change  = self._save,
                create_tx_cb = self._create_kira_transaction,
                user_id    = self.user_id,
                tab_name   = td.get("tab_name", ""),
            )
            idx = self.tabs.addTab(w, td.get("tab_name","Sekme"))
            self.tabs.setTabToolTip(idx, td.get("tab_name","Sekme"))

        # Kayıtlı sekme genişliklerini geri yükle
        saved_widths = data.get("tab_widths", {})
        if saved_widths:
            tb = self.tabs.tabBar()
            if isinstance(tb, ResizableTabBar):
                tb.apply_widths_by_name(saved_widths)

    # ── UI inşası ─────────────────────────────────────────────────────────────
    def _build(self):
        lay = QVBoxLayout(self); lay.setContentsMargins(0,0,0,0); lay.setSpacing(0)

        # Sekme yönetim toolbar
        tb = QHBoxLayout(); tb.setContentsMargins(8,4,8,4); tb.setSpacing(6)
        tb.addStretch()
        excel_imp_btn = QPushButton("📥 Excel'den Aktar")
        excel_imp_btn.setStyleSheet(
            "background:#00897b;color:white;padding:4px 12px;border-radius:5px;font-size:9pt;")
        excel_imp_btn.clicked.connect(self._import_excel)
        excel_exp_btn = QPushButton("📤 Excel'e Aktar")
        excel_exp_btn.setStyleSheet(
            "background:#558b2f;color:white;padding:4px 12px;border-radius:5px;font-size:9pt;")
        excel_exp_btn.clicked.connect(self._export_excel)
        tb.addWidget(excel_imp_btn); tb.addWidget(excel_exp_btn)
        self._rename_btn = QPushButton("✏️ Sekmeyi Düzenle")
        self._rename_btn.setStyleSheet(
            "background:#1976d2;color:white;padding:4px 12px;border-radius:5px;font-size:9pt;")
        self._rename_btn.clicked.connect(self._rename_tab)
        self._del_btn = QPushButton("🗑️ Sekmeyi Sil")
        self._del_btn.setStyleSheet(
            "background:#e53935;color:white;padding:4px 12px;border-radius:5px;font-size:9pt;")
        self._del_btn.clicked.connect(self._delete_tab)
        add_btn = QPushButton("＋ Yeni Grup Ekle")
        add_btn.setStyleSheet(
            "background:#43a047;color:white;font-weight:bold;padding:4px 14px;"
            "border-radius:5px;font-size:9pt;")
        add_btn.clicked.connect(self._add_tab)
        save_widths_btn = QPushButton("💾 Kaydet")
        save_widths_btn.setToolTip("Sekme genişliklerini kaydet")
        save_widths_btn.setStyleSheet(
            "background:#546e7a;color:white;padding:4px 10px;border-radius:5px;font-size:9pt;")
        save_widths_btn.clicked.connect(self._save)
        tb.addWidget(self._rename_btn); tb.addWidget(self._del_btn)
        tb.addWidget(add_btn); tb.addWidget(save_widths_btn)
        tb_frame = QWidget(); tb_frame.setLayout(tb)
        tb_frame.setStyleSheet("background:#eceff1;border-bottom:1px solid #cfd8dc;")
        lay.addWidget(tb_frame)

        # Sekmeler
        self.tabs = QTabWidget()
        _rbar = ResizableTabBar()
        _rbar.widthsChanged.connect(self._save)
        self.tabs.setTabBar(_rbar)
        self.tabs.setUsesScrollButtons(True)
        self.tabs.setElideMode(Qt.ElideNone)
        self.tabs.setStyleSheet(
            "QTabBar::tab{padding:8px 18px;font-size:11pt;font-weight:bold;}"
            "QTabBar::tab:selected{background:white;}"
            "QTabBar::scroller{width:26px;}"
            "QTabBar QToolButton{background:#eceff1;border:1px solid #ccc;border-radius:3px;}"
        )
        self.tabs.tabBar().setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabs.tabBar().customContextMenuRequested.connect(self._tab_ctx_menu)
        lay.addWidget(self.tabs)

    def _next_color(self):
        used = {self.tabs.widget(i).hdr_color
                for i in range(self.tabs.count())
                if isinstance(self.tabs.widget(i), TahsilatWidget)}
        for c in TAB_COLORS:
            if c not in used: return c
        return TAB_COLORS[self.tabs.count() % len(TAB_COLORS)]

    def _add_tab(self):
        dlg = TabNameDialog("","",self._next_color(), self)
        if dlg.exec_() != QDialog.Accepted: return
        d = dlg.get_data()
        w = TahsilatWidget(d["title"], d["color"], [], {}, on_change=self._save,
                           create_tx_cb=self._create_kira_transaction,
                           user_id=self.user_id, tab_name=d["tab_name"])
        self.tabs.addTab(w, d["tab_name"])
        self.tabs.setTabToolTip(self.tabs.count()-1, d["tab_name"])
        self.tabs.setCurrentIndex(self.tabs.count()-1)
        self._save()

    # ── DB Senkronizasyon ─────────────────────────────────────────────────────
    def _create_kira_transaction(self, kiraci: str, ay: int, tutar: float,
                                     odeme_bilgi: dict, aciklama_kw: str = "kira"):
        """Kira Takip'te ÖDENDİ işaretlenince otomatik DB işlem kaydı oluşturur."""
        if not self.user_id:
            return
        kw = self._tr_lower(aciklama_kw.strip() or "kira")
        try:
            from src.services.transaction_service import TransactionService
            from src.database.models import TransactionType, PaymentMethod
            from datetime import date as _d
            cur_year = date.today().year
            # Aynı ay + aynı kiracı + aynı konu için işlem zaten var mı?
            existing = TransactionService.get_all_transactions(
                self.user_id,
                start_date=_d(cur_year, ay, 1),
                end_date=_d(cur_year, ay, 28),
            )
            for t in existing:
                if (self._tr_lower(t.customer_name.strip()) == self._tr_lower(kiraci.strip()) and
                        (kw in self._tr_lower(t.subject or "") or
                         kw in self._tr_lower(t.description or ""))):
                    return  # Zaten kayıtlı
            # Ödeme detayından tarih ve banka bilgisini al
            tx_date = _d(cur_year, ay, date.today().day if ay == date.today().month else 1)
            banka_adi = ""
            aciklama = f"{AYLAR_TR[ay-1]} {aciklama_kw.upper()} ÖDEMESİ"
            if odeme_bilgi:
                banka_adi = odeme_bilgi.get("banka", "").strip()
                aciklama_d = odeme_bilgi.get("aciklama", "").strip()
                if aciklama_d:
                    aciklama = aciklama_d
                try:
                    from datetime import datetime as _dt
                    tx_date = _dt.strptime(odeme_bilgi["tarih"], "%d.%m.%Y").date()
                except Exception:
                    pass
            payment_method = PaymentMethod.BANKA if banka_adi else PaymentMethod.NAKIT
            TransactionService.create_transaction(
                user_id=self.user_id,
                transaction_date=tx_date,
                transaction_type=TransactionType.GELIR,
                payment_method=payment_method,
                customer_name=kiraci,
                description=aciklama,
                amount=tutar,
                subject=aciklama_kw.upper() + " ÖDEMESİ",
                payment_type=banka_adi or None,
            )
        except Exception as e:
            print(f"[KiraTakip] İşlem oluşturma hatası: {e}")

    @staticmethod
    def _tr_lower(s: str) -> str:
        """Türkçe karakterleri ASCII'ye çevirerek güvenli lowercase karşılaştırma yapar."""
        return (s
                .replace("İ", "I").replace("Ş", "S").replace("Ç", "C")
                .replace("Ğ", "G").replace("Ü", "U").replace("Ö", "O")
                .replace("ı", "i").replace("ş", "s").replace("ç", "c")
                .replace("ğ", "g").replace("ü", "u").replace("ö", "o")
                .lower())

    def showEvent(self, event):
        """Sekme her gösterildiğinde DB ile tam mutabakat yapar."""
        super().showEvent(event)
        self._sync_from_transactions()

    def _sync_from_transactions(self):
        """DB kira işlemlerini Kira Takip'e tam mutabakat ile yansıtır.
        - DB'de işlem var   → ODENDI veya KISMI
        - DB'de işlem yoksa → ODENDI ise ODENMEDI'ye geri al
        Sekme her gösterildiğinde çalışır.
        """
        if not self.user_id:
            return
        try:
            from src.services.transaction_service import TransactionService
            from datetime import date as _d
            from datetime import datetime as _dt

            years = set()
            for i in range(self.tabs.count()):
                w = self.tabs.widget(i)
                if isinstance(w, TahsilatWidget):
                    years.add(w.year)
            if not years:
                return

            # Tüm sekmelerdeki sözleşmelerden kullanılan konu kelimelerini topla
            all_kws = set()
            for i in range(self.tabs.count()):
                w = self.tabs.widget(i)
                if isinstance(w, TahsilatWidget):
                    for c in w.contracts:
                        kw = self._tr_lower(c.get("aciklama_kw", "kira").strip() or "kira")
                        all_kws.add(kw)
            if not all_kws:
                all_kws = {"kira"}

            # pay_map anahtarı: (konu_kw, kiraci_key, ay)
            year_pay = {}
            for yr in years:
                txns = TransactionService.get_all_transactions(
                    self.user_id,
                    start_date=_d(yr, 1, 1),
                    end_date=_d(yr, 12, 31),
                )
                pay_map    = {}
                pay_detail = {}
                for t in txns:
                    subj = self._tr_lower(t.subject or "")
                    desc = self._tr_lower(t.description or "")
                    cn   = self._tr_lower(t.customer_name.strip())
                    ay   = t.transaction_date.month
                    for kw in all_kws:
                        if kw in subj or kw in desc:
                            key = (kw, cn, ay)
                            pay_map[key]    = pay_map.get(key, 0.0) + float(t.amount or 0)
                            pay_detail[key] = {
                                "tarih":    t.transaction_date.strftime("%d.%m.%Y"),
                                "banka":    t.payment_type or "",
                                "aciklama": t.description or "",
                            }
                year_pay[yr] = (pay_map, pay_detail)

            changed = False
            for i in range(self.tabs.count()):
                w = self.tabs.widget(i)
                if not isinstance(w, TahsilatWidget):
                    continue
                yr = w.year
                pay_map, pay_detail = year_pay.get(yr, ({}, {}))

                for c in w.contracts:
                    kiraci_key = self._tr_lower(c["kiraci"].strip())
                    cid        = int(c["id"])
                    monthly    = float(c.get("tutar", 0))
                    c_kw       = self._tr_lower(c.get("aciklama_kw", "kira").strip() or "kira")
                    try:
                        bas = _dt.strptime(c["bas"], "%d.%m.%Y").date()
                        bit = _dt.strptime(c["bit"], "%d.%m.%Y").date()
                    except Exception:
                        continue

                    for ay in range(1, 13):
                        mst  = _d(yr, ay, 1)
                        in_c = (bas <= _d(yr, ay, 28)) and (bit >= mst)
                        if not in_c:
                            continue

                        key       = (c_kw, kiraci_key, ay)
                        cur_durum = w.payments.get(cid, {}).get(ay, "ODENMEDI")

                        if key in pay_map:
                            total_paid = pay_map[key]
                            if monthly > 0 and total_paid < (monthly - 0.01):
                                kalan     = monthly - total_paid
                                new_durum = (
                                    f"KISMI:Odenen: {total_paid:,.0f} TL | Kalan: {kalan:,.0f} TL"
                                    .replace(",", ".")
                                )
                            else:
                                new_durum = "ODENDI"
                            if cur_durum != new_durum:
                                w.payments.setdefault(cid, {})[ay] = new_durum
                                detay = pay_detail.get(key)
                                if detay:
                                    w.odeme_detay.setdefault(cid, {})[ay] = detay
                                changed = True
                        else:
                            if cur_durum == "ODENDI":
                                w.payments.setdefault(cid, {})[ay] = "ODENMEDI"
                                changed = True

            if changed:
                self._save()
                for i in range(self.tabs.count()):
                    w = self.tabs.widget(i)
                    if isinstance(w, TahsilatWidget):
                        w._load()
        except Exception as e:
            print(f"[KiraTakip] Sync hatası: {e}")
    # ── Excel Aktarım ─────────────────────────────────────────────────────────
    def _export_excel(self):
        """Aktif sekmedeki kiracı verilerini Excel dosyasına aktarır."""
        idx = self.tabs.currentIndex()
        if idx < 0:
            QMessageBox.warning(self, "Uyarı", "Aktif sekme bulunamadı."); return
        w = self.tabs.widget(idx)
        if not isinstance(w, TahsilatWidget):
            QMessageBox.warning(self, "Uyarı", "Aktif sekme kira takip sekmesi değil."); return

        from PyQt5.QtWidgets import QFileDialog
        tab_name = self.tabs.tabText(idx).replace("/","-").replace("\\","-")
        path, _ = QFileDialog.getSaveFileName(
            self, "Excel Olarak Kaydet",
            f"kira_takip_{tab_name}_{w.year}.xlsx",
            "Excel Dosyası (*.xlsx)"
        )
        if not path: return

        try:
            import openpyxl
            from openpyxl.styles import PatternFill, Font, Alignment
            from openpyxl.utils import get_column_letter
            from datetime import date as _d, datetime as _dt

            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = tab_name[:31]

            headers = ["KİRACI ADI", "SÖZLEŞME BAŞL.", "SÖZLEŞME BİTİŞ",
                       "ÖDEME GÜNÜ", f"AYLIK TUTAR (TL) - {w.year} YILI"]
            headers += AYLAR_TR
            headers.append("GENEL NOT")

            hdr_fill   = PatternFill("solid", fgColor="1565C0")
            hdr_font   = Font(bold=True, color="FFFFFF")
            center_aln = Alignment(horizontal="center", vertical="center")
            odendi_fill   = PatternFill("solid", fgColor="C8F7C5")
            odenmedi_fill = PatternFill("solid", fgColor="FFD6D6")
            kismi_fill    = PatternFill("solid", fgColor="FFF3CD")
            disari_fill   = PatternFill("solid", fgColor="EBEBEB")

            for col, h in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=h)
                cell.fill = hdr_fill; cell.font = hdr_font; cell.alignment = center_aln
            ws.row_dimensions[1].height = 22

            for row_idx, c in enumerate(w.contracts, 2):
                cid  = c["id"]
                pays = w.payments.get(cid, {})
                ws.cell(row=row_idx, column=1, value=c["kiraci"])
                ws.cell(row=row_idx, column=2, value=c["bas"])
                ws.cell(row=row_idx, column=3, value=c["bit"])
                ws.cell(row=row_idx, column=4, value=c.get("odeme_gunu", ""))
                tutar_cell = ws.cell(row=row_idx, column=5, value=c.get("tutar", 0))
                tutar_cell.number_format = '#,##0.00 "TL"'
                try:
                    bas = _dt.strptime(c["bas"], "%d.%m.%Y").date()
                    bit = _dt.strptime(c["bit"], "%d.%m.%Y").date()
                except Exception:
                    bas = bit = _d(w.year, 1, 1)
                for ay in range(1, 13):
                    col_n = 5 + ay
                    mst   = _d(w.year, ay, 1)
                    in_c  = (bas <= _d(w.year, ay, 28)) and (bit >= mst)
                    if not in_c:
                        cell = ws.cell(row=row_idx, column=col_n, value="—")
                        cell.fill = disari_fill; cell.alignment = center_aln
                    else:
                        d_val = pays.get(ay, "ODENMEDI")
                        if d_val == "ODENDI":
                            txt = "ÖDENDİ";    fill = odendi_fill
                        elif d_val.startswith("KISMI:"):
                            txt = d_val[6:];    fill = kismi_fill
                        else:
                            txt = "ÖDENMEDİ"; fill = odenmedi_fill
                        cell = ws.cell(row=row_idx, column=col_n, value=txt)
                        cell.fill = fill; cell.alignment = center_aln
                ws.cell(row=row_idx, column=18, value=w.yil_nots.get(cid, ""))
                ws.row_dimensions[row_idx].height = 20

            ws.column_dimensions["A"].width = 26
            for letter, w_ in [("B",14),("C",14),("D",20),("E",20)]:
                ws.column_dimensions[letter].width = w_
            for i in range(6, 18):
                ws.column_dimensions[get_column_letter(i)].width = 12
            ws.column_dimensions[get_column_letter(18)].width = 28
            ws.freeze_panes = "F2"

            wb.save(path)
            QMessageBox.information(self, "Başarılı",
                f"{len(w.contracts)} kiracı Excel'e aktarıldı:\n{path}")
        except Exception as e:
            import traceback
            QMessageBox.critical(self, "Hata",
                f"Excel aktarımı başarısız:\n{e}\n\n{traceback.format_exc()}")

    def _import_excel(self):
        """Excel dosyasından kiracıları aktif sekmeye aktarır."""
        idx = self.tabs.currentIndex()
        if idx < 0:
            QMessageBox.warning(self, "Uyarı", "Aktif sekme bulunamadı."); return
        w = self.tabs.widget(idx)
        if not isinstance(w, TahsilatWidget):
            QMessageBox.warning(self, "Uyarı", "Aktif sekme kira takip sekmesi değil."); return

        from PyQt5.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(
            self, "Excel Dosyası Seç", "", "Excel Dosyaları (*.xlsx *.xls)"
        )
        if not path: return

        try:
            import openpyxl, re as _re2
            wb = openpyxl.load_workbook(path, data_only=True)
            ws = wb.active
            rows_data = list(ws.iter_rows(min_row=2, values_only=True))
            if not rows_data:
                QMessageBox.warning(self, "Uyarı", "Excel dosyasında veri bulunamadı."); return

            existing_names = {c["kiraci"].strip().lower() for c in w.contracts}
            max_id = max((c["id"] for c in w.contracts), default=0)
            added = 0; skipped = 0
            date_pat = _re2.compile(r'^\d{2}\.\d{2}\.\d{4}$')

            for row in rows_data:
                if not row or not row[0]: continue
                kiraci = str(row[0]).strip()
                if not kiraci: continue
                bas = str(row[1]).strip() if len(row) > 1 and row[1] else ""
                bit = str(row[2]).strip() if len(row) > 2 and row[2] else ""
                odeme_gunu = str(row[3]).strip() if len(row) > 3 and row[3] else ""
                try:
                    tutar = float(str(row[4]).replace("TL","").replace(" ","").replace(",",".")) \
                        if len(row) > 4 and row[4] else 0.0
                except (ValueError, TypeError):
                    tutar = 0.0
                if not date_pat.match(bas) or not date_pat.match(bit):
                    skipped += 1; continue
                if kiraci.lower() in existing_names:
                    skipped += 1; continue

                max_id += 1
                contract = {"id": max_id, "kiraci": kiraci,
                            "bas": bas, "bit": bit,
                            "odeme_gunu": odeme_gunu, "tutar": tutar}
                w.contracts.append(contract)
                existing_names.add(kiraci.lower())

                for ay in range(1, 13):
                    col_idx = 4 + ay
                    if col_idx < len(row) and row[col_idx]:
                        val = str(row[col_idx]).strip()
                        if val in ("ÖDENDİ", "ODENDİ", "ODENDI"):
                            w.payments.setdefault(max_id, {})[ay] = "ODENDI"
                        elif val and val not in ("—", "ÖDENMEDİ", "ODENMEDI"):
                            w.payments.setdefault(max_id, {})[ay] = f"KISMI:{val}"
                added += 1

            w._load(); self._save()
            msg = f"{added} kiracı başarıyla içe aktarıldı."
            if skipped:
                msg += f"\n{skipped} satır atlandı (aynı isim veya hatalı tarih formatı)."
            QMessageBox.information(self, "İçe Aktarma Tamamlandı", msg)
        except Exception as e:
            import traceback
            QMessageBox.critical(self, "Hata",
                f"İçe aktarma başarısız:\n{e}\n\n{traceback.format_exc()}")

    def _rename_tab(self):
        idx = self.tabs.currentIndex()
        if idx < 0: return
        w = self.tabs.widget(idx)
        dlg = TabNameDialog(
            self.tabs.tabText(idx),
            getattr(w,"title",""),
            getattr(w,"hdr_color","#1565c0"), self
        )
        if dlg.exec_() != QDialog.Accepted: return
        d = dlg.get_data()
        self.tabs.setTabText(idx, d["tab_name"])
        self.tabs.setTabToolTip(idx, d["tab_name"])
        w.title = d["title"]; w.hdr_color = d["color"]; w._load()
        self._save()

    def _delete_tab(self):
        idx = self.tabs.currentIndex()
        if idx < 0: return
        tab_name = self.tabs.tabText(idx)
        ret = QMessageBox.question(
            self,"Sekmeyi Sil",
            f"<b>{tab_name}</b> sekmesi ve tüm kiracı/ödeme kayıtları silinsin mi?",
            QMessageBox.Yes | QMessageBox.No
        )
        if ret == QMessageBox.Yes:
            # Çöp kutusuna kaydet
            try:
                w = self.tabs.widget(idx)
                if isinstance(w, TahsilatWidget):
                    tab_data = {"tab_name": tab_name, **w.to_dict()}
                    label = f"Kira Takip Sekme: {tab_name} | {len(w.contracts)} sözleşme"
                    from src.services.recycle_bin_service import RecycleBinService
                    RecycleBinService._add(
                        self.user_id, 'kira_takip_sekme', None, label, tab_data
                    )
            except Exception as _e:
                print(f"Çöp kutusu kayıt hatası: {_e}")
            self.tabs.removeTab(idx); self._save()

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
