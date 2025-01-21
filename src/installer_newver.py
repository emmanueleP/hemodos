import os
import sys
import requests
import tempfile
import subprocess
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton
from core.logger import logger

class DownloadDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Download Aggiornamento")
        self.setFixedSize(400, 150)
        
        layout = QVBoxLayout()
        
        # Label informativa
        self.info_label = QLabel("Download dell'aggiornamento in corso...")
        layout.addWidget(self.info_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)

    def update_progress(self, value):
        self.progress_bar.setValue(value)
        if value == 100:
            self.info_label.setText("Download completato. L'applicazione verrà riavviata...")

class InstallerThread(QThread):
    download_progress = pyqtSignal(int)  # Segnale per il progresso del download
    installation_complete = pyqtSignal()  # Segnale per installazione completata
    installation_error = pyqtSignal(str)  # Segnale per errori

    def __init__(self, download_url):
        super().__init__()
        self.download_url = download_url
        self.is_running = True

    def run(self):
        """Esegue il download e l'installazione"""
        try:
            # Crea la cartella downloads se non esiste
            downloads_dir = os.path.expanduser("~/Downloads/Hemodos")
            os.makedirs(downloads_dir, exist_ok=True)
            
            # Percorso del nuovo installer
            installer_path = os.path.join(downloads_dir, "Hemodos_Setup_New.exe")
            
            # Download del file
            logger.info(f"Avvio download da: {self.download_url}")
            response = requests.get(self.download_url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            
            if total_size == 0:
                raise Exception("Impossibile determinare la dimensione del file")

            # Scarica il file mostrando il progresso
            downloaded = 0
            with open(installer_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if not self.is_running:
                        logger.info("Download interrotto dall'utente")
                        return
                    if chunk:
                        downloaded += len(chunk)
                        f.write(chunk)
                        progress = int((downloaded / total_size) * 100)
                        self.download_progress.emit(progress)

            logger.info("Download completato")
            
            # Attendi un secondo per mostrare il 100%
            self.sleep(1)
            
            # Avvia il nuovo installer
            logger.info("Avvio nuovo installer")
            subprocess.Popen([installer_path], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
            
            # Emetti il segnale di completamento
            self.installation_complete.emit()

        except Exception as e:
            error_msg = f"Errore durante l'aggiornamento: {str(e)}"
            logger.error(error_msg)
            self.installation_error.emit(error_msg)

    def stop(self):
        """Ferma il download"""
        self.is_running = False
        self.wait()


def install_update(download_url, parent=None):
    """Funzione principale per gestire l'installazione dell'aggiornamento"""
    try:
        # Crea il dialog di download
        download_dialog = DownloadDialog(parent)
        
        # Crea e avvia il thread di installazione
        installer = InstallerThread(download_url)
        
        # Connetti i segnali
        installer.download_progress.connect(download_dialog.update_progress)
        installer.installation_complete.connect(parent.close)
        installer.installation_error.connect(
            lambda msg: parent.status_manager.show_message(f"Errore: {msg}", 5000)
        )
        
        # Mostra il dialog e avvia il download
        download_dialog.show()
        installer.start()
        
        return installer
        
    except Exception as e:
        error_msg = f"Errore nell'avvio dell'installazione: {str(e)}"
        logger.error(error_msg)
        if parent:
            parent.status_manager.show_message(error_msg, 5000)
        return None 