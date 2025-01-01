import sqlite3
from datetime import datetime, timedelta
import os
from PyQt5.QtCore import QSettings, QThread, pyqtSignal, QDate
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from core.logger import logger
import time
from core.delete_db_logic import get_base_path

def get_db_path(specific_date=None, is_donation_dates=False):
    """Ottiene il percorso del database corretto
    
    Args:
        specific_date: Data specifica (QDate)
        is_donation_dates: Se True, restituisce il percorso del database delle date di donazione
    """
    settings = QSettings('Hemodos', 'DatabaseSettings')
    service = settings.value("cloud_service", "Locale")
    
    if service == "Locale":
        base_path = os.path.expanduser("~/Documents/Hemodos")
    else:
        cloud_path = settings.value("cloud_path", "")
        base_path = os.path.join(cloud_path, "Hemodos")
    
    if specific_date:
        year = specific_date.year()
        year_path = os.path.join(base_path, str(year))
        os.makedirs(year_path, exist_ok=True)
        
        if is_donation_dates:
            return os.path.join(year_path, f"date_donazione_{year}.db")
        else:
            db_name = f"prenotazioni_{specific_date.day():02d}_{specific_date.month():02d}.db"
            return os.path.join(year_path, db_name)
    else:
        # Restituisci l'ultimo database usato o quello dell'anno corrente
        last_db = settings.value("last_database")
        if last_db and os.path.exists(last_db):
            return last_db
        
        year = QDate.currentDate().year()
        return os.path.join(base_path, str(year), f"hemodos_{year}.db")

def migrate_database():
    """Aggiorna la struttura del database se necessario"""
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Verifica se la colonna stato esiste
        cursor = c.execute('PRAGMA table_info(reservations)')
        columns = [column[1] for column in cursor.fetchall()]
        
        # Aggiungi la colonna stato se non esiste
        if 'stato' not in columns:
            c.execute('ALTER TABLE reservations ADD COLUMN stato text DEFAULT "Non effettuata"')
            logger.info("Aggiunta colonna stato alla tabella reservations")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Errore nella migrazione del database: {str(e)}")
        return False

def init_db(specific_date=None):
    """Inizializza il database con struttura ottimizzata per grandi quantità di dati"""
    try:
        # Inizializza il database giornaliero
        db_path = get_db_path(specific_date=specific_date)
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        with get_db_connection(db_path) as conn:
            c = conn.cursor()
            
            # Crea le tabelle con indici appropriati
            c.executescript('''
                CREATE TABLE IF NOT EXISTS reservations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    time TEXT NOT NULL,
                    name TEXT,
                    surname TEXT,
                    first_donation BOOLEAN DEFAULT 0,
                    stato TEXT DEFAULT 'Non effettuata',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_reservations_time ON reservations(time);
                CREATE INDEX IF NOT EXISTS idx_reservations_name ON reservations(name, surname);
                CREATE INDEX IF NOT EXISTS idx_reservations_stato ON reservations(stato);
                
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    action TEXT NOT NULL,
                    details TEXT,
                    user TEXT
                );
                
                CREATE INDEX IF NOT EXISTS idx_history_timestamp ON history(timestamp);
                CREATE INDEX IF NOT EXISTS idx_history_action ON history(action);
            ''')
            
            # Trigger per aggiornare updated_at
            c.execute('''
                CREATE TRIGGER IF NOT EXISTS update_timestamp 
                AFTER UPDATE ON reservations
                BEGIN
                    UPDATE reservations SET updated_at = CURRENT_TIMESTAMP 
                    WHERE id = NEW.id;
                END;
            ''')
            
        # Inizializza anche il database annuale con struttura ottimizzata
        year_db_path = os.path.join(os.path.dirname(db_path), f"hemodos_{datetime.now().year}.db")
        
        with get_db_connection(year_db_path) as conn:
            c = conn.cursor()
            
            c.executescript('''
                CREATE TABLE IF NOT EXISTS annual_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    total_donations INTEGER DEFAULT 0,
                    first_donations INTEGER DEFAULT 0,
                    completed_donations INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE UNIQUE INDEX IF NOT EXISTS idx_annual_stats_date ON annual_stats(date);
                
                CREATE TABLE IF NOT EXISTS monthly_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    year INTEGER NOT NULL,
                    month INTEGER NOT NULL,
                    total_reservations INTEGER DEFAULT 0,
                    completed_donations INTEGER DEFAULT 0,
                    first_donations INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(year, month)
                );
                
                CREATE INDEX IF NOT EXISTS idx_monthly_stats_date ON monthly_stats(year, month);
            ''')
            
        logger.info(f"Database inizializzato con struttura ottimizzata: {db_path}")
        return True
        
    except Exception as e:
        logger.error(f"Errore durante l'inizializzazione del database: {str(e)}")
        raise

def get_history_db_path(year=None):
    """Ottiene il percorso del database della cronologia per l'anno specificato"""
    if year is None:
        year = datetime.now().year
    
    base_path = os.path.dirname(get_db_path())
    return os.path.join(base_path, f"cronologia_{year}.db")

def add_history_entry(action, details, specific_date=None):
    """Aggiunge un'entrata nella cronologia"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        year = specific_date.year() if isinstance(specific_date, QDate) else datetime.now().year
        
        history_db = get_history_db_path(year)
        os.makedirs(os.path.dirname(history_db), exist_ok=True)
        
        with get_db_connection(history_db) as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS history
                         (timestamp text, action text, details text)''')
            c.execute("INSERT INTO history VALUES (?, ?, ?)", 
                     (timestamp, action, details))
            conn.commit()
            
    except Exception as e:
        logger.error(f"Errore nell'aggiunta alla cronologia: {str(e)}")

def get_history(year=None):
    """Recupera la cronologia"""
    try:
        if year is None:
            year = datetime.now().year
            
        history_db = get_history_db_path(year)
        if not os.path.exists(history_db):
            return []
            
        with get_db_connection(history_db) as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS history
                         (timestamp text, action text, details text)''')
            c.execute("SELECT timestamp, action, details FROM history ORDER BY timestamp DESC")
            return c.fetchall()
            
    except Exception as e:
        logger.error(f"Errore nel recupero della cronologia: {str(e)}")
        return []

def add_reservation(date, time, name, surname, first_donation):
    """Aggiunge o aggiorna una prenotazione nel database"""
    try:
        if isinstance(date, str):
            date_obj = QDate.fromString(date, "yyyy-MM-dd")
        else:
            date_obj = date
            
        db_path = get_db_path(date_obj)
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        with get_db_connection(db_path) as conn:
            c = conn.cursor()
            
            # Crea le tabelle se non esistono
            c.executescript('''
                CREATE TABLE IF NOT EXISTS reservations
                    (time text PRIMARY KEY, name text, surname text, 
                     first_donation boolean DEFAULT 0, 
                     stato text DEFAULT 'Non effettuata');
            ''')
            
            # Verifica se esiste già una prenotazione per questo orario
            c.execute("SELECT name, surname, stato FROM reservations WHERE time=?", (time,))
            result = c.fetchone()
            
            if result:
                old_name, old_surname, current_status = result
                # Aggiungi alla cronologia solo se c'è un cambiamento e i campi non sono vuoti
                if ((old_name != name or old_surname != surname) and 
                    (name.strip() or surname.strip() or old_name.strip() or old_surname.strip())):
                    details = f"Data: {date_obj.toString('yyyy-MM-dd')}, Ora: {time}\n"
                    if old_name or old_surname:
                        details += f"Da: {old_name} {old_surname} -> "
                    details += f"A: {name} {surname}"
                    add_history_entry("Modifica prenotazione", details, specific_date=date_obj)
            else:
                # Nuova prenotazione - aggiungi alla cronologia solo se non è vuota
                if name.strip() or surname.strip():
                    details = f"Data: {date_obj.toString('yyyy-MM-dd')}, Ora: {time}, Nome: {name} {surname}"
                    add_history_entry("Nuova prenotazione", details, specific_date=date_obj)
            
            # Inserisci o aggiorna la prenotazione
            c.execute("""INSERT OR REPLACE INTO reservations 
                         (time, name, surname, first_donation, stato) 
                         VALUES (?,?,?,?,?)""", 
                      (time, name, surname, first_donation, 
                       current_status if result else 'Non effettuata'))
            
            conn.commit()
            
        return True
        
    except Exception as e:
        logger.error(f"Errore nel salvataggio della prenotazione: {str(e)}")
        return False

def get_db_connection(db_path):
    """Crea una connessione al database con impostazioni ottimizzate per grandi dataset"""
    conn = sqlite3.connect(db_path)
    
    # Configurazioni per prestazioni ottimali
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA temp_store=MEMORY")
    conn.execute("PRAGMA cache_size=10000")
    conn.execute("PRAGMA page_size=4096")
    conn.execute("PRAGMA mmap_size=30000000000")
    conn.execute("PRAGMA busy_timeout=60000")
    conn.execute("PRAGMA foreign_keys=ON")
    
    # Abilita il supporto alle foreign keys
    conn.execute("PRAGMA foreign_keys=ON")
    
    # Ottimizza le query
    conn.execute("PRAGMA optimize")
    
    return conn

def get_reservations(selected_date):
    """Ottiene le prenotazioni per una data specifica"""
    try:
        db_path = get_db_path(selected_date)
        if not os.path.exists(db_path):
            return []
            
        with get_db_connection(db_path) as conn:
            c = conn.cursor()
            c.execute('CREATE INDEX IF NOT EXISTS idx_time ON reservations(time)')
            c.execute("""SELECT time, name, surname, first_donation, stato 
                        FROM reservations 
                        ORDER BY time""")
            return c.fetchall()
            
    except Exception as e:
        logger.error(f"Errore nel recupero delle prenotazioni: {str(e)}")
        return []

def delete_reservation_from_db(date, time):
    """Elimina una prenotazione dal database"""
    try:
        if isinstance(date, str):
            date_obj = QDate.fromString(date, "yyyy-MM-dd")
        else:
            date_obj = date
            
        db_path = get_db_path(date_obj)
        
        with get_db_connection(db_path) as conn:
            c = conn.cursor()
            c.execute("DELETE FROM reservations WHERE time=?", (time,))
            conn.commit()
            
            if c.rowcount > 0:
                details = f"Data: {date}, Ora: {time}"
                add_history_entry("Cancellazione prenotazione", details)
                return True
        return False
        
    except Exception as e:
        logger.error(f"Errore nell'eliminazione della prenotazione: {str(e)}")
        return False

def get_cloud_path():
    settings = QSettings('Hemodos', 'DatabaseSettings')
    service = settings.value("cloud_service")
    
    if service == "onedrive":
        # Implementa la logica per OneDrive
        pass
    elif service == "google":
        # Implementa la logica per Google Drive
        pass
    
    # Usa il percorso locale direttamente invece di chiamare get_local_path
    default_path = os.path.expanduser("~/Documents/Hemodos")
    os.makedirs(default_path, exist_ok=True)
    return os.path.join(default_path, "hemodos.db")

def add_donation_date(year, date):
    """Aggiunge una data di donazione al database annuale"""
    try:
        db_path = get_db_path(is_donation_dates=True)
        
        with get_db_connection(db_path) as conn:
            c = conn.cursor()
            
            # Crea le tabelle con struttura ottimizzata
            c.executescript('''
                CREATE TABLE IF NOT EXISTS donation_dates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    year INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(year, date)
                );
                
                CREATE INDEX IF NOT EXISTS idx_donation_dates ON donation_dates(year, date);
                
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    action TEXT NOT NULL,
                    details TEXT
                );
            ''')
            
            # Inserisci la data
            c.execute("INSERT OR IGNORE INTO donation_dates (year, date) VALUES (?, ?)", 
                     (year, date))
            
            # Aggiungi alla cronologia
            details = f"Anno: {year}, Data: {date}"
            c.execute("INSERT INTO history (action, details) VALUES (?, ?)",
                     ("Aggiunta data donazione", details))
            
            conn.commit()
            return True
            
    except Exception as e:
        logger.error(f"Errore nell'aggiunta della data di donazione: {str(e)}")
        return False

def get_donation_dates(year):
    """Ottiene le date di donazione per un anno specifico"""
    try:
        # Crea una data fittizia per l'anno richiesto
        dummy_date = QDate(year, 1, 1)
        db_path = get_db_path(dummy_date, is_donation_dates=True)
        
        if not os.path.exists(db_path):
            return []
            
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Crea la tabella se non esiste
        c.execute('''CREATE TABLE IF NOT EXISTS donation_dates
                     (date text PRIMARY KEY)''')
        
        # Ottieni tutte le date
        c.execute("SELECT date FROM donation_dates ORDER BY date")
        dates = [row[0] for row in c.fetchall()]
        
        conn.close()
        return dates
        
    except Exception as e:
        logger.error(f"Errore nel recupero delle date di donazione: {str(e)}")
        return []

def delete_donation_date(year, date):
    try:
        db_path = get_db_path(is_donation_dates=True)
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Elimina la data
        c.execute("DELETE FROM donation_dates WHERE year=? AND date=?", (year, date))
        
        # Aggiungi alla cronologia
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        details = f"Anno: {year}, Data: {date}"
        c.execute("INSERT INTO history VALUES (?, ?, ?)", 
                 (timestamp, "Rimozione data donazione", details))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Errore nella rimozione della data di donazione: {str(e)}")
        return False

def add_donation_time(date, time, name="", surname="", first_donation=False):
    """Aggiunge un orario di donazione per una data specifica"""
    try:
        if isinstance(date, str):
            date_obj = QDate.fromString(date, "yyyy-MM-dd")
        else:
            date_obj = date
            
        db_path = get_db_path(date_obj)
        
        with get_db_connection(db_path) as conn:
            c = conn.cursor()
            
            # Aggiungi la riga con l'orario
            c.execute("""INSERT INTO reservations 
                        (time, name, surname, first_donation, stato) 
                        VALUES (?,?,?,?,'Non effettuata')""", 
                     (time, name, surname, first_donation))
            
            # Assicurati che la data sia anche nelle date di donazione
            year = date_obj.year()
            add_donation_date(year, date_obj.toString("yyyy-MM-dd"))
            
            conn.commit()
            
            details = f"Data: {date_obj.toString('yyyy-MM-dd')}, Ora: {time}"
            add_history_entry("Aggiunta orario donazione", details, specific_date=date_obj)
            return True
            
    except Exception as e:
        logger.error(f"Errore nell'aggiunta dell'orario di donazione: {str(e)}")
        return False

class CloudMonitorThread(QThread):
    file_changed = pyqtSignal()

    def __init__(self, watch_path):
        super().__init__()
        self.watch_path = watch_path
        self.running = True
        logger.info(f"Monitoraggio cloud avviato su: {watch_path}")

    def run(self):
        event_handler = DatabaseChangeHandler(self)
        observer = Observer()
        observer.schedule(event_handler, self.watch_path, recursive=False)
        observer.start()
        logger.info("Observer cloud avviato")
        
        while self.running:
            self.msleep(1000)  # Controlla ogni secondo
            
        observer.stop()
        observer.join()
        logger.info("Observer cloud fermato")

    def stop(self):
        logger.info("Arresto monitoraggio cloud...")
        self.running = False

class DatabaseChangeHandler(FileSystemEventHandler):
    def __init__(self, thread):
        self.thread = thread
        self.last_modified = time.time()
        
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.db'):
            current_time = time.time()
            if current_time - self.last_modified > 1:
                self.last_modified = current_time
                logger.debug(f"Rilevata modifica file: {event.src_path}")
                self.thread.file_changed.emit()

def setup_cloud_monitoring(main_window):
    """Configura il monitoraggio del cloud"""
    try:
        settings = QSettings('Hemodos', 'DatabaseSettings')
        service = settings.value("cloud_service", "Locale")
        
        if service in ["OneDrive", "Google Drive"]:
            db_path = get_db_path()
            watch_dir = os.path.dirname(db_path)
            
            logger.info(f"Avvio monitoraggio cloud per servizio: {service}")
            monitor_thread = CloudMonitorThread(watch_dir)
            monitor_thread.file_changed.connect(main_window.reload_database)
            monitor_thread.start()
            return monitor_thread
            
        logger.info("Monitoraggio cloud non necessario (modalità locale)")
        return None
        
    except Exception as e:
        logger.error(f"Errore nel setup del monitoraggio cloud: {str(e)}")
        return None

def get_monthly_stats_db_path(year, month):
    """Ottiene il percorso del database delle statistiche mensili"""
    base_path = os.path.dirname(get_db_path())
    return os.path.join(base_path, f"statistiche_{year}_{month:02d}.db")

def save_donation_status(date, time, status):
    """Salva lo stato di una donazione"""
    try:
        if isinstance(date, str):
            date_obj = QDate.fromString(date, "yyyy-MM-dd")
        else:
            date_obj = date
            
        db_path = get_db_path(date_obj)
        
        with get_db_connection(db_path) as conn:
            c = conn.cursor()
            c.execute("UPDATE reservations SET stato = ? WHERE time = ?", 
                     (status, time))
            conn.commit()
            
            if c.rowcount > 0:
                details = f"Data: {date}, Ora: {time}, Nuovo stato: {status}"
                add_history_entry("Cambio stato donazione", details, specific_date=date_obj)
                return True
        return False
        
    except Exception as e:
        logger.error(f"Errore nel salvataggio dello stato: {str(e)}")
        return False

def reset_reservation(date, time):
    """Resetta i dati di una prenotazione mantenendo l'orario"""
    try:
        if isinstance(date, str):
            date_obj = QDate.fromString(date, "yyyy-MM-dd")
        else:
            date_obj = date
            
        db_path = get_db_path(date_obj)
        
        with get_db_connection(db_path) as conn:
            c = conn.cursor()
            
            # Prima ottieni i dati attuali per la cronologia
            c.execute("SELECT name, surname FROM reservations WHERE time = ?", (time,))
            result = c.fetchone()
            old_name, old_surname = result if result else ("", "")
            
            # Resetta tutti i campi tranne l'orario
            c.execute("""UPDATE reservations 
                        SET name = '', surname = '', 
                            first_donation = 0, stato = 'Non effettuata',
                            updated_at = CURRENT_TIMESTAMP
                        WHERE time = ?""", (time,))
            
            conn.commit()
            
            # Aggiungi alla cronologia
            if old_name or old_surname:
                details = f"Data: {date_obj.toString('yyyy-MM-dd')}, Ora: {time}\n"
                details += f"Prenotazione cancellata: {old_name} {old_surname}"
                add_history_entry("Reset prenotazione", details, specific_date=date_obj)
            
            return True
            
    except Exception as e:
        logger.error(f"Errore nel reset della prenotazione: {str(e)}")
        return False

def optimize_database(db_path):
    """Esegue ottimizzazioni periodiche sul database"""
    try:
        with get_db_connection(db_path) as conn:
            # Analizza gli indici
            conn.execute("ANALYZE")
            
            # Ricostruisci gli indici
            conn.execute("REINDEX")
            
            # Compatta il database
            conn.execute("VACUUM")
            
            # Ottimizza il database
            conn.execute("PRAGMA optimize")
            
        logger.info(f"Database ottimizzato: {db_path}")
        return True
        
    except Exception as e:
        logger.error(f"Errore nell'ottimizzazione del database: {str(e)}")
        return False

def cleanup_old_data(days_to_keep=365):
    """Pulisce i dati più vecchi di un certo numero di giorni"""
    try:
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # Trova tutti i database più vecchi
        base_path = os.path.dirname(get_db_path())
        for year_dir in os.listdir(base_path):
            if not year_dir.isdigit():
                continue
                
            year = int(year_dir)
            if year < cutoff_date.year:
                # Archivia o elimina i dati vecchi secondo la policy
                archive_old_data(year)
                
        logger.info(f"Pulizia dati completata. Mantenuti ultimi {days_to_keep} giorni")
        return True
        
    except Exception as e:
        logger.error(f"Errore nella pulizia dei dati vecchi: {str(e)}")
        return False

def archive_old_data(year):
    """Archivia i dati di un anno specifico"""
    try:
        base_path = os.path.dirname(get_db_path())
        year_path = os.path.join(base_path, str(year))
        archive_path = os.path.join(base_path, "archivio")
        
        if os.path.exists(year_path):
            # Crea la directory di archivio se non esiste
            os.makedirs(archive_path, exist_ok=True)
            
            # Sposta l'intera directory dell'anno nell'archivio
            import shutil
            shutil.move(year_path, os.path.join(archive_path, str(year)))
            
            logger.info(f"Anno {year} archiviato con successo")
            return True
            
    except Exception as e:
        logger.error(f"Errore nell'archiviazione dell'anno {year}: {str(e)}")
        return False

def add_to_history(year, action, details):
    """Aggiunge un'azione alla cronologia"""
    try:
        base_path = get_base_path()
        history_db_path = os.path.join(base_path, str(year), f"cronologia_{year}.db")
        
        # Crea la directory se non esiste
        os.makedirs(os.path.dirname(history_db_path), exist_ok=True)
        
        conn = sqlite3.connect(history_db_path)
        c = conn.cursor()
        
        # Crea la tabella se non esiste
        c.execute('''CREATE TABLE IF NOT EXISTS history
                    (timestamp text, action text, details text)''')
        
        # Inserisci il record
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO history VALUES (?, ?, ?)", 
                 (timestamp, action, details))
        
        conn.commit()
        conn.close()
        
        return True
    except Exception as e:
        logger.error(f"Errore nell'aggiunta alla cronologia: {str(e)}")
        return False
