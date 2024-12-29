import sqlite3
from datetime import datetime
import os
from PyQt5.QtCore import QSettings, QThread, pyqtSignal, QDate
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from core.logger import logger
import time

def get_db_path(specific_date=None):
    """Ottiene il percorso del database corretto"""
    settings = QSettings('Hemodos', 'DatabaseSettings')
    service = settings.value("cloud_service", "Locale")
    
    if service == "Locale":
        base_path = os.path.expanduser("~/Documents/Hemodos")
    else:
        cloud_path = settings.value("cloud_path", "")
        base_path = os.path.join(cloud_path, "Hemodos")
    
    if specific_date:
        # Assicurati che la directory dell'anno esista
        year_path = os.path.join(base_path, str(specific_date.year()))
        os.makedirs(year_path, exist_ok=True)
        
        # Crea il nome del file con giorno e mese
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
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Controlla quali colonne esistono
        cursor = c.execute('PRAGMA table_info(reservations)')
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'first_donation' not in columns or 'stato' not in columns:
            print("Migrazione database: aggiunta colonne mancanti")
            # Crea una tabella temporanea con la nuova struttura
            c.executescript('''
                BEGIN TRANSACTION;
                
                -- Crea una tabella temporanea con la nuova struttura
                CREATE TABLE reservations_new
                    (time text, name text, surname text, 
                     first_donation boolean DEFAULT 0,
                     stato text DEFAULT 'Non effettuata');
                
                -- Copia i dati esistenti
                INSERT INTO reservations_new (time, name, surname)
                SELECT time, name, surname FROM reservations;
                
                -- Elimina la vecchia tabella
                DROP TABLE reservations;
                
                -- Rinomina la nuova tabella
                ALTER TABLE reservations_new RENAME TO reservations;
                
                COMMIT;
            ''')
            
        conn.commit()
        conn.close()
        print("Migrazione database completata con successo")
    except Exception as e:
        print(f"Errore durante la migrazione del database: {str(e)}")
        raise

def init_db(specific_date=None):
    """Inizializza il database per una data specifica"""
    try:
        # Inizializza il database giornaliero
        db_path = get_db_path(specific_date=specific_date)
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
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
        
        # Esegui la migrazione se necessario
        migrate_database()
        
        # Inizializza anche il database annuale
        year_db_path = os.path.join(os.path.dirname(db_path), f"hemodos_{datetime.now().year}.db")
        conn = sqlite3.connect(year_db_path)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS annual_stats
                     (date text, total_donations integer, 
                      first_donations integer, completed_donations integer)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS monthly_stats
                     (month integer, total_reservations integer, 
                      completed_donations integer, first_donations integer)''')
        
        conn.commit()
        conn.close()
        
        print(f"Database inizializzato con successo: {db_path}")
    except Exception as e:
        print(f"Errore durante l'inizializzazione del database: {str(e)}")
        raise

def get_history_db_path(year=None):
    """Ottiene il percorso del database della cronologia per l'anno specificato"""
    if year is None:
        year = datetime.now().year
    
    base_path = os.path.dirname(get_db_path())
    return os.path.join(base_path, f"cronologia_{year}.db")

def add_history_entry(action, details, specific_date=None):
    """
    Aggiunge un'entrata nella cronologia nel database annuale
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Gestisci la data specifica
        if specific_date:
            if isinstance(specific_date, QDate):
                year = specific_date.year()
            elif isinstance(specific_date, str):
                year = int(specific_date.split('-')[0])
            else:
                year = datetime.now().year
        else:
            year = datetime.now().year
        
        # Usa il database della cronologia annuale
        history_db = get_history_db_path(year)
        
        # Assicurati che la directory esista
        os.makedirs(os.path.dirname(history_db), exist_ok=True)
        
        # Usa with per gestire correttamente la connessione
        with sqlite3.connect(history_db) as conn:
            c = conn.cursor()
            
            c.execute('''CREATE TABLE IF NOT EXISTS history
                         (timestamp text, action text, details text)''')
            c.execute("INSERT INTO history VALUES (?, ?, ?)", 
                     (timestamp, action, details))
            
            conn.commit()
            
    except Exception as e:
        logger.error(f"Errore nell'aggiunta alla cronologia: {str(e)}")

def get_history(year=None):
    """Recupera la cronologia per l'anno specificato"""
    if year is None:
        year = datetime.now().year
        
    history_db = get_history_db_path(year)
    
    if not os.path.exists(history_db):
        return []
        
    conn = sqlite3.connect(history_db)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (timestamp text, action text, details text)''')
    
    c.execute("SELECT timestamp, action, details FROM history ORDER BY timestamp DESC")
    results = c.fetchall()
    conn.close()
    
    return results

def add_reservation(date, time, name, surname, first_donation):
    """Aggiunge o aggiorna una prenotazione nel database"""
    try:
        # Converti la data in QDate se è una stringa
        if isinstance(date, str):
            date_obj = QDate.fromString(date, "yyyy-MM-dd")
        else:
            date_obj = date
            
        # Ottieni il percorso del database per questa data
        db_path = get_db_path(date_obj)
        
        # Assicurati che la directory esista
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Usa with per gestire correttamente la connessione
        with sqlite3.connect(db_path) as conn:
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

def get_reservations(selected_date):
    """Ottiene le prenotazioni per una data specifica"""
    try:
        # Converti QDate in stringa se necessario
        if hasattr(selected_date, 'toString'):
            date_str = selected_date.toString("yyyy-MM-dd")
            selected_date = QDate.fromString(date_str, "yyyy-MM-dd")
        
        # Ottieni il percorso del database per questa data
        db_path = get_db_path(selected_date)
        
        # Crea la directory se non esiste
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Crea la tabella se non esiste
        c.execute('''CREATE TABLE IF NOT EXISTS reservations
                     (time text PRIMARY KEY, name text, surname text, 
                      first_donation integer DEFAULT 0, 
                      stato text DEFAULT 'Non effettuata')''')
        
        c.execute('SELECT time, name, surname, first_donation, stato FROM reservations ORDER BY time')
        reservations = c.fetchall()
        conn.close()
        
        return reservations
        
    except Exception as e:
        logger.error(f"Errore nel recupero delle prenotazioni: {str(e)}")
        return []

def delete_reservation(date, time):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("DELETE FROM reservations WHERE date=? AND time=?", 
              (date, time))
    conn.commit()
    conn.close()
    
    details = f"Data: {date}, Ora: {time}"
    add_history_entry("Cancellazione prenotazione", details)

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
    try:
        db_path = get_db_path(is_donation_dates=True)
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Crea le tabelle se non esistono
        c.executescript('''
            CREATE TABLE IF NOT EXISTS donation_dates
                (year integer, date text, UNIQUE(year, date));
            CREATE TABLE IF NOT EXISTS history
                (timestamp text, action text, details text);
        ''')
        
        # Inserisci la data
        c.execute("INSERT OR IGNORE INTO donation_dates VALUES (?, ?)", (year, date))
        
        # Aggiungi alla cronologia
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        details = f"Anno: {year}, Data: {date}"
        c.execute("INSERT INTO history VALUES (?, ?, ?)", 
                 (timestamp, "Aggiunta data donazione", details))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Errore nell'aggiunta della data di donazione: {str(e)}")
        return False

def get_donation_dates(year):
    """Ottiene le date di donazione per un anno specifico"""
    try:
        settings = QSettings('Hemodos', 'DatabaseSettings')
        service = settings.value("cloud_service", "Locale")
        
        if service == "Locale":
            base_path = os.path.expanduser("~/Documents/Hemodos")
        else:
            cloud_path = settings.value("cloud_path", "")
            base_path = os.path.join(cloud_path, "Hemodos")
        
        db_path = os.path.join(base_path, str(year), f"date_donazione_{year}.db")
        
        if not os.path.exists(db_path):
            return []
            
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('SELECT date FROM donation_dates WHERE year = ?', (year,))
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
    """
    Aggiunge un orario di donazione per una data specifica
    """
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Aggiungi la riga con l'orario (gli altri campi sono vuoti)
        c.execute("INSERT INTO reservations VALUES (?,?,?,?,?)", 
                 (date, time, name, surname, first_donation))
        
        # Assicurati che la data sia anche nelle date di donazione
        year = int(date.split('-')[0])
        add_donation_date(year, date)
        
        conn.commit()
        conn.close()
        
        details = f"Data: {date}, Ora: {time}"
        add_history_entry("Aggiunta orario donazione", details)
        return True
        
    except Exception as e:
        print(f"Errore nell'aggiunta dell'orario di donazione: {str(e)}")
        return False

class CloudMonitorThread(QThread):
    file_changed = pyqtSignal()

    def __init__(self, watch_path):
        super().__init__()
        self.watch_path = watch_path
        self.running = True

    def run(self):
        event_handler = DatabaseChangeHandler(self)
        observer = Observer()
        observer.schedule(event_handler, self.watch_path, recursive=False)
        observer.start()
        
        while self.running:
            self.msleep(1000)  # Controlla ogni secondo
            
        observer.stop()
        observer.join()

    def stop(self):
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
                self.thread.file_changed.emit()

def setup_cloud_monitoring(main_window):
    settings = QSettings('Hemodos', 'DatabaseSettings')
    service = settings.value("cloud_service", "Locale")
    
    if service in ["OneDrive", "Google Drive"]:
        db_path = get_db_path()
        watch_dir = os.path.dirname(db_path)
        
        monitor_thread = CloudMonitorThread(watch_dir)
        monitor_thread.file_changed.connect(main_window.reload_database)
        monitor_thread.start()
        return monitor_thread
    return None

def get_monthly_stats_db_path(year, month):
    """Ottiene il percorso del database delle statistiche mensili"""
    base_path = os.path.dirname(get_db_path())
    return os.path.join(base_path, f"statistiche_{year}_{month:02d}.db")

def save_donation_status(date, time, status):
    """Salva lo stato di una donazione"""
    try:
        # Converti la data in QDate se è una stringa
        if isinstance(date, str):
            date_obj = QDate.fromString(date, "yyyy-MM-dd")
        else:
            date_obj = date
            
        # Ottieni il percorso del database per questa data
        db_path = get_db_path(date_obj)
        
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Aggiorna lo stato
        c.execute("UPDATE reservations SET stato = ? WHERE time = ?", 
                 (status, time))
        
        # Aggiungi alla cronologia
        if c.rowcount > 0:
            details = f"Data: {date}, Ora: {time}, Nuovo stato: {status}"
            add_history_entry("Cambio stato donazione", details, specific_date=date_obj)
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Errore nel salvataggio dello stato: {str(e)}")
        return False

def reset_reservation(date, time):
    """Resetta i dati di una prenotazione mantenendo l'orario"""
    try:
        db_path = get_db_path(specific_date=date)
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Prima ottieni i dati attuali per la cronologia
        c.execute("SELECT name, surname FROM reservations WHERE time = ?", (time,))
        result = c.fetchone()
        old_name, old_surname = result if result else ("", "")
        
        # Resetta tutti i campi tranne l'orario
        c.execute("""UPDATE reservations 
                    SET name = '', surname = '', 
                        first_donation = 0, stato = 'Non effettuata'
                    WHERE time = ?""", (time,))
        
        conn.commit()
        conn.close()
        
        # Aggiungi alla cronologia
        if old_name or old_surname:  # Solo se c'era una prenotazione
            details = f"Data: {date}, Ora: {time}\nPrenotazione cancellata: {old_name} {old_surname}"
            add_history_entry("Reset prenotazione", details, specific_date=date)
        
        return True
        
    except Exception as e:
        print(f"Errore nel reset della prenotazione: {str(e)}")
        return False
