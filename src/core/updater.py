import requests
import os
import json
from PyQt5.QtCore import QThread, pyqtSignal, QSettings
from core.logger import logger
from core.exceptions import UpdateError

class UpdateChecker(QThread):
    update_available = pyqtSignal(str, str, str)  # version, release_notes, download_url
    error_occurred = pyqtSignal(str)
    
    def __init__(self, current_version):
        super().__init__()
        self.current_version = current_version
        self.base_url = "https://api.github.com"
        self.owner = "emmanueleP"
        self.repo = "hemodos"
        
    def run(self):
        try:
            headers = {
                'Accept': 'application/vnd.github+json',
                'X-GitHub-Api-Version': '2022-11-28'
            }
            
            # Prima ottieni l'ultimo release
            releases_url = f"{self.base_url}/repos/{self.owner}/{self.repo}/releases"
            response = requests.get(releases_url, headers=headers)
            response.raise_for_status()
            
            releases = response.json()
            if not releases:
                logger.info("Nessun release trovato")
                return
                
            latest_release = releases[0]  # Il primo è il più recente
            latest_version = latest_release['tag_name'].lstrip('v')
            
            # Controlla se la versione più recente è diversa da quella corrente
            if latest_version != self.current_version:
                # Controlla se c'è una versione più recente
                if self._compare_versions(latest_version, self.current_version) > 0:
                    # Ottieni l'asset dell'installer
                    assets = latest_release['assets']
                    installer_asset = next(
                        (asset for asset in assets if asset['name'].endswith('.exe')), 
                        None
                    )
                    
                    if installer_asset:
                        download_url = installer_asset['browser_download_url']
                        self.update_available.emit(
                            latest_version,
                            latest_release['body'],  # Release notes
                            download_url
                        )
                        logger.info(f"Nuova versione disponibile: {latest_version}")
                        
                        # Aggiungi alla cronologia degli aggiornamenti
                        self.add_to_update_history(latest_version, latest_release['published_at'])
                    else:
                        raise UpdateError("Installer non trovato nel release")
                else:
                    logger.info(f"Versione corrente ({self.current_version}) è aggiornata")
            
        except Exception as e:
            error_msg = f"Errore nel controllo aggiornamenti: {str(e)}"
            self.error_occurred.emit(error_msg)
            logger.error(error_msg)
    
    def add_to_update_history(self, version, date):
        """Aggiunge un entry alla cronologia degli aggiornamenti"""
        try:
            settings = QSettings('Hemodos', 'DatabaseSettings')
            history = settings.value("update_history", [])
            
            # Aggiungi la nuova entry
            history.append({
                'version': version,
                'date': date,
                'status': 'available'
            })
            
            # Mantieni solo le ultime 10 entry
            if len(history) > 10:
                history = history[-10:]
            
            settings.setValue("update_history", history)
            
        except Exception as e:
            logger.error(f"Errore nel salvare la cronologia aggiornamenti: {str(e)}")
    
    def _compare_versions(self, version1, version2):
        """Confronta due versioni. Ritorna 1 se version1 > version2, -1 se version1 < version2, 0 se uguali"""
        v1_parts = [int(x) for x in version1.split('.')]
        v2_parts = [int(x) for x in version2.split('.')]
        
        for i in range(max(len(v1_parts), len(v2_parts))):
            v1 = v1_parts[i] if i < len(v1_parts) else 0
            v2 = v2_parts[i] if i < len(v2_parts) else 0
            
            if v1 > v2:
                return 1
            elif v1 < v2:
                return -1
        return 0

class Updater(QThread):
    update_progress = pyqtSignal(int)  # percentuale di progresso
    update_completed = pyqtSignal()
    update_error = pyqtSignal(str)
    
    def __init__(self, download_url):
        super().__init__()
        self.download_url = download_url
        
    def run(self):
        try:
            # Scarica il nuovo installer
            response = requests.get(self.download_url, stream=True)
            response.raise_for_status()
            
            # Ottieni la dimensione totale del file
            total_size = int(response.headers.get('content-length', 0))
            
            # Prepara il percorso di download
            download_path = os.path.join(os.path.expanduser("~/Downloads"), "Hemodos_Setup.exe")
            
            # Scarica il file mostrando il progresso
            with open(download_path, 'wb') as f:
                if total_size == 0:
                    f.write(response.content)
                else:
                    downloaded = 0
                    for data in response.iter_content(chunk_size=4096):
                        downloaded += len(data)
                        f.write(data)
                        progress = int((downloaded / total_size) * 100)
                        self.update_progress.emit(progress)
            
            # Avvia l'installer automaticamente
            os.startfile(download_path)
            self.update_completed.emit()
            
        except Exception as e:
            error_msg = f"Errore durante l'aggiornamento: {str(e)}"
            self.update_error.emit(error_msg)
            logger.error(error_msg) 