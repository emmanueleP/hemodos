import logging
import os
from datetime import datetime

def setup_logger():
    """Configura il logger dell'applicazione"""
    # Crea la directory dei log se non esiste
    log_dir = os.path.expanduser("~/Documents/Hemodos/logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Nome del file di log con data
    log_file = os.path.join(log_dir, f"hemodos_{datetime.now().strftime('%Y%m%d')}.log")
    
    # Configurazione base
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    # Logger specifico per l'applicazione
    logger = logging.getLogger('hemodos')
    logger.setLevel(logging.INFO)
    
    return logger

# Logger globale
logger = setup_logger() 