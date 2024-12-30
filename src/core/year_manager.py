import os
import sqlite3
from PyQt5.QtCore import QObject, pyqtSignal, QDate
from core.database import get_db_path
from core.logger import logger
from PyQt5.QtCore import QSettings

class YearManager(QObject):
    # Segnali per notificare i cambiamenti
    year_created = pyqtSignal(int)  # Emesso quando viene creato un nuovo anno
    year_changed = pyqtSignal(int)  # Emesso quando si cambia anno
    
    def __init__(self):
        super().__init__()
        self.MAX_YEAR = 2039
        
    def create_year_structure(self, year):
        """Crea la struttura completa per un nuovo anno"""
        try:
            if not isinstance(year, int) or year < 2000 or year > self.MAX_YEAR:
                raise ValueError(f"Anno non valido. Deve essere tra 2000 e {self.MAX_YEAR}")
            
            # Crea una data fittizia per l'anno
            dummy_date = QDate(year, 1, 1)
            base_path = os.path.dirname(get_db_path(dummy_date))
            
            # Crea la directory dell'anno
            os.makedirs(base_path, exist_ok=True)
            
            # Database necessari:
            required_dbs = {
                f"hemodos_{year}.db": [
                    '''CREATE TABLE IF NOT EXISTS annual_stats
                        (date text, total_donations integer, 
                         first_donations integer, completed_donations integer)''',
                    '''CREATE TABLE IF NOT EXISTS monthly_stats
                        (month integer, total_reservations integer, 
                         completed_donations integer, first_donations integer)'''
                ],
                f"date_donazione_{year}.db": [
                    '''CREATE TABLE IF NOT EXISTS donation_dates
                        (date text PRIMARY KEY)'''
                ],
                f"cronologia_{year}.db": [
                    '''CREATE TABLE IF NOT EXISTS history
                        (timestamp text, action text, details text)'''
                ]
            }
            
            # Crea i database giornalieri per tutto l'anno
            current_date = QDate(year, 1, 1)
            while current_date.year() == year:
                db_path = get_db_path(current_date)
                if not os.path.exists(db_path):
                    conn = sqlite3.connect(db_path)
                    c = conn.cursor()
                    c.execute('''CREATE TABLE IF NOT EXISTS reservations
                                (time text, name text, surname text, 
                                 first_donation boolean DEFAULT 0,
                                 stato text DEFAULT 'Non effettuata')''')
                    c.execute('''CREATE TABLE IF NOT EXISTS history
                                (timestamp text, action text, details text)''')
                    conn.commit()
                    conn.close()
                current_date = current_date.addDays(1)
            
            # Crea i database principali
            for db_name, tables in required_dbs.items():
                db_path = os.path.join(base_path, db_name)
                if not os.path.exists(db_path):
                    conn = sqlite3.connect(db_path)
                    c = conn.cursor()
                    for table_sql in tables:
                        c.execute(table_sql)
                    conn.commit()
                    conn.close()
            
            logger.info(f"Struttura per l'anno {year} creata con successo")
            self.year_created.emit(year)
            return True
            
        except Exception as e:
            logger.error(f"Errore nella creazione della struttura per l'anno {year}: {str(e)}")
            raise
    
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