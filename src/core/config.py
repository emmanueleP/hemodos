import json
import os
import platform
from pathlib import Path
from core.logger import logger
from core.constants import DEFAULT_PATHS

class Config:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """Carica la configurazione dal file config.json"""
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'config.json')
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
            logger.info("Configurazione caricata con successo")
        except Exception as e:
            logger.error(f"Errore nel caricamento della configurazione: {str(e)}")
            self._config = self._get_default_config()
    
    def _get_default_config(self):
        """Restituisce la configurazione predefinita"""
        return {
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "hemodos_db",
                "user": "admin",
                "password": "password",
                "backup_dir": "backups"
            },
            "app": {
                "debug": True,
                "log_level": "INFO",
                "autosave": {"enabled": True, "interval": 5},
                "cloud": {"service": "Locale", "sync_interval": 30}
            },
            "ui": {
                "theme": "dark",
                "primary_color": "#004d4d",
                "font": "SF Pro Display",
                "window": {
                    "width": 1024,
                    "height": 768,
                    "min_width": 800,
                    "min_height": 600
                }
            }
        }
    
    def get(self, key, default=None):
        """Ottiene un valore dalla configurazione"""
        try:
            keys = key.split('.')
            value = self._config
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            logger.warning(f"Chiave di configurazione non trovata: {key}")
            return default
    
    def set(self, key, value):
        """Imposta un valore nella configurazione"""
        try:
            keys = key.split('.')
            config = self._config
            for k in keys[:-1]:
                config = config[k]
            config[keys[-1]] = value
            self._save_config()
            logger.info(f"Configurazione aggiornata: {key} = {value}")
        except Exception as e:
            logger.error(f"Errore nell'aggiornamento della configurazione: {str(e)}")
    
    def _save_config(self):
        """Salva la configurazione su file"""
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'config.json')
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4)
            logger.info("Configurazione salvata con successo")
        except Exception as e:
            logger.error(f"Errore nel salvataggio della configurazione: {str(e)}")

    @staticmethod
    def get_app_data_dir():
        """Restituisce la directory per i dati dell'applicazione"""
        system = platform.system()
        if system == "Windows":
            return os.path.join(os.environ["APPDATA"], "Hemodos")
        elif system == "Darwin":  # macOS
            return os.path.join(str(Path.home()), "Library", "Application Support", "Hemodos")
        else:  # Linux e altri Unix
            return os.path.join(str(Path.home()), ".hemodos")

    @staticmethod
    def get_documents_dir():
        """Restituisce la directory Documenti"""
        system = platform.system()
        if system == "Windows":
            return os.path.join(os.path.expanduser("~"), "Documents")
        elif system == "Darwin":
            return os.path.join(str(Path.home()), "Documents")
        else:
            return os.path.join(str(Path.home()), "Documents")

    @staticmethod
    def get_syncthing_config():
        """Restituisce la configurazione di Syncthing per il sistema"""
        system = platform.system()
        if system == "Windows":
            return {
                "binary": "syncthing.exe",
                "config_dir": os.path.join(os.environ["APPDATA"], "Syncthing")
            }
        elif system == "Darwin":
            return {
                "binary": "syncthing",
                "config_dir": os.path.join(str(Path.home()), "Library", "Application Support", "Syncthing")
            }
        else:
            return {
                "binary": "syncthing",
                "config_dir": os.path.join(str(Path.home()), ".config", "syncthing")
            } 