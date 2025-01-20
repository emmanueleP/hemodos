import os
import sys
import requests
import tempfile
import subprocess
from PyQt5.QtCore import QThread, pyqtSignal
from core.logger import logger

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
            # Crea una directory temporanea per il download
            temp_dir = tempfile.mkdtemp()
            installer_path = os.path.join(temp_dir, "Hemodos_Setup.exe")

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

            # Prepara il comando per l'installazione silenziosa
            install_cmd = f'"{installer_path}" /VERYSILENT /NORESTART /CLOSEAPPLICATIONS'

            # Crea un file batch per eseguire l'installazione dopo la chiusura dell'app
            batch_path = os.path.join(temp_dir, "install.bat")
            with open(batch_path, 'w') as f:
                f.write(f'''@echo off
timeout /t 2 /nobreak
{install_cmd}
del "{installer_path}"
del "%~f0"
''')

            # Avvia il batch file in modo nascosto
            logger.info("Avvio installazione")
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.Popen(['cmd', '/c', batch_path], 
                           startupinfo=startupinfo,
                           creationflags=subprocess.CREATE_NO_WINDOW)

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
        # Crea e avvia il thread di installazione
        installer = InstallerThread(download_url)
        
        # Connetti i segnali alla finestra principale se presente
        if parent:
            installer.download_progress.connect(parent.status_manager.show_message)
            installer.installation_complete.connect(lambda: parent.close())
            installer.installation_error.connect(
                lambda msg: parent.status_manager.show_message(f"Errore: {msg}", 5000)
            )
        
        # Avvia il thread
        installer.start()
        
        return installer
        
    except Exception as e:
        error_msg = f"Errore nell'avvio dell'installazione: {str(e)}"
        logger.error(error_msg)
        if parent:
            parent.status_manager.show_message(error_msg, 5000)
        return None 