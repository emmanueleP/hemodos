from dialog_base import HemodosDialog
from PyQt5.QtWidgets import (QVBoxLayout, QTableWidget, QTableWidgetItem,
                            QPushButton, QHBoxLayout, QTabWidget, QWidget)
from PyQt5.QtCore import Qt
from database import get_history, get_db_path
import sqlite3
from datetime import datetime

class HistoryDialog(HemodosDialog):
    def __init__(self, parent=None):
        super().__init__(parent, "Cronologia")
        self.setMinimumSize(800, 500)  # Finestra più grande
        self.init_ui()

    def init_ui(self):
        # Crea un tab widget per separare le cronologie
        tab_widget = QTabWidget()
        
        # Tab per le prenotazioni
        reservations_tab = QWidget()
        reservations_layout = QVBoxLayout()
        
        self.reservations_table = QTableWidget()
        self.reservations_table.setColumnCount(3)
        self.reservations_table.setHorizontalHeaderLabels(["Data e Ora", "Azione", "Dettagli"])
        self.reservations_table.setColumnWidth(0, 150)
        self.reservations_table.setColumnWidth(1, 150)
        self.reservations_table.setColumnWidth(2, 450)
        self.reservations_table.setAlternatingRowColors(True)
        reservations_layout.addWidget(self.reservations_table)
        
        reservations_tab.setLayout(reservations_layout)
        tab_widget.addTab(reservations_tab, "Prenotazioni")
        
        # Tab per le date di donazione
        donation_dates_tab = QWidget()
        donation_dates_layout = QVBoxLayout()
        
        self.donation_dates_table = QTableWidget()
        self.donation_dates_table.setColumnCount(3)
        self.donation_dates_table.setHorizontalHeaderLabels(["Data e Ora", "Azione", "Dettagli"])
        self.donation_dates_table.setColumnWidth(0, 150)
        self.donation_dates_table.setColumnWidth(1, 150)
        self.donation_dates_table.setColumnWidth(2, 450)
        self.donation_dates_table.setAlternatingRowColors(True)
        donation_dates_layout.addWidget(self.donation_dates_table)
        
        donation_dates_tab.setLayout(donation_dates_layout)
        tab_widget.addTab(donation_dates_tab, "Date di Donazione")
        
        self.content_layout.addWidget(tab_widget)
        
        # Carica i dati
        self.load_history()

    def load_history(self):
        # Carica cronologia prenotazioni
        self.load_reservations_history()
        
        # Carica cronologia date di donazione
        self.load_donation_dates_history()

    def load_reservations_history(self):
        try:
            db_path = get_db_path(is_donation_dates=False)
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("SELECT timestamp, action, details FROM history ORDER BY timestamp DESC")
            results = c.fetchall()
            conn.close()
            
            self.reservations_table.setRowCount(len(results))
            for row, (timestamp, action, details) in enumerate(results):
                self.reservations_table.setItem(row, 0, QTableWidgetItem(timestamp))
                self.reservations_table.setItem(row, 1, QTableWidgetItem(action))
                self.reservations_table.setItem(row, 2, QTableWidgetItem(details))
        except Exception as e:
            print(f"Errore nel caricamento della cronologia prenotazioni: {str(e)}")

    def load_donation_dates_history(self):
        try:
            db_path = get_db_path(is_donation_dates=True)
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            
            # Crea la tabella history se non esiste
            c.execute('''CREATE TABLE IF NOT EXISTS history
                         (timestamp text, action text, details text)''')
            
            c.execute("SELECT timestamp, action, details FROM history ORDER BY timestamp DESC")
            results = c.fetchall()
            conn.close()
            
            self.donation_dates_table.setRowCount(len(results))
            for row, (timestamp, action, details) in enumerate(results):
                self.donation_dates_table.setItem(row, 0, QTableWidgetItem(timestamp))
                self.donation_dates_table.setItem(row, 1, QTableWidgetItem(action))
                self.donation_dates_table.setItem(row, 2, QTableWidgetItem(details))
        except Exception as e:
            print(f"Errore nel caricamento della cronologia date di donazione: {str(e)}") 