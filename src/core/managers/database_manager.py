from PyQt5.QtCore import QObject, QDate
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
import os
from datetime import datetime
from core.logger import logger
from core.database import (
    init_db, get_db_path, add_reservation, 
    save_donation_status, delete_reservation_from_db, add_to_history
)
from gui.dialogs.daily_reservations_dialog import DailyReservationsDialog
import glob
import sqlite3

class DatabaseManager(QObject):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.last_vacuum_date = self.main_window.settings.value("last_vacuum_date", None)
        
        # Inizializza WAL mode per tutti i database esistenti
        self._init_wal_mode()

    def _init_wal_mode(self):
        """Inizializza il WAL mode per tutti i database esistenti"""
        try:
            import sqlite3
            base_path = self._get_base_path()
            
            # Cerca tutti i database nell'applicazione
            for year_dir in os.listdir(base_path):
                year_path = os.path.join(base_path, year_dir)
                if os.path.isdir(year_path):
                    db_pattern = os.path.join(year_path, "hemodos_*.db")
                    for db_file in glob.glob(db_pattern):
                        self._enable_wal_for_db(db_file)
                        
            logger.info("WAL mode inizializzato per tutti i database")
            
        except Exception as e:
            logger.error(f"Errore nell'inizializzazione WAL mode: {str(e)}")

    def _enable_wal_for_db(self, db_path):
        """Abilita il WAL mode per un singolo database"""
        try:
            with sqlite3.connect(db_path) as conn:
                conn.execute("PRAGMA journal_mode=WAL")
                # Ottimizzazioni aggiuntive per le prestazioni
                conn.execute("PRAGMA synchronous=NORMAL")
                conn.execute("PRAGMA temp_store=MEMORY")
                conn.execute("PRAGMA mmap_size=30000000000")
            logger.debug(f"WAL mode abilitato per: {db_path}")
        except Exception as e:
            logger.error(f"Errore nell'abilitazione WAL mode per {db_path}: {str(e)}")

    def _get_base_path(self):
        """Ottiene il percorso base per i database"""
        service = self.main_window.settings.value("cloud_service", "Locale")
        if service == "Locale":
            return os.path.expanduser("~/Documents/Hemodos")
        else:
            cloud_path = self.main_window.settings.value("cloud_path", "")
            return os.path.join(cloud_path, "Hemodos")

    def load_current_day(self):
        """Carica il database del giorno corrente"""
        try:
            current_date = QDate.currentDate()
            db_path = get_db_path(current_date)
            
            # Se il database non esiste, crealo con WAL mode
            if not os.path.exists(db_path):
                init_db(specific_date=current_date)
                self._enable_wal_for_db(db_path)
            
            # Imposta la data corrente nel calendario
            self.main_window.calendar.setSelectedDate(current_date)
            
            # Aggiorna le info del database
            self.update_db_info()
            
        except Exception as e:
            logger.error(f"Errore nel caricamento del database giornaliero: {str(e)}")
            raise

    def delete_reservation(self, table, current_row):
        """Elimina la prenotazione selezionata"""
        try:
            if current_row >= 0:
                time = table.item(current_row, 0).text()
                name = table.item(current_row, 1).text() if table.item(current_row, 1) else ""
                surname = table.item(current_row, 2).text() if table.item(current_row, 2) else ""
                
                if name.strip() or surname.strip():
                    reply = QMessageBox.question(
                        self.main_window,
                        'Conferma eliminazione',
                        f'Vuoi davvero eliminare la prenotazione delle {time}?',
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )
                    
                    if reply == QMessageBox.Yes:
                        date = self.main_window.calendar.selectedDate().toString("yyyy-MM-dd")
                        if delete_reservation_from_db(date, time):
                            # Reset row data
                            table.setItem(current_row, 1, QTableWidgetItem(""))
                            table.setItem(current_row, 2, QTableWidgetItem(""))
                            table.cellWidget(current_row, 3).setCurrentText("No")
                            table.cellWidget(current_row, 4).setCurrentText("Non effettuata")
                            self.main_window.status_manager.show_message("Prenotazione eliminata", 3000)
                else:
                    QMessageBox.warning(
                        self.main_window,
                        "Attenzione",
                        "Seleziona una prenotazione da eliminare"
                    )
            else:
                QMessageBox.warning(
                    self.main_window,
                    "Attenzione",
                    "Seleziona una prenotazione da eliminare"
                )
                
        except Exception as e:
            self.main_window._handle_error("l'eliminazione della prenotazione", e)

    def on_date_changed(self):
        """Gestisce il cambio di data"""
        try:
            selected_date = self.main_window.calendar.selectedDate()
            self.main_window.calendar_manager.highlight_donation_dates()
            self.update_db_info()
            
        except Exception as e:
            self.main_window._handle_error("il cambio data", e)

    def update_db_info(self):
        """Aggiorna le informazioni del database"""
        try:
            selected_date = self.main_window.calendar.selectedDate()
            year = selected_date.year()
            date_str = selected_date.toString("dd/MM/yyyy")
            db_path = get_db_path(selected_date)
            
            exists = os.path.exists(os.path.dirname(db_path))
            self.main_window.status_manager.update_db_info(year, date_str, exists)
                
        except Exception as e:
            logger.error(f"Errore nell'aggiornamento delle info del database: {str(e)}")
            self.main_window.status_manager.set_db_error()

    def save_reservations(self, table, date, show_dialog=True):
        """Salva lo stato corrente delle prenotazioni"""
        try:
            # Salva ogni riga della tabella
            for row in range(table.rowCount()):
                time = table.item(row, 0).text()
                name = table.item(row, 1).text() if table.item(row, 1) else ""
                surname = table.item(row, 2).text() if table.item(row, 2) else ""
                first_donation = table.cellWidget(row, 3).currentText() == "Sì"
                stato = table.cellWidget(row, 4).currentText()
                
                if name.strip() or surname.strip():
                    add_reservation(date, time, name, surname, first_donation)
                    save_donation_status(date, time, stato)
            
            # Controlla la dimensione del database e fai vacuum se necessario
            self._check_and_vacuum(date)
            
            # Aggiorna l'ultimo salvataggio nella status bar
            current_time = datetime.now().strftime("%H:%M:%S")
            self.main_window.settings.setValue("last_save_time", current_time)
            self.main_window.status_manager.update_last_save_info()
            
            if show_dialog:
                self.main_window.status_manager.show_message("Salvataggio completato", 3000)
            
            # Aggiungi alla cronologia
            year = QDate.fromString(date, "yyyy-MM-dd").year()
            add_to_history(
                year,
                "Salvataggio prenotazioni",
                f"Salvate prenotazioni per la data {date}"
            )
            
            return True
            
        except Exception as e:
            return self.main_window._handle_error("il salvataggio", e, show_dialog)

    def _check_and_vacuum(self, date):
        """Controlla la dimensione del database e esegue VACUUM se necessario"""
        try:
            # Ottieni il percorso del database
            db_path = os.path.join(
                os.path.dirname(get_db_path()),
                date[:4],  # Anno
                f"prenotazioni_{date[8:10]}_{date[5:7]}.db"  # giorno_mese.db
            )
            
            if os.path.exists(db_path):
                # Controlla la dimensione in KB
                size_kb = os.path.getsize(db_path) / 1024
                
                if size_kb > 100:
                    logger.info(f"Database {db_path} supera 100KB ({size_kb:.2f}KB). Esecuzione VACUUM...")
                    
                    # Esegui VACUUM
                    conn = sqlite3.connect(db_path)
                    conn.execute("VACUUM")
                    conn.close()
                    
                    # Registra la nuova dimensione
                    new_size_kb = os.path.getsize(db_path) / 1024
                    logger.info(f"VACUUM completato. Nuova dimensione: {new_size_kb:.2f}KB")
                    
        except Exception as e:
            logger.error(f"Errore durante il VACUUM: {str(e)}")

    def update_last_save_info(self):
        """Aggiorna le informazioni sull'ultimo salvataggio"""
        self.main_window.status_manager.update_last_save_info()

    def reload_database(self):
        """Ricarica il database e aggiorna le informazioni"""
        try:
            # Salva lo stato corrente se necessario
            if self.main_window.settings.value("autosave_on_cloud_change", True, type=bool):
                self.save_reservations(show_message=False)
            
            # Ricarica le prenotazioni
            selected_date = self.main_window.calendar.selectedDate()
            self.main_window.reservations_widget.load_reservations(selected_date)
            
            # Aggiorna le informazioni
            self.update_db_info()
            self.update_last_save_info()
            
            # Aggiorna la status bar
            self.main_window.status_manager.show_message(
                f"Database ricaricato: {selected_date.toString('dd/MM/yyyy')}", 
                3000
            )
            
        except Exception as e:
            self.main_window._handle_error("la ricarica del database", e) 
    
    def save_all(self):
        """Salva tutto lo stato del database"""
        try:
            # Trova e salva le impostazioni aperte
            dialog = self.main_window.findChild(DailyReservationsDialog)
            if dialog:
                dialog.save_reservations(
                    table=dialog.reservations_table,
                    date=dialog.date_edit.date().toString("yyyy-MM-dd"),
                    show_dialog=False
                )
            # Esegui VACUUM se serve
            self._check_and_vacuum(QDate.currentDate().toString("yyyy-MM-dd"))

            #Aggiorna l'ultimo salvataggio
            current_time = datetime.now().strftime("%H:%M:%S")
            self.main_window.settings.setValue("last_save_time", current_time)
            self.main_window.status_manager.update_last_save_info()

            return True
        
        except Exception as e:
            logger.error(f"Errore durante il salvataggio completo: {str(e)}")
            return False
