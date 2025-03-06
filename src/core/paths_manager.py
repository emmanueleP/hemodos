import os
import sys
import platform
from PyQt5.QtCore import QSettings

class PathsManager:
    def __init__(self):
        self.is_macos = platform.system() == 'Darwin'
        self.is_frozen = getattr(sys, 'frozen', False)
        self._init_paths()
        
    def _init_paths(self):
        """Inizializza i percorsi base dell'applicazione"""
        if self.is_frozen:
            if self.is_macos:
                # In macOS, quando frozen, il bundle è in .app/Contents/MacOS/
                self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(sys._MEIPASS)))
                self.resources_path = os.path.join(self.base_path, 'Contents', 'Resources')
            else:
                self.base_path = os.path.dirname(sys.executable)
                self.resources_path = sys._MEIPASS
        else:
            # In development
            self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            self.resources_path = os.path.join(self.base_path, 'resources')
            
    def get_asset_path(self, *paths):
        """
        Restituisce il percorso completo di un asset
        
        Args:
            *paths: parti del percorso da unire al percorso base delle risorse
            
        Returns:
            str: percorso completo dell'asset
        """
        return os.path.join(self.resources_path, *paths)
        
    def get_config_path(self):
        """Restituisce il percorso della directory di configurazione"""
        if self.is_macos:
            # Usa ~/Library/Application Support per le configurazioni su macOS
            return os.path.expanduser("~/Library/Application Support/Hemodos")
        else:
            # Su altri sistemi usa la directory dell'applicazione
            return os.path.join(self.base_path, 'config')
            
    def get_logs_path(self):
        """Restituisce il percorso della directory dei log"""
        if self.is_macos:
            # Usa ~/Library/Logs per i log su macOS
            logs_dir = os.path.expanduser("~/Library/Logs/Hemodos")
        else:
            logs_dir = os.path.join(self.base_path, 'logs')
            
        os.makedirs(logs_dir, exist_ok=True)
        return logs_dir
        
    def get_database_path(self):
        """Restituisce il percorso del database"""
        if self.is_macos:
            # Usa ~/Library/Application Support per il database su macOS
            db_dir = os.path.expanduser("~/Library/Application Support/Hemodos/db")
        else:
            db_dir = os.path.join(self.base_path, 'db')
            
        os.makedirs(db_dir, exist_ok=True)
        return os.path.join(db_dir, 'hemodos.db')

    def get_cloud_path(self):
        """Restituisce il percorso del cloud configurato"""
        settings = QSettings('Hemodos', 'DatabaseSettings')
        return settings.value("cloud_path")
        
    def is_auto_sync_enabled(self):
        """Verifica se il salvataggio automatico è attivo"""
        settings = QSettings('Hemodos', 'DatabaseSettings')
        return settings.value("auto_sync", False, type=bool) 