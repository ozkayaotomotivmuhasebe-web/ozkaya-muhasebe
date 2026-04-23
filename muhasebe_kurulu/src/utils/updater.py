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
            # GitHub redirect'lerini takip et; User-Agent olmadan CDN reddedebilir
            req = urllib.request.Request(
                self.url,
                headers={'User-Agent': 'Mozilla/5.0 OzkayaMuhasebe-Updater'}
            )
            # timeout=120: bağlantı ve her read() için 2 dakika — yavaş bağlantılar için yeterli
            with urllib.request.urlopen(req, timeout=120) as resp:
                total = int(resp.headers.get("Content-Length") or resp.headers.get("content-length") or 0)
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
                        else:
                            self.progress.emit(min(99, int(downloaded / (55 * 1024 * 1024) * 100)))
            self.progress.emit(100)
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
    def __init__(self, current: str, new_ver: str, notes: str, parent=None, has_download: bool = True):
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

        if has_download:
            info = QLabel("⚠️ Uygulama güncellendikten sonra otomatik yeniden başlayacak.")
            info.setWordWrap(True)
            info.setStyleSheet("color: #666; font-size: 9pt;")
            layout.addWidget(info)
        else:
            info = QLabel("ℹ️ Bu güncelleme otomatik yüklendi. Uygulamayı yeniden başlatmanız yeterli.")
            info.setWordWrap(True)
            info.setStyleSheet("color: #1565C0; font-size: 9pt;")
            layout.addWidget(info)

        btn_layout = QHBoxLayout()

        if has_download:
            btn_later = QPushButton("⏭️  Sonra Hatırlat")
            btn_later.setMinimumHeight(36)
            btn_later.setStyleSheet("""
                QPushButton { background:#9E9E9E; color:white; border:none; border-radius:4px;
                              padding:8px 16px; font-size:10pt; }
                QPushButton:hover { background:#757575; }
            """)
            btn_later.clicked.connect(self.reject)
            btn_layout.addWidget(btn_later)

            btn_update = QPushButton("✅  Şimdi Güncelle")
            btn_update.setMinimumHeight(36)
            btn_update.setStyleSheet("""
                QPushButton { background:#1565C0; color:white; border:none; border-radius:4px;
                              padding:8px 16px; font-size:10pt; font-weight:bold; }
                QPushButton:hover { background:#0D47A1; }
            """)
            btn_update.clicked.connect(self.accept)
            btn_layout.addWidget(btn_update)
        else:
            btn_ok = QPushButton("✅  Tamam")
            btn_ok.setMinimumHeight(36)
            btn_ok.setStyleSheet("""
                QPushButton { background:#2E7D32; color:white; border:none; border-radius:4px;
                              padding:8px 20px; font-size:10pt; font-weight:bold; }
                QPushButton:hover { background:#1B5E20; }
            """)
            btn_ok.clicked.connect(self.accept)
            btn_layout.addWidget(btn_ok)

        layout.addLayout(btn_layout)


# ─────────────────────────────────────────────────────────
# Versiyon kontrol thread'i (QThread + signal - tam thread-safe)
# ─────────────────────────────────────────────────────────
class _VersionCheckThread(QThread):
    update_found = pyqtSignal(str, str, str, str)  # current, remote, notes, url

    def __init__(self, url, current):
        super().__init__()
        self._url = url
        self._current = current

    def run(self):
        try:
            with urllib.request.urlopen(self._url, timeout=10) as resp:
                data = json.loads(resp.read().decode('utf-8-sig'))
            remote_ver   = data.get("version", "0.0.0")
            download_url = data.get("download_url", "")
            notes        = data.get("notes", "")
            if _is_newer(remote_ver, self._current) and download_url:
                self.update_found.emit(self._current, remote_ver, notes, download_url)
        except Exception as e:
            print(f"[Güncelleme] Kontrol hatası: {e}")


# ─────────────────────────────────────────────────────────
# Ana kontrol fonksiyonu
# ─────────────────────────────────────────────────────────
def check_and_update(parent=None):
    """
    Arka planda versiyon kontrolü yapar (QThread + signal - tam thread-safe).
    Yeni sürüm varsa ana thread'de dialog gösterir.
    """
    try:
        import config
        url     = getattr(config, "UPDATE_CHECK_URL", "")
        enabled = getattr(config, "UPDATE_ENABLED", False)
        current = getattr(config, "APP_VERSION", "0.0.0")

        if not enabled or not url or url.startswith("https://GITHUB_KULLANICI"):
            return

        thread = _VersionCheckThread(url, current)

        def _on_update_found(cur, remote, notes, dl_url):
            dlg = UpdateDialog(cur, remote, notes, parent, has_download=bool(dl_url))
            if dlg.exec_() == QDialog.Accepted:
                if dl_url:
                    _do_update(parent, dl_url, remote)

        thread.update_found.connect(_on_update_found)
        # parent'e referans tutturarak GC'den korunur
        if parent is not None:
            parent._updater_thread = thread
        thread.start()

    except Exception as e:
        print(f"[Güncelleme] Başlatma hatası: {e}")


def _do_update(parent, download_url, new_ver):
    """Güncellemeyi indir ve uygula"""
    try:
        import shutil
        import time
        
        tmp_dir = tempfile.gettempdir()
        new_exe = os.path.join(tmp_dir, "Muhasebe_guncelleme.exe")
        log_path = os.path.join(tmp_dir, "_ozkaya_update_log.txt")
        
        # Log helper
        def log_msg(msg):
            try:
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
            except:
                pass

        dl_dlg = DownloadDialog(download_url, new_exe, parent)
        if dl_dlg.exec_() != QDialog.Accepted or not dl_dlg.result_path:
            log_msg("HATA: Download iptal edildi")
            return

        log_msg(f"INDIRME_OK: {new_exe}")
        log_msg(f"Dosya boyutu: {os.path.getsize(new_exe)} byte")

        if getattr(sys, "frozen", False):
            current_exe = sys.executable
            log_msg(f"CURRENT_EXE: {current_exe}")
            log_msg(f"CURRENT_PID: {os.getpid()}")
            
            QMessageBox.information(
                parent, "Güncelleme Hazır",
                f"✅ Sürüm {new_ver} indirildi!\n\n"
                "Uygulama şimdi kapanacak ve yeni sürüm otomatik başlayacak."
            )
            
            log_msg("MESSAGE_BOX_KAPATILDI")
            
            # Windows'ta kilitli dosyayı değiştirmek için PowerShell script kullan
            # PowerShell, batch'ten daha flexible ve error handling daha iyi
            
            ps_script = f"""
$old_exe = "{current_exe}"
$new_exe = "{new_exe}"

# 3 saniye bekle - Python process kapatılması için
Start-Sleep -Seconds 3

# Retry logic ile dosya silme
$retry_count = 0
while ($retry_count -lt 5) {{
    try {{
        if (Test-Path "$old_exe") {{
            Remove-Item "$old_exe" -Force -ErrorAction Stop
            break
        }}
        else {{
            break
        }}
    }}
    catch {{
        $retry_count++
        if ($retry_count -lt 5) {{
            Start-Sleep -Milliseconds 500
        }}
    }}
}}

# Yeni dosyayı taşı
$retry_count = 0
while ($retry_count -lt 5) {{
    try {{
        if (Test-Path "$new_exe") {{
            Move-Item "$new_exe" "$old_exe" -Force -ErrorAction Stop
            break
        }}
    }}
    catch {{
        $retry_count++
        if ($retry_count -lt 5) {{
            Start-Sleep -Milliseconds 500
        }}
    }}
}}

# Yeni programı başlat
if (Test-Path "$old_exe") {{
    & "$old_exe"
}}
"""
            
            ps_file = os.path.join(tmp_dir, "update_apply.ps1")
            try:
                with open(ps_file, 'w', encoding='utf-8') as f:
                    f.write(ps_script)
                log_msg(f"POWERSHELL_SCRIPT_OLUSTURULDU: {ps_file}")
            except Exception as e:
                log_msg(f"POWERSHELL_SCRIPT_OLUSTURMA_HATA: {str(e)}")
                QMessageBox.critical(parent, "HATA", f"Update script oluşturulamadı:\n{e}")
                return
            
            # PowerShell script'i başlat (parent process'ten completely bağımsız - detached)
            try:
                log_msg(f"POWERSHELL_SCRIPT_BASLANIYOR: {ps_file}")
                # Windows'ta CREATE_NEW_PROCESS_GROUP ile script parent'ten detach olur
                if sys.platform == "win32":
                    subprocess.Popen(
                        [
                            "powershell.exe",
                            "-NoProfile",
                            "-ExecutionPolicy", "Bypass",
                            "-File", ps_file
                        ],
                        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                else:
                    # Linux/Mac için (fallback)
                    subprocess.Popen(
                        ["pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ps_file],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                log_msg("POWERSHELL_SCRIPT_BASLATILDI_OK")
            except Exception as e:
                log_msg(f"POWERSHELL_SCRIPT_BASLATMA_HATA: {str(e)}")
                QMessageBox.critical(parent, "HATA", f"Update script başlatılamadı:\n{e}")
                return
            
            log_msg("UYGULAMADAN_CIKILIYOR")
            # Python process'ini kapat - PowerShell script parent'ten bağımsız olarak çalışacak
            os._exit(0)
        else:
            log_msg("SCRIPT_MODUNDA_CALISILIYOR")
            QMessageBox.information(
                parent, "Güncelleme İndirildi",
                f"✅ Yeni sürüm {new_ver} indirildi:\n{new_exe}\n\n"
                "Script modunda çalışıyorsunuz, EXE'yi manuel değiştirin."
            )

    except Exception as e:
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"[FINAL_EXCEPTION] {str(e)}\n")
        except:
            pass
        QMessageBox.critical(parent, "Güncelleme Hatası",
                             f"Güncelleme uygulanamadı:\n{e}")
