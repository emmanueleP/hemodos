import os
import sqlite3
from PyQt5.QtCore import QObject, pyqtSignal
from core.database import get_db_path
from core.logger import logger
from PyQt5.QtCore import QSettings

class YearManager(QObject):
    # Segnali per notificare i cambiamenti
    year_created = pyqtSignal(int)  # Emesso quando viene creato un nuovo anno
    year_changed = pyqtSignal(int)  # Emesso quando si cambia anno
    
    def __init__(self):
        super().__init__()
        
    def create_year_structure(self, year):
        """Crea la struttura completa per un nuovo anno"""
        try:
            # Ottieni il percorso base (Locale o Cloud)/Hemodos
            settings = QSettings('Hemodos', 'DatabaseSettings')
            service = settings.value("cloud_service", "Locale")
            
            if service == "Locale":
                base_path = os.path.expanduser("~/Documents/Hemodos")
            else:
                cloud_path = settings.value("cloud_path", "")
                base_path = os.path.join(cloud_path, "Hemodos")
            
            # Crea la directory dell'anno dentro Hemodos
            year_path = os.path.join(base_path, str(year))
            os.makedirs(year_path, exist_ok=True)
            
            # Crea i database necessari
            self._create_main_db(year_path, year)
            self._create_dates_db(year_path, year)
            self._create_history_db(year_path, year)
            self._create_stats_db(year_path, year)
            
            # Emetti il segnale di creazione anno
            self.year_created.emit(year)
            logger.info(f"Creata struttura per l'anno {year}")
            return True
            
        except Exception as e:
            logger.error(f"Errore nella creazione dell'anno {year}: {str(e)}")
            raise
    
    def _create_main_db(self, year_path, year):
        db_path = os.path.join(year_path, f"hemodos_{year}.db")
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS annual_stats
                     (date text, total_donations integer, 
                      first_donations integer, completed_donations integer)''')
        conn.commit()
        conn.close()
    
    def _create_dates_db(self, year_path, year):
        dates_path = os.path.join(year_path, f"date_donazione_{year}.db")
        conn = sqlite3.connect(dates_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS donation_dates
                     (year integer, date text)''')
        conn.commit()
        conn.close()
    
    def _create_history_db(self, year_path, year):
        history_path = os.path.join(year_path, f"cronologia_{year}.db")
        conn = sqlite3.connect(history_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS history
                     (timestamp text, action text, details text)''')
        conn.commit()
        conn.close()
    
    def _create_stats_db(self, year_path, year):
        stats_path = os.path.join(year_path, f"statistiche_{year}.db")
        conn = sqlite3.connect(stats_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS monthly_stats
                     (month integer, total_reservations integer, 
                      completed_donations integer, first_donations integer)''')
        conn.commit()
        conn.close()
    
    def get_available_years(self):
        """Ottiene la lista degli anni disponibili"""
        base_path = os.path.dirname(get_db_path())
        years = set()
        
        if os.path.exists(base_path):
            for filename in os.listdir(base_path):
                if os.path.isdir(os.path.join(base_path, filename)):
                    try:
                        year = int(filename)
                        years.add(year)
                    except ValueError:
                        continue
        
        return sorted(list(years), reverse=True) 
    
    def get_year_paths(self, year):
        """Ottiene i percorsi dei file per un anno specifico"""
        settings = QSettings('Hemodos', 'DatabaseSettings')
        service = settings.value("cloud_service", "Locale")
        
        if service == "Locale":
            base_path = os.path.expanduser("~/Documents/Hemodos")
        else:
            cloud_path = settings.value("cloud_path", "")
            base_path = os.path.join(cloud_path, "Hemodos")
        
        year_path = os.path.join(base_path, str(year))
        
        return {
            'base': base_path,
            'year': year_path,
            'main': os.path.join(year_path, f"hemodos_{year}.db"),
            'dates': os.path.join(year_path, f"date_donazione_{year}.db"),
            'history': os.path.join(year_path, f"cronologia_{year}.db"),
            'stats': os.path.join(year_path, f"statistiche_{year}.db"),
            'daily': lambda day, month: os.path.join(year_path, f"prenotazioni_{day:02d}_{month:02d}.db")
        } 