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
        tmp_dir = tempfile.gettempdir()
        new_exe = os.path.join(tmp_dir, "Muhasebe_guncelleme.exe")

        dl_dlg = DownloadDialog(download_url, new_exe, parent)
        if dl_dlg.exec_() != QDialog.Accepted or not dl_dlg.result_path:
            return

        if getattr(sys, "frozen", False):
            current_exe = sys.executable
            current_pid = os.getpid()
            ps1_path = os.path.join(tmp_dir, "_ozkaya_update.ps1")
            log_path = os.path.join(tmp_dir, "_ozkaya_update_log.txt")

            # Basit ve robust PS1 script
            # UTF-8 BOM ile yazılacak, Türkçe karakterler düzgün olur
            ps1_content = (
                "$ErrorActionPreference = 'Continue'\n"
                f"$src = \"{new_exe}\"\n"
                f"$dst = \"{current_exe}\"\n"
                f"$log = \"{log_path}\"\n"
                f"$oldpid = {current_pid}\n"
                "\n"
                "function wlog($m) {\n"
                "    try {\n"
                "        $ts = (Get-Date -f 'HH:mm:ss')\n"
                "        [IO.File]::AppendAllText($log, \"[$ts] $m`r`n\")\n"
                "    } catch { }\n"
                "}\n"
                "\n"
                "# İlk log kaydı\n"
                "wlog 'UPDATE_BASLATILDI'\n"
                "\n"
                "# Eski process'in kapanmasını bekle\n"
                "$waited = 0\n"
                "while ((Get-Process -Id $oldpid -ErrorAction SilentlyContinue) -and ($waited -lt 30)) {\n"
                "    Start-Sleep -Milliseconds 500\n"
                "    $waited++\n"
                "}\n"
                "wlog 'OLP_PROCESS_BITTI_(waited_' $waited ')'\n"
                "\n"
                "Start-Sleep -Seconds 2\n"
                "\n"
                "# Kontrolleri yap\n"
                "if (-not (Test-Path $src -PathType Leaf)) {\n"
                "    wlog 'HATA_1_KAYNAK_DOSYA_YOK'\n"
                "    exit 1\n"
                "}\n"
                "\n"
                "wlog 'KAYNAK_DOSYA_KONTROL_OK'\n"
                "\n"
                "# Dosyayı oku\n"
                "try {\n"
                "    $bytes = [IO.File]::ReadAllBytes($src)\n"
                "    $size = $bytes.Length\n"
                "    wlog \"DOSYA_OKUNDU_size_$size\"\n"
                "} catch {\n"
                "    wlog \"HATA_2_OKUMA_$_\"\n"
                "    exit 1\n"
                "}\n"
                "\n"
                "# Kopyala (20 deneme)\n"
                "$ok = $false\n"
                "for ($i = 1; $i -le 20; $i++) {\n"
                "    try {\n"
                "        [IO.File]::WriteAllBytes($dst, $bytes)\n"
                "        $ok = $true\n"
                "        wlog \"KOPYALANDI_deneme_$i\"\n"
                "        break\n"
                "    } catch {\n"
                "        wlog \"DENEME_$i_HATA_$_\"\n"
                "        if ($i -lt 20) { Start-Sleep -Seconds 1 }\n"
                "    }\n"
                "}\n"
                "\n"
                "if ($ok) {\n"
                "    wlog 'BASLATILIYOR_YENİ_SURUM'\n"
                "    Start-Sleep -Seconds 1\n"
                "    try {\n"
                "        Start-Process $dst\n"
                "        wlog 'YENI_SURUM_BASLATILDI_OK'\n"
                "    } catch {\n"
                "        wlog \"HATA_3_BASLAT_$_\"\n"
                "    }\n"
                "} else {\n"
                "    wlog 'HATA_4_KOPYALAMA_20_DENEME_BASARISIZ'\n"
                "}\n"
                "\n"
                "# Temp dosyasını sil\n"
                "try {\n"
                "    Remove-Item $src -Force -ErrorAction SilentlyContinue\n"
                "    wlog 'TEMP_DOSYA_SILINDI'\n"
                "} catch { }\n"
                "\n"
                "wlog 'UPDATE_TAMAMLANDI'\n"
            )
            # UTF-8 BOM
            with open(ps1_path, "w", encoding="utf-8-sig") as f:
                f.write(ps1_content)

            QMessageBox.information(
                parent, "Güncelleme Hazır",
                f"✅ Sürüm {new_ver} indirildi!\n\n"
                "Uygulama şimdi kapanacak ve yeni sürüm otomatik başlayacak."
            )

            # Log dosyasını önceden create et (PS1'in yazabilmesi için)
            try:
                open(log_path, "w").close()
            except:
                pass
            
            # Windows START komutu ile PowerShell'i ayrı process'te başlat
            # START /B = detached (parent'ın kapanması child'i etkilemez)
            # START /MIN = pencereyi minimize
            # START /WAIT değil = async
            try:
                # shell=True ile cmd.exe'ye delegete et
                # Bu şekilde parent process çocuk processin başladığından emin olur
                cmd = f'START /B /MIN "" "{os.environ.get("SystemRoot", r"C:\Windows")}\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File "{ps1_path}"'
                
                # CREATE_NEW_PROCESS_GROUP: Child process'in kendi process grubu olur
                # stdin/stdout/stderr: None (silent)
                proc = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
                # Process tamamlanmasını bekleme - hemen exit et
                # shell=True ile subprocess.Popen çocuğu bağımsız hale getiriyor
            except Exception as e:
                msg = f"PowerShell hatası: {e}"
                QMessageBox.critical(parent, "HATA", msg)
                return
            
            os._exit(0)
        else:
            QMessageBox.information(
                parent, "Güncelleme İndirildi",
                f"✅ Yeni sürüm {new_ver} indirildi:\n{new_exe}\n\n"
                "Script modunda çalışıyorsunuz, EXE'yi manuel değiştirin."
            )

    except Exception as e:
        QMessageBox.critical(parent, "Güncelleme Hatası",
                             f"Güncelleme uygulanamadı:\n{e}")
