"""
Otomatik Güncelleme Modülü
- Başlangıçta GitHub'dan yeni sürüm kontrolü yapar
- Güncelleme varsa kullanıcıya sorar
- Onay verilirse indirir ve kendini değiştirir
"""
import sys
import os
import json
import threading
import subprocess
import tempfile
from pathlib import Path

import urllib.request
import urllib.error

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QProgressBar, QMessageBox, QTextEdit)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont


def _parse_version(v: str):
    """'1.2.3' → (1, 2, 3) tuple"""
    try:
        return tuple(int(x) for x in v.strip().lstrip("v").split("."))
    except Exception:
        return (0, 0, 0)


def _is_newer(remote: str, local: str) -> bool:
    return _parse_version(remote) > _parse_version(local)


# ─────────────────────────────────────────────────────────
# İndirme Thread'i
# ─────────────────────────────────────────────────────────
class DownloadThread(QThread):
    progress = pyqtSignal(int)       # 0-100
    finished = pyqtSignal(str)       # indirilen dosya yolu
    error    = pyqtSignal(str)

    def __init__(self, url: str, dest: str):
        super().__init__()
        self.url  = url
        self.dest = dest

    def run(self):
        try:
            with urllib.request.urlopen(self.url, timeout=30) as resp:
                total = int(resp.headers.get("Content-Length", 0))
                downloaded = 0
                chunk_size = 65536
                with open(self.dest, "wb") as f:
                    while True:
                        chunk = resp.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total > 0:
                            self.progress.emit(int(downloaded * 100 / total))
            self.finished.emit(self.dest)
        except Exception as e:
            self.error.emit(str(e))


# ─────────────────────────────────────────────────────────
# İndirme Dialog
# ─────────────────────────────────────────────────────────
class DownloadDialog(QDialog):
    def __init__(self, url: str, dest: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Güncelleme İndiriliyor")
        self.setModal(True)
        self.setFixedWidth(420)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        lbl = QLabel("⬇️  Yeni sürüm indiriliyor, lütfen bekleyin...")
        lbl.setFont(QFont("Segoe UI", 10))
        layout.addWidget(lbl)

        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setValue(0)
        self.bar.setMinimumHeight(24)
        layout.addWidget(self.bar)

        self.pct_label = QLabel("% 0")
        self.pct_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.pct_label)

        self.thread = DownloadThread(url, dest)
        self.thread.progress.connect(self._on_progress)
        self.thread.finished.connect(self._on_done)
        self.thread.error.connect(self._on_error)
        self.thread.start()

        self.result_path = None

    def _on_progress(self, pct):
        self.bar.setValue(pct)
        self.pct_label.setText(f"% {pct}")

    def _on_done(self, path):
        self.result_path = path
        self.accept()

    def _on_error(self, msg):
        QMessageBox.critical(self, "İndirme Hatası",
                             f"Güncelleme indirilemedi:\n{msg}")
        self.reject()


# ─────────────────────────────────────────────────────────
# Güncelleme Teklif Dialog
# ─────────────────────────────────────────────────────────
class UpdateDialog(QDialog):
    def __init__(self, current: str, new_ver: str, notes: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔄 Güncelleme Mevcut")
        self.setModal(True)
        self.setMinimumWidth(440)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("🎉  Yeni Sürüm Mevcut!")
        title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        title.setStyleSheet("color: #1565C0;")
        layout.addWidget(title)

        ver_lbl = QLabel(
            f"<b>Mevcut sürüm:</b>  {current}<br>"
            f"<b>Yeni sürüm:</b>  &nbsp;<span style='color:#2E7D32'>{new_ver}</span>"
        )
        ver_lbl.setFont(QFont("Segoe UI", 10))
        layout.addWidget(ver_lbl)

        if notes:
            notes_title = QLabel("📋 Değişiklikler:")
            notes_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
            layout.addWidget(notes_title)

            notes_box = QTextEdit()
            notes_box.setPlainText(notes)
            notes_box.setReadOnly(True)
            notes_box.setMaximumHeight(120)
            notes_box.setStyleSheet("background:#f5f5f5; border:1px solid #ddd; border-radius:4px;")
            layout.addWidget(notes_box)

        info = QLabel("⚠️ Uygulama güncellendikten sonra otomatik yeniden başlayacak.")
        info.setWordWrap(True)
        info.setStyleSheet("color: #666; font-size: 9pt;")
        layout.addWidget(info)

        btn_layout = QHBoxLayout()
        btn_later = QPushButton("⏭️  Sonra Hatırlat")
        btn_later.setMinimumHeight(36)
        btn_later.setStyleSheet("""
            QPushButton { background:#9E9E9E; color:white; border:none; border-radius:4px;
                          padding:8px 16px; font-size:10pt; }
            QPushButton:hover { background:#757575; }
        """)
        btn_later.clicked.connect(self.reject)

        btn_update = QPushButton("✅  Şimdi Güncelle")
        btn_update.setMinimumHeight(36)
        btn_update.setStyleSheet("""
            QPushButton { background:#1565C0; color:white; border:none; border-radius:4px;
                          padding:8px 16px; font-size:10pt; font-weight:bold; }
            QPushButton:hover { background:#0D47A1; }
        """)
        btn_update.clicked.connect(self.accept)

        btn_layout.addWidget(btn_later)
        btn_layout.addWidget(btn_update)
        layout.addLayout(btn_layout)


# ─────────────────────────────────────────────────────────
# Ana kontrol fonksiyonu
# ─────────────────────────────────────────────────────────
def check_and_update(parent=None):
    """
    Arka planda versiyon kontrolü yapar.
    Yeni sürüm varsa kullanıcıya sorar ve günceller.
    config.py içinde UPDATE_CHECK_URL tanımlı olmalıdır.
    """
    try:
        import config
        url = getattr(config, "UPDATE_CHECK_URL", "")
        enabled = getattr(config, "UPDATE_ENABLED", False)
        current = getattr(config, "APP_VERSION", "0.0.0")

        if not enabled or not url or url.startswith("https://GITHUB_KULLANICI"):
            return  # Yapılandırılmamış, sessizce geç

        def _run():
            try:
                with urllib.request.urlopen(url, timeout=8) as resp:
                    data = json.loads(resp.read().decode())
                remote_ver   = data.get("version", "0.0.0")
                download_url = data.get("download_url", "")
                notes        = data.get("notes", "")

                if _is_newer(remote_ver, current) and download_url:
                    # GUI işlemi ana thread'de yapılmalı
                    from PyQt5.QtCore import QMetaObject, Qt as Qt2
                    _show_update_dialog(parent, current, remote_ver, notes, download_url)

            except Exception as e:
                print(f"[Güncelleme] Kontrol hatası: {e}")

        t = threading.Thread(target=_run, daemon=True)
        t.start()

    except Exception as e:
        print(f"[Güncelleme] Başlatma hatası: {e}")


def _show_update_dialog(parent, current, new_ver, notes, download_url):
    """Güncelleme dialogunu göster (ana thread'de çağrılmalı)"""
    try:
        from PyQt5.QtCore import QTimer

        def show():
            dlg = UpdateDialog(current, new_ver, notes, parent)
            if dlg.exec_() == QDialog.Accepted:
                _do_update(parent, download_url, new_ver)

        # Ana event loop'tan tetikle
        QTimer.singleShot(1500, show)

    except Exception as e:
        print(f"[Güncelleme] Dialog hatası: {e}")


def _do_update(parent, download_url, new_ver):
    """Güncellemeyi indir ve uygula"""
    try:
        # İndirme hedefi
        tmp_dir = tempfile.gettempdir()
        new_exe = os.path.join(tmp_dir, "Muhasebe_guncelleme.exe")

        # İndir
        dl_dlg = DownloadDialog(download_url, new_exe, parent)
        if dl_dlg.exec_() != QDialog.Accepted or not dl_dlg.result_path:
            return

        if getattr(sys, "frozen", False):
            # Çalışan EXE'yi değiştir
            current_exe = sys.executable
            bat_path = os.path.join(tmp_dir, "_ozkaya_update.bat")
            bat_content = f"""@echo off
timeout /t 2 /nobreak >nul
move /y "{new_exe}" "{current_exe}"
start "" "{current_exe}"
del "%~f0"
"""
            with open(bat_path, "w", encoding="cp1254") as f:
                f.write(bat_content)

            QMessageBox.information(
                parent, "Güncelleme Hazır",
                f"✅ Sürüm {new_ver} indirildi!\n\n"
                "Uygulama şimdi kapanacak ve yeni sürüm otomatik başlayacak."
            )
            subprocess.Popen(["cmd", "/c", bat_path],
                             creationflags=subprocess.CREATE_NO_WINDOW)
            sys.exit(0)
        else:
            # Python script modunda
            QMessageBox.information(
                parent, "Güncelleme İndirildi",
                f"✅ Yeni sürüm {new_ver} indirildi:\n{new_exe}\n\n"
                "Script modunda çalışıyorsunuz, EXE'yi manuel değiştirin."
            )

    except Exception as e:
        QMessageBox.critical(parent, "Güncelleme Hatası",
                             f"Güncelleme uygulanamadı:\n{e}")
