from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                            QComboBox, QGroupBox, QMessageBox)
from PyQt5.QtCore import QTime, Qt, QDate
from core.logger import logger
from core.database import get_reservations, add_reservation, save_donation_status
from datetime import datetime
from core.database import delete_reservation_from_db

class ReservationsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.init_ui()
        self.load_default_times()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Tabella prenotazioni
        table_group = QGroupBox("Prenotazioni")
        table_layout = QVBoxLayout()
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Orario", "Nome", "Cognome", "Prima Donazione", "Stato"
        ])
        
        # Imposta le dimensioni delle colonne
        self.table.setColumnWidth(0, 100)  # Orario
        self.table.setColumnWidth(1, 200)  # Nome
        self.table.setColumnWidth(2, 200)  # Cognome
        self.table.setColumnWidth(3, 120)  # Prima Donazione
        self.table.setColumnWidth(4, 150)  # Stato
        
        # Connetti solo il segnale cellChanged
        self.table.cellChanged.connect(self.on_cell_changed)
        
        table_layout.addWidget(self.table)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

    def load_default_times(self):
        """Carica gli orari predefiniti nella tabella"""
        try:
            # Genera tutti gli orari possibili dalle 7:50 alle 12:10 con intervalli di 5 minuti
            start_time = QTime(7, 50)
            end_time = QTime(12, 10)
            current_time = start_time
            default_times = []
            
            while current_time <= end_time:
                default_times.append(current_time.toString("HH:mm"))
                current_time = current_time.addSecs(5 * 60)  # Aggiungi 5 minuti
            
            # Ottieni gli orari esistenti dal database
            selected_date = self.main_window.calendar.selectedDate()
            if isinstance(selected_date, str):
                selected_date = QDate.fromString(selected_date, "yyyy-MM-dd")
            
            reservations = get_reservations(selected_date)
            existing_times = [res[0] for res in reservations]
            
            # Unisci tutti gli orari
            all_times = list(set(default_times + existing_times))
            
            # Converti in oggetti QTime per un ordinamento corretto
            time_objects = [(QTime.fromString(t, "HH:mm"), t) for t in all_times]
            time_objects.sort(key=lambda x: x[0])  # Ordina per orario
            
            # Filtra gli orari per mantenere solo quelli nel range desiderato
            filtered_times = [t[1] for t in time_objects 
                             if start_time <= t[0] <= end_time]
            
            # Popola la tabella
            self.table.setRowCount(len(filtered_times))
            for row, time in enumerate(filtered_times):
                self.table.setItem(row, 0, QTableWidgetItem(time))
                
                # Aggiungi le combo box
                self.setup_combo_boxes(row, time)
                
        except Exception as e:
            logger.error(f"Errore nel caricamento degli orari predefiniti: {str(e)}")
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore nel caricamento degli orari predefiniti: {str(e)}"
            )

    def setup_combo_boxes(self, row, time):
        """Configura le combo box per prima donazione e stato"""
        # ComboBox per Prima Donazione
        first_combo = QComboBox()
        first_combo.addItems(["No", "Sì"])
        
        # Se l'orario è dalle 10:00 in poi, imposta "No" e disabilita il ComboBox
        time_obj = QTime.fromString(time, "HH:mm")
        if time_obj >= QTime(10, 0):
            first_combo.setCurrentText("No")
            first_combo.setEnabled(False)
            first_combo.setStyleSheet("""
                QComboBox {
                    background-color: #f0f0f0;
                    color: #666666;
                }
            """)
        
        self.table.setCellWidget(row, 3, first_combo)
        
        # ComboBox per lo Stato
        stato_combo = QComboBox()
        stato_combo.addItems([
            "Non effettuata",
            "Sì",
            "No",
            "Non presentato",
            "Donazione interrotta"
        ])
        stato_combo.currentTextChanged.connect(
            lambda text, r=row: self.on_status_changed(r, text)
        )
        self.table.setCellWidget(row, 4, stato_combo)

    def on_cell_changed(self, row, column):
        """Gestisce i cambiamenti nelle celle della tabella"""
        try:
            if column in [1, 2]:  # Nome o Cognome
                self.save_reservation(row)
        except Exception as e:
            logger.error(f"Errore nella gestione del cambio cella: {str(e)}")

    def on_status_changed(self, row, new_status):
        """Gestisce il cambio di stato di una donazione"""
        try:
            time = self.table.item(row, 0).text()
            name = self.table.item(row, 1).text() if self.table.item(row, 1) else ""
            surname = self.table.item(row, 2).text() if self.table.item(row, 2) else ""
            
            if name.strip() or surname.strip():
                # Converti la data nel formato corretto
                selected_date = self.main_window.calendar.selectedDate()
                date_str = selected_date.toString("yyyy-MM-dd")
                save_donation_status(date_str, time, new_status)
                
        except Exception as e:
            logger.error(f"Errore nel salvataggio dello stato: {str(e)}")
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore nel salvataggio dello stato: {str(e)}"
            )

    def save_reservation(self, row):
        """Salva una prenotazione nel database"""
        try:
            time = self.table.item(row, 0).text()
            name = self.table.item(row, 1).text() if self.table.item(row, 1) else ""
            surname = self.table.item(row, 2).text() if self.table.item(row, 2) else ""
            first_donation = self.table.cellWidget(row, 3).currentText() == "Sì"
            
            # Converti la data nel formato corretto
            selected_date = self.main_window.calendar.selectedDate()
            date_str = selected_date.toString("yyyy-MM-dd")
            
            add_reservation(date_str, time, name, surname, first_donation)
            
        except Exception as e:
            logger.error(f"Errore nel salvataggio della prenotazione: {str(e)}")
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore nel salvataggio della prenotazione: {str(e)}"
            )

    def delete_reservation(self, row):
        """Elimina una prenotazione dal database"""
        time = self.table.item(row, 0).text()
        delete_reservation_from_db(self.main_window.calendar.selectedDate(), time)
        self.load_default_times()

    def clear_table(self):
        """Pulisce la tabella"""
        self.table.setRowCount(0)

    def get_table(self):
        """Restituisce il riferimento alla tabella"""
        return self.table

    def load_reservations(self, selected_date):
        """Carica le prenotazioni per una data specifica"""
        try:
            self.clear_table()
            
            # Assicurati che selected_date sia un oggetto QDate
            if isinstance(selected_date, str):
                selected_date = QDate.fromString(selected_date, "yyyy-MM-dd")
            
            # Carica gli orari predefiniti e le prenotazioni esistenti
            self.load_default_times()
            
            # Ottieni le prenotazioni dal database
            reservations = get_reservations(selected_date)
            
            # Popola la tabella con le prenotazioni esistenti
            for time, name, surname, first_donation, stato in reservations:
                for row in range(self.table.rowCount()):
                    if self.table.item(row, 0) and self.table.item(row, 0).text() == time:
                        self.table.setItem(row, 1, QTableWidgetItem(name))
                        self.table.setItem(row, 2, QTableWidgetItem(surname))
                        
                        first_combo = self.table.cellWidget(row, 3)
                        first_combo.setCurrentText("Sì" if first_donation else "No")
                        
                        stato_combo = self.table.cellWidget(row, 4)
                        stato_combo.setCurrentText(stato)
                        break
                        
        except Exception as e:
            logger.error(f"Errore nel caricamento delle prenotazioni: {str(e)}")
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore nel caricamento delle prenotazioni: {str(e)}"
            ) 