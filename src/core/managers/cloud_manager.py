from PyQt5.QtCore import QObject, QTimer, QSettings, pyqtSignal, QThread
import os
import shutil
import time
from datetime import datetime
from core.logger import logger
import sqlite3
import hashlib
from core.database import setup_cloud_monitoring
from PyQt5.QtWidgets import QApplication

class SyncThread(QThread):
    def __init__(self, local_path, cloud_path, parent=None):
        super().__init__(parent)
        self.local_path = local_path
        self.cloud_path = cloud_path
        self.is_running = True
        
    def run(self):
        logger.info(f"Thread di sincronizzazione avviato per {self.local_path}")
        while self.is_running:
            try:
                if not self.is_running:
                    logger.info("Thread interrotto, uscita...")
                    break
                    
                if os.path.exists(self.local_path) and os.path.exists(self.cloud_path):
                    local_mtime = os.path.getmtime(self.local_path)
                    cloud_mtime = os.path.getmtime(self.cloud_path)
                    
                    if local_mtime > cloud_mtime:
                        shutil.copy2(self.local_path, self.cloud_path)
                    elif cloud_mtime > local_mtime:
                        shutil.copy2(self.cloud_path, self.local_path)
                
                time.sleep(1)  # Ridotto il tempo di sleep per una chiusura più veloce
            except Exception as e:
                logger.error(f"Errore nella sincronizzazione: {str(e)}")
                if not self.is_running:
                    break
                time.sleep(5)

    def stop(self):
        """Ferma il thread in modo sicuro"""
        logger.info("Richiesta interruzione thread...")
        self.is_running = False
        if not self.wait(2000):  # Attendi max 2 secondi
            logger.warning("Thread non terminato naturalmente, forzo la chiusura")
            self.terminate()
            self.wait()  # Attendi la terminazione forzata
        logger.info("Thread terminato")

class CloudSetupThread(QThread):
    def __init__(self, cloud_service):
        super().__init__()
        self.cloud_service = cloud_service
        self._is_running = True
        
    def stop(self):
        self._is_running = False
        self.wait()
        
    def run(self):
        if not self._is_running:
            return
            
        try:
            # Configura il servizio cloud selezionato
            if self.cloud_service == "Google Drive":
                self.setup_google_drive()
            elif self.cloud_service == "Dropbox":
                self.setup_dropbox()
        except Exception as e:
            logger.error(f"Errore nella configurazione cloud: {str(e)}")

class CloudManager(QObject):
    sync_started = pyqtSignal()
    sync_completed = pyqtSignal()
    sync_error = pyqtSignal(str)
    
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.settings = QSettings('Hemodos', 'DatabaseSettings')
        
        # Inizializza i timer come None
        self.sync_timer = None
        self.first_sync_timer = None
        
        # Crea il timer di sincronizzazione
        self._create_sync_timer()
        
        self.last_sync = None
        self.is_syncing = False
        self.sync_threads = []
        self.observer = None
        self.is_cloud_mode = False

    def _create_sync_timer(self):
        """Crea il timer di sincronizzazione"""
        if not self.sync_timer:
            self.sync_timer = QTimer(self)
            self.sync_timer.timeout.connect(self.sync_databases)

    def cleanup(self):
        """Pulisce tutte le risorse cloud"""
        try:
            logger.info("Inizio pulizia risorse cloud...")
            
            # Ferma i timer in modo sicuro
            try:
                if self.sync_timer is not None:
                    self.sync_timer.stop()
                    self.sync_timer = None
                
                if self.first_sync_timer is not None:
                    self.first_sync_timer.stop()
                    self.first_sync_timer = None
            except Exception as e:
                logger.error(f"Errore nella chiusura dei timer: {str(e)}")
            
            # Ferma l'observer
            if self.observer:
                try:
                    self.observer.stop()
                    self.observer.join()
                    self.observer = None
                    logger.info("Observer arrestato con successo")
                except Exception as e:
                    logger.error(f"Errore nell'arresto dell'observer: {str(e)}")
            
            # Ferma i thread di sincronizzazione
            if self.sync_threads:
                logger.info(f"Arresto {len(self.sync_threads)} thread di sincronizzazione...")
                for thread in self.sync_threads[:]:
                    if thread and thread.isRunning():
                        try:
                            thread.stop()
                            self.sync_threads.remove(thread)
                        except Exception as e:
                            logger.error(f"Errore nell'arresto del thread: {str(e)}")
            
            self.sync_threads.clear()
            self.is_cloud_mode = False
            logger.info("Pulizia risorse cloud completata con successo")
            
        except Exception as e:
            logger.error(f"Errore critico durante la pulizia delle risorse cloud: {str(e)}")
            import traceback
            logger.error(f"Traceback completo:\n{traceback.format_exc()}")

    def __del__(self):
        """Distruttore della classe"""
        try:
            logger.info("Distruzione CloudManager...")
            self.cleanup()
        except Exception as e:
            logger.error(f"Errore nel distruttore di CloudManager: {str(e)}")

    def setup_monitoring(self):
        """Configura il monitoraggio del cloud"""
        try:
            # Prima ferma eventuali monitoraggi esistenti
            self.cleanup()
            
            # Usa database_dir_manager per verificare la modalità
            if self.main_window.database_dir_manager.is_local_mode():
                logger.info("Monitoraggio cloud non avviato: modalità locale")
                self.is_cloud_mode = False
                return
                
            # Attendi che eventuali operazioni in sospeso siano completate
            QApplication.processEvents()
            
            self.is_cloud_mode = True
            self.observer = setup_cloud_monitoring(self.main_window)
            cloud_service = self.settings.value("cloud_service", "Locale")
            cloud_path = self.settings.value("cloud_path", "")
            logger.info(f"Monitoraggio cloud avviato per {cloud_service} su {cloud_path}")
            
        except Exception as e:
            logger.error(f"Errore nell'avvio del monitoraggio cloud: {str(e)}")
            self.is_cloud_mode = False

    def setup_cloud_sync(self, cloud_path):
        """Configura la sincronizzazione cloud"""
        logger.info(f"Tentativo di configurazione sincronizzazione cloud per: {cloud_path}")
        
        if not self.main_window.database_dir_manager.is_cloud_path(cloud_path):
            logger.warning(f"Percorso non riconosciuto come cloud: {cloud_path}")
            return False
            
        try:
            logger.info("Avvio configurazione sincronizzazione cloud...")
            
            base_path = self.main_window.database_dir_manager.get_base_path()
            logger.info(f"Percorso base: {base_path}")
            
            current_year = self.settings.value("selected_year")
            year_path = os.path.join(base_path, str(current_year))
            logger.info(f"Percorso anno: {year_path}")
            
            if not os.path.exists(year_path):
                logger.info(f"Creazione directory anno: {year_path}")
                os.makedirs(year_path)
            
            # Configura i thread di sincronizzazione
            db_files = [f for f in os.listdir(year_path) if f.endswith('.db')]
            logger.info(f"Trovati {len(db_files)} database da sincronizzare")
            
            for i, db_file in enumerate(db_files):
                cloud_db_path = os.path.join(year_path, db_file)
                local_db_path = os.path.join(os.path.dirname(cloud_db_path), f"local_{db_file}")
                logger.info(f"Configurazione thread {i+1} per: {db_file}")
                
                try:
                    sync_thread = SyncThread(local_db_path, cloud_db_path, parent=self)
                    sync_thread.start()
                    self.sync_threads.append(sync_thread)
                    logger.info(f"Thread {i+1} avviato con successo")
                except Exception as e:
                    logger.error(f"Errore nell'avvio del thread {i+1}: {str(e)}")
            
            self.is_cloud_mode = True
            logger.info("Configurazione sincronizzazione cloud completata con successo")
            return True
            
        except Exception as e:
            logger.error(f"Errore critico nella configurazione cloud: {str(e)}")
            import traceback
            logger.error(f"Traceback completo:\n{traceback.format_exc()}")
            self.is_cloud_mode = False
            return False

    def start_delayed_sync(self):
        """Avvia la sincronizzazione dopo un ritardo"""
        if self.settings.value("pending_cloud_sync", False, type=bool):
            logger.info("Programmata sincronizzazione cloud tra 5 minuti")
            
            # Ferma eventuali timer esistenti
            if self.first_sync_timer:
                self.first_sync_timer.stop()
                self.first_sync_timer = None
            
            # Crea un nuovo timer per il primo avvio
            self.first_sync_timer = QTimer(self)
            self.first_sync_timer.setSingleShot(True)
            self.first_sync_timer.timeout.connect(self._initialize_sync)
            self.first_sync_timer.start(300000)  # 5 minuti
            
            # Aggiorna solo la status bar
            self.update_status_bar()

    def _initialize_sync(self):
        """Inizializza effettivamente la sincronizzazione"""
        try:
            cloud_path = self.settings.value("cloud_path", "")
            if not cloud_path:
                return
                
            base_path = self.main_window.database_dir_manager.get_base_path()
            current_year = self.settings.value("selected_year")
            year_path = os.path.join(base_path, str(current_year))
            
            if not os.path.exists(year_path):
                os.makedirs(year_path)
            
            # Configura i thread di sincronizzazione
            db_files = [f for f in os.listdir(year_path) if f.endswith('.db')]
            for db_file in db_files:
                cloud_db_path = os.path.join(year_path, db_file)
                local_db_path = os.path.join(os.path.dirname(cloud_db_path), f"local_{db_file}")
                
                sync_thread = SyncThread(local_db_path, cloud_db_path, parent=self)
                sync_thread.start()
                self.sync_threads.append(sync_thread)
            
            # Rimuovi il flag di sincronizzazione pendente
            self.settings.remove("pending_cloud_sync")
            
            logger.info("Sincronizzazione cloud inizializzata")
            
        except Exception as e:
            logger.error(f"Errore nell'inizializzazione della sincronizzazione: {str(e)}")

    def set_local_mode(self):
        """Imposta la modalità locale"""
        self.cleanup()
        self.settings.setValue("cloud_service", "Locale")
        self.settings.setValue("cloud_path", "")
        self.update_status_bar()
        logger.info("Modalità locale attivata")

    def update_status_bar(self):
        """Aggiorna le informazioni nella status bar"""
        if not hasattr(self.main_window, 'status_manager'):
            return
            
        if not self.is_cloud_mode:
            self.main_window.status_manager.update_cloud_info("")
            return
            
        cloud_service = self.settings.value("cloud_service", "Locale")
        if self.last_sync:
            sync_time = self.last_sync.strftime("%H:%M:%S")
            self.main_window.status_manager.update_cloud_info(
                f"Cloud: {cloud_service} - Ultima sync: {sync_time}"
            )
        else:
            self.main_window.status_manager.update_cloud_info(
                f"Cloud: {cloud_service} - In attesa prima sync"
            )

    def sync_databases(self):
        """Sincronizza i database con il cloud"""
        if self.is_syncing:
            return
            
        try:
            self.is_syncing = True
            self.sync_started.emit()
            self.main_window.status_manager.show_message("Sincronizzazione in corso...", 0)
            
            cloud_service = self.settings.value("cloud_service", "Locale")
            if cloud_service == "Locale":
                return
                
            cloud_path = self.settings.value("cloud_path", "")
            if not cloud_path or not os.path.exists(cloud_path):
                raise Exception("Percorso cloud non valido")

            current_year = self.settings.value("selected_year")
            hemodos_path = os.path.join(cloud_path, "Hemodos", str(current_year))
            
            # Verifica e sincronizza ogni database
            db_files = [f for f in os.listdir(hemodos_path) if f.endswith('.db')]
            for db_file in db_files:
                cloud_db_path = os.path.join(hemodos_path, db_file)
                local_db_path = os.path.join(os.path.dirname(cloud_db_path), f"local_{db_file}")
                
                # Se il file locale non esiste, crea una copia
                if not os.path.exists(local_db_path):
                    shutil.copy2(cloud_db_path, local_db_path)
                    continue
                
                # Confronta le versioni e sincronizza
                self._sync_database(local_db_path, cloud_db_path)
            
            self.last_sync = datetime.now()
            self.update_status_bar()
            self.sync_completed.emit()
            self.main_window.status_manager.show_message("Sincronizzazione completata", 3000)
            
        except Exception as e:
            error_msg = f"Errore durante la sincronizzazione: {str(e)}"
            logger.error(error_msg)
            self.sync_error.emit(error_msg)
            self.main_window.status_manager.show_message(error_msg, 5000)
        finally:
            self.is_syncing = False

    def _sync_database(self, local_path, cloud_path):
        """Sincronizza un singolo database"""
        try:
            # Ottieni l'hash dei file
            local_hash = self._get_file_hash(local_path)
            cloud_hash = self._get_file_hash(cloud_path)
            
            if local_hash != cloud_hash:
                # Ottieni i timestamp di modifica
                local_mtime = os.path.getmtime(local_path)
                cloud_mtime = os.path.getmtime(cloud_path)
                
                # Il file più recente vince
                if local_mtime > cloud_mtime:
                    shutil.copy2(local_path, cloud_path)
                else:
                    shutil.copy2(cloud_path, local_path)
                    
        except Exception as e:
            logger.error(f"Errore nella sincronizzazione del database {local_path}: {str(e)}")
            raise

    def _get_file_hash(self, file_path):
        """Calcola l'hash SHA-256 di un file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def stop_sync(self):
        """Ferma la sincronizzazione"""
        self.sync_timer.stop()

    def set_local_mode(self):
        """Imposta la modalità locale"""
        self.cleanup()
        self.settings.setValue("cloud_service", "Locale")
        self.settings.setValue("cloud_path", "")
        self.update_status_bar()
        logger.info("Modalità locale attivata")

    def update_status_bar(self):
        """Aggiorna le informazioni nella status bar"""
        if not hasattr(self.main_window, 'status_manager'):
            return
            
        if not self.is_cloud_mode:
            self.main_window.status_manager.update_cloud_info("")
            return
            
        cloud_service = self.settings.value("cloud_service", "Locale")
        if self.last_sync:
            sync_time = self.last_sync.strftime("%H:%M:%S")
            self.main_window.status_manager.update_cloud_info(
                f"Cloud: {cloud_service} - Ultima sync: {sync_time}"
            )
        else:
            self.main_window.status_manager.update_cloud_info(
                f"Cloud: {cloud_service} - In attesa prima sync"
            ) 