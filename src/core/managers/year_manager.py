from PyQt5.QtCore import QObject, QSettings, pyqtSignal
import os
from datetime import datetime
from core.database import get_db_path
from core.logger import logger

class YearManager(QObject):
    # Segnali
    year_created = pyqtSignal(int)  # Emesso quando viene creato un nuovo anno
    year_changed = pyqtSignal(int)  # Emesso quando si cambia anno

    def __init__(self):
        super().__init__()
        self.settings = QSettings('Hemodos', 'DatabaseSettings')

    def create_year_structure(self, year):
        """Crea la struttura dell'anno con tutti i database necessari"""
        try:
            # Ottieni il percorso base (Hemodos)
            settings = QSettings('Hemodos', 'DatabaseSettings')
            service = settings.value("cloud_service", "Locale")
            
            if service == "Locale":
                base_path = os.path.expanduser("~/Documents/Hemodos")
            else:
                cloud_path = settings.value("cloud_path", "")
                base_path = os.path.join(cloud_path, "Hemodos")
            
            # Crea la directory dell'anno
            year_path = os.path.join(base_path, str(year))
            os.makedirs(year_path, exist_ok=True)
            
            # Crea i database annuali
            databases = [
                f"hemodos_{year}.db",           # Database principale
                f"cronologia_{year}.db",        # Database cronologia
                f"date_donazione_{year}.db",    # Database date donazioni
                f"statistiche_{year}.db"        # Database statistiche
            ]
            
            for db_name in databases:
                db_path = os.path.join(year_path, db_name)
                if not os.path.exists(db_path):
                    from core.database import get_db_connection
                    with get_db_connection(db_path) as conn:
                        conn.commit()
                    logger.info(f"Creato database: {db_path}")
            
            # Emetti il segnale di creazione anno
            self.year_created.emit(year)
            logger.info(f"Struttura anno {year} creata con successo")
            return True
            
        except Exception as e:
            logger.error(f"Errore nella creazione della struttura anno {year}: {str(e)}")
            return False

    def handle_year_change(self, date):
        """Gestisce il cambio di anno"""
        try:
            year = date.year()
            current_year = self.settings.value("current_year", datetime.now().year)
            
            if year != current_year:
                # Crea la struttura del nuovo anno se non esiste
                if not os.path.exists(os.path.join(os.path.dirname(get_db_path()), str(year))):
                    if not self.create_year_structure(year):
                        return False
                
                self.settings.setValue("current_year", year)
                logger.info(f"Anno cambiato da {current_year} a {year}")
            
            return True
            
        except Exception as e:
            logger.error(f"Errore nel cambio anno: {str(e)}")
            return False 