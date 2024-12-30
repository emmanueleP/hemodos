from PyQt5.QtCore import QThread, pyqtSignal
from core.database import get_reservations, init_db, get_db_path
import os
from datetime import datetime
from core.logger import logger

class DatabaseCache:
    """Cache per i dati del database"""
    _instance = None
    _cache = {}
    _max_size = 10  # Numero massimo di date in cache
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = DatabaseCache()
        return cls._instance
    
    def get(self, date_key):
        """Ottiene i dati dalla cache"""
        return self._cache.get(date_key)
    
    def set(self, date_key, data):
        """Salva i dati in cache"""
        # Rimuovi elementi vecchi se la cache è piena
        if len(self._cache) >= self._max_size:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        self._cache[date_key] = data
    
    def clear(self):
        """Pulisce la cache"""
        self._cache.clear()

class DatabaseLoader(QThread):
    loading_started = pyqtSignal()
    loading_finished = pyqtSignal(list)
    loading_error = pyqtSignal(str)
    progress_updated = pyqtSignal(int)
    
    def __init__(self, selected_date):
        super().__init__()
        self.selected_date = selected_date
        self.cache = DatabaseCache.get_instance()
        
    def run(self):
        try:
            self.loading_started.emit()
            self.progress_updated.emit(10)
            
            # Verifica se i dati sono in cache
            date_key = self.selected_date.toString("yyyy-MM-dd")
            cached_data = self.cache.get(date_key)
            
            if cached_data:
                logger.info(f"Dati recuperati dalla cache per {date_key}")
                self.progress_updated.emit(90)
                self.loading_finished.emit(cached_data)
                self.progress_updated.emit(100)
                return
            
            # Se non in cache, carica dal database
            db_path = get_db_path(self.selected_date)
            if not os.path.exists(db_path):
                self.progress_updated.emit(30)
                init_db(specific_date=self.selected_date)
            
            self.progress_updated.emit(60)
            
            # Carica le prenotazioni
            reservations = get_reservations(self.selected_date)
            
            # Salva in cache
            self.cache.set(date_key, reservations)
            
            self.progress_updated.emit(90)
            self.loading_finished.emit(reservations)
            self.progress_updated.emit(100)
            
        except Exception as e:
            logger.error(f"Errore nel caricamento del database: {str(e)}")
            self.loading_error.emit(str(e))
