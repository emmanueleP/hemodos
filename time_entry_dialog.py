from dialog_base import HemodosDialog
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, 
                            QTimeEdit, QMessageBox)
from PyQt5.QtCore import QTime
from database import add_donation_time

class TimeEntryDialog(HemodosDialog):
    def __init__(self, parent=None, selected_date=None):
        super().__init__(parent, "Aggiungi Orario")
        self.selected_date = selected_date
        self.init_ui()

    def init_ui(self):
        # Time selection
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Orario:"))
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")
        self.time_edit.setTimeRange(QTime(7, 50), QTime(12, 10))  # Imposta range orario
        self.time_edit.setMinimumTime(QTime(7, 50))
        self.time_edit.setMaximumTime(QTime(12, 10))
        self.time_edit.setTime(QTime(8, 0))  # Default 8:00
        time_layout.addWidget(self.time_edit)
        self.content_layout.addLayout(time_layout)

    def accept(self):
        time = self.time_edit.time()
        
        # Verifica che l'orario sia a intervalli di 5 minuti
        if time.minute() % 5 != 0:
            QMessageBox.warning(self, "Errore", 
                              "L'orario deve essere a intervalli di 5 minuti")
            return
        
        # Verifica che l'orario non esista già
        if self.parent() and self.orario_exists(time.toString("HH:mm")):
            QMessageBox.warning(self, "Errore", 
                              "Questo orario esiste già nella tabella")
            return

        # Aggiungi l'orario
        time_str = time.toString("HH:mm")
        if add_donation_time(self.selected_date, time_str, "", "", False):
            # Aggiorna la vista principale
            if self.parent():
                self.parent().load_reservations()
                self.parent().highlight_donation_dates()
                self.parent().update_db_info()
            super().accept()
        else:
            QMessageBox.warning(self, "Errore", "Impossibile aggiungere l'orario")

    def orario_exists(self, new_time):
        """Verifica se l'orario esiste già nella tabella"""
        table = self.parent().table
        for row in range(table.rowCount()):
            item = table.item(row, 0)
            if item and item.text() == new_time:
                return True
        return False
