from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QTableWidget, QTableWidgetItem, QStatusBar
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from gui.widgets.reservations_widget import ReservationsWidget
from core.database import add_donation_time
from gui.dialogs.time_entry_dialog import TimeEntryDialog
from core.utils import print_data
import os

class DailyReservationsDialog(QDialog):
    def __init__(self, main_window, selected_date):
        super().__init__(main_window)
        self.main_window = main_window
        self.selected_date = selected_date
        
        self.setWindowTitle(f"Prenotazioni del {selected_date.toString('dd/MM/yyyy')}")
        self.setMinimumSize(890, 800)  
        
        # Layout principale
        layout = QVBoxLayout(self)
        
        # Toolbar
        self._init_toolbar(layout)
        
        # Widget prenotazioni
        self.reservations_widget = ReservationsWidget(main_window)
        layout.addWidget(self.reservations_widget)
        
        # Status Bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("QStatusBar { border-top: 1px solid #ccc; }")
        layout.addWidget(self.status_bar)
        
        # Carica i dati
        self.reservations_widget.load_reservations(selected_date)
        
        # Mostra messaggio iniziale nella status bar
        self.show_status_message("Pronto")
        
    def _init_toolbar(self, layout):
        """Inizializza la toolbar con i pulsanti"""
        toolbar = QHBoxLayout()
        
        buttons = [
            ("add_time.png", "Aggiungi orario", self.show_time_entry_dialog),
            ("diskette.png", "Salva (Ctrl+S)", self.save_reservations),
            ("trash.png", "Elimina prenotazione", self.delete_reservation),
            ("doc.png", "Esporta in docx", lambda: self.main_window.export_manager.export_to_docx(self.reservations_widget)),
            ("printer.png", "Stampa", self.print_reservations)
        ]
        
        for icon_name, tooltip, callback in buttons:
            button = QPushButton()
            button.setIcon(QIcon(f'assets/{icon_name}'))
            button.setIconSize(QSize(24, 24))
            button.setToolTip(tooltip)
            button.clicked.connect(callback)
            button.setFixedSize(36, 36)
            toolbar.addWidget(button)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
    def show_time_entry_dialog(self):
        """Mostra il dialog per l'inserimento degli orari"""
        dialog = TimeEntryDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            time = dialog.get_time()
            date = self.selected_date.toString("yyyy-MM-dd")
            if add_donation_time(date, time):
                self.reservations_widget.load_reservations(self.selected_date)
                self.main_window.calendar_manager.highlight_donation_dates() 

    def show_status_message(self, message, timeout=0):
        """Mostra un messaggio nella status bar"""
        self.status_bar.showMessage(message, timeout)

    def save_reservations(self):
        """Salva le prenotazioni correnti"""
        if self.main_window.database_manager.save_reservations(
            self.reservations_widget.get_table(),
            self.selected_date.toString("yyyy-MM-dd"),
            True
        ):
            self.show_status_message("Salvataggio completato", 3000)
            return True
        else:
            self.show_status_message("Errore durante il salvataggio", 3000)
            return False

    def delete_reservation(self):
        """Elimina la prenotazione selezionata"""
        table = self.reservations_widget.get_table()
        if self.main_window.database_manager.delete_reservation(
            table,
            table.currentRow()
        ):
            self.show_status_message("Prenotazione eliminata", 3000)
        else:
            self.show_status_message("Errore durante l'eliminazione", 3000) 

    def print_reservations(self):
        """Stampa le prenotazioni"""
        self.main_window.print_manager.print_reservations(self)

    def _collect_table_data(self):
        """Raccoglie i dati dalla tabella"""
        data = []
        table = self.reservations_widget.get_table()
        
        for row in range(table.rowCount()):
            time = table.item(row, 0).text()
            name = table.item(row, 1).text() if table.item(row, 1) else ""
            surname = table.item(row, 2).text() if table.item(row, 2) else ""
            first_donation = table.cellWidget(row, 3).currentText()
            stato = table.cellWidget(row, 4).currentText()
            
            if name.strip() or surname.strip():
                data.append([time, name, surname, first_donation, stato])
                
        return data 
    