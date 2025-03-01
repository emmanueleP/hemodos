import os
import sys
import subprocess
import requests
import time
import xml.etree.ElementTree as ET
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from core.logger import logger
import platform

class SyncthingManager(QObject):
    sync_status_changed = pyqtSignal(str)  # Segnale per lo stato della sincronizzazione
    error_occurred = pyqtSignal(str)       # Segnale per gli errori

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.api_key = None
        self.syncthing_process = None
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.check_sync_status)
        self.base_url = "http://localhost:8384"
        
    def setup_syncthing(self):
        """Configura Syncthing per la prima volta"""
        try:
            # Crea la directory per i dati Hemodos
            hemodos_path = os.path.expanduser("~/Documents/Hemodos")
            os.makedirs(hemodos_path, exist_ok=True)
            
            # Avvia Syncthing se non è già in esecuzione
            if not self.is_syncthing_running():
                self.start_syncthing()
            
            # Configura la cartella Hemodos come cartella sincronizzata
            self.configure_folder(hemodos_path)
            
            # Avvia il monitoraggio dello stato
            self.status_timer.start(30000)  # Controlla ogni 30 secondi
            
            self.sync_status_changed.emit("Syncthing configurato e attivo")
            return True
            
        except Exception as e:
            logger.error(f"Errore nella configurazione di Syncthing: {str(e)}")
            self.error_occurred.emit(f"Errore nella configurazione: {str(e)}")
            return False

    def start_syncthing(self):
        """Avvia il processo Syncthing"""
        try:
            # Determina il percorso dell'eseguibile Syncthing
            if getattr(sys, 'frozen', False):
                # Se l'app è compilata, usa il binario incluso
                base_path = os.path.dirname(sys.executable)
                if platform.system() == "Windows":
                    syncthing_path = os.path.join(base_path, "syncthing.exe")
                else:
                    syncthing_path = os.path.join(base_path, "syncthing")
            else:
                # In sviluppo, usa il binario dalla cartella syncthing
                if platform.system() == "Windows":
                    syncthing_path = "syncthing/windows/syncthing.exe"
                elif platform.system() == "Darwin":
                    syncthing_path = "syncthing/macos/syncthing"
                else:
                    syncthing_path = "syncthing/linux/syncthing"
            
            # Avvia Syncthing in background
            self.syncthing_process = subprocess.Popen(
                [syncthing_path, "--no-browser", "--no-restart"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Attendi che Syncthing sia pronto
            time.sleep(2)
            
            # Ottieni l'API key
            self.get_api_key()
            
        except Exception as e:
            logger.error(f"Errore nell'avvio di Syncthing: {str(e)}")
            raise

    def get_api_key(self):
        """Ottiene l'API key di Syncthing"""
        try:
            config_path = os.path.expanduser("~/.config/syncthing/config.xml")
            if os.path.exists(config_path):
                tree = ET.parse(config_path)
                root = tree.getroot()
                self.api_key = root.find(".//apikey").text
        except Exception as e:
            logger.error(f"Errore nel recupero dell'API key: {str(e)}")
            raise

    def configure_folder(self, folder_path):
        """Configura una cartella per la sincronizzazione"""
        if not self.api_key:
            raise Exception("API key non disponibile")
            
        headers = {
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json'
        }
        
        data = {
            "id": "hemodos",
            "label": "Hemodos Data",
            "path": folder_path,
            "type": "sendreceive",
            "rescanIntervalS": 30,
            "fsWatcherEnabled": True,
            "fsWatcherDelayS": 10,
            "ignorePerms": False,
            "autoNormalize": True
        }
        
        response = requests.post(
            f"{self.base_url}/rest/config/folders",
            headers=headers,
            json=data
        )
        
        if response.status_code not in (200, 201):
            raise Exception(f"Errore nella configurazione della cartella: {response.text}")

    def check_sync_status(self):
        """Controlla lo stato della sincronizzazione"""
        try:
            if not self.api_key:
                return
                
            headers = {'X-API-Key': self.api_key}
            response = requests.get(f"{self.base_url}/rest/system/status", headers=headers)
            
            if response.status_code == 200:
                status = response.json()
                if status.get("state") == "syncing":
                    self.sync_status_changed.emit("Sincronizzazione in corso...")
                else:
                    self.sync_status_changed.emit("Sincronizzato")
                    
        except Exception as e:
            logger.error(f"Errore nel controllo dello stato: {str(e)}")

    def is_syncthing_running(self):
        """Verifica se Syncthing è in esecuzione"""
        try:
            response = requests.get(f"{self.base_url}/rest/system/ping")
            return response.status_code == 200
        except:
            return False

    def cleanup(self):
        """Pulisce le risorse"""
        self.status_timer.stop()
        if self.syncthing_process:
            self.syncthing_process.terminate()
            self.syncthing_process.wait()

    def get_status(self):
        """Ottiene lo stato attuale di Syncthing"""
        try:
            if not self.api_key:
                return {"state": "Non configurato"}
                
            headers = {'X-API-Key': self.api_key}
            response = requests.get(f"{self.base_url}/rest/system/status", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "state": data.get("state", "Sconosciuto"),
                    "uptime": data.get("uptime", 0),
                    "version": data.get("version", "")
                }
            return {"state": "Errore di connessione"}
            
        except Exception as e:
            logger.error(f"Errore nel recupero dello stato: {str(e)}")
            return {"state": "Errore"}

    def get_device_id(self):
        """Ottiene l'ID del dispositivo corrente"""
        try:
            if not self.api_key:
                return "Non disponibile"
                
            headers = {'X-API-Key': self.api_key}
            response = requests.get(f"{self.base_url}/rest/system/status", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("myID", "Non disponibile")
            return "Errore di connessione"
            
        except Exception as e:
            logger.error(f"Errore nel recupero dell'ID dispositivo: {str(e)}")
            return "Errore"

    def get_folder_path(self):
        """Ottiene il percorso della cartella sincronizzata"""
        try:
            if not self.api_key:
                return "Non configurato"
                
            headers = {'X-API-Key': self.api_key}
            response = requests.get(f"{self.base_url}/rest/config/folders", headers=headers)
            
            if response.status_code == 200:
                folders = response.json()
                for folder in folders:
                    if folder.get("id") == "hemodos":
                        return folder.get("path", "Non trovato")
            return "Errore di connessione"
            
        except Exception as e:
            logger.error(f"Errore nel recupero del percorso: {str(e)}")
            return "Errore"

    def add_device(self, device_id):
        """Aggiunge un nuovo dispositivo alla configurazione"""
        try:
            if not self.api_key:
                raise Exception("Syncthing non configurato")
                
            headers = {
                'X-API-Key': self.api_key,
                'Content-Type': 'application/json'
            }
            
            # Prepara i dati del dispositivo
            device_data = {
                "deviceID": device_id,
                "name": f"Hemodos Device {device_id[:7]}",
                "addresses": ["dynamic"],
                "compression": "metadata",
                "introducer": False,
                "skipIntroductionRemovals": False,
                "introducedBy": "",
                "paused": False,
                "allowedNetworks": [],
                "autoAcceptFolders": False,
                "maxSendKbps": 0,
                "maxRecvKbps": 0,
                "ignoredFolders": [],
                "pendingFolders": []
            }
            
            # Aggiungi il dispositivo
            response = requests.post(
                f"{self.base_url}/rest/config/devices",
                headers=headers,
                json=device_data
            )
            
            if response.status_code not in (200, 201):
                raise Exception(f"Errore nell'aggiunta del dispositivo: {response.text}")
                
            # Condividi la cartella Hemodos con il nuovo dispositivo
            self.share_folder_with_device(device_id)
            
        except Exception as e:
            logger.error(f"Errore nell'aggiunta del dispositivo: {str(e)}")
            raise

    def share_folder_with_device(self, device_id):
        """Condivide la cartella Hemodos con un dispositivo"""
        try:
            headers = {
                'X-API-Key': self.api_key,
                'Content-Type': 'application/json'
            }
            
            # Ottieni la configurazione attuale della cartella
            response = requests.get(
                f"{self.base_url}/rest/config/folders/hemodos",
                headers=headers
            )
            
            if response.status_code == 200:
                folder_config = response.json()
                # Aggiungi il nuovo dispositivo
                folder_config["devices"].append({
                    "deviceID": device_id,
                    "introducedBy": ""
                })
                
                # Aggiorna la configurazione
                update_response = requests.put(
                    f"{self.base_url}/rest/config/folders/hemodos",
                    headers=headers,
                    json=folder_config
                )
                
                if update_response.status_code not in (200, 201):
                    raise Exception(f"Errore nella condivisione della cartella: {update_response.text}")
                    
        except Exception as e:
            logger.error(f"Errore nella condivisione della cartella: {str(e)}")
            raise

    def restart(self):
        """Riavvia il servizio Syncthing"""
        try:
            if not self.api_key:
                raise Exception("Syncthing non configurato")
                
            headers = {'X-API-Key': self.api_key}
            response = requests.post(f"{self.base_url}/rest/system/restart", headers=headers)
            
            if response.status_code != 200:
                raise Exception("Errore nel riavvio di Syncthing")
                
            # Attendi che il servizio si riavvii
            time.sleep(5)
            self._update_syncthing_status()
            
        except Exception as e:
            logger.error(f"Errore nel riavvio di Syncthing: {str(e)}")
            raise 