import os
import shutil
from PyQt5.QtCore import QSettings
from core.logger import logger

def get_base_path():
    """Ottiene il percorso base dei database"""
    settings = QSettings('Hemodos', 'DatabaseSettings')
    service = settings.value("cloud_service", "Locale")
    
    if service == "Locale":
        return os.path.expanduser("~/Documents/Hemodos")
    else:
        cloud_path = settings.value("cloud_path", "")
        return os.path.join(cloud_path, "Hemodos")

def delete_year_directory(year):
    """Elimina l'intera directory di un anno"""
    try:
        base_path = get_base_path()
        year_path = os.path.join(base_path, str(year))
        
        if os.path.exists(year_path):
            # Elimina l'intera directory e tutto il suo contenuto
            shutil.rmtree(year_path)
            logger.info(f"Directory dell'anno {year} eliminata con successo")
            return True
        else:
            logger.warning(f"Directory dell'anno {year} non trovata")
            return False
            
    except Exception as e:
        logger.error(f"Errore nell'eliminazione della directory dell'anno {year}: {str(e)}")
        raise

def get_available_years():
    """Ottiene la lista degli anni disponibili"""
    try:
        base_path = get_base_path()
        if not os.path.exists(base_path):
            return []
            
        years = []
        for item in os.listdir(base_path):
            if os.path.isdir(os.path.join(base_path, item)):
                try:
                    year = int(item)
                    years.append(year)
                except ValueError:
                    continue
                    
        return sorted(years, reverse=True)
        
    except Exception as e:
        logger.error(f"Errore nel recupero degli anni disponibili: {str(e)}")
        return [] 