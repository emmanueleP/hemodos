from dialog_base import HemodosDialog
from PyQt5.QtWidgets import (QVBoxLayout, QTableWidget, QTableWidgetItem,
                            QPushButton, QHBoxLayout, QTabWidget, QWidget, QComboBox, QLabel, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from database import get_history, get_db_path, get_history_db_path
import sqlite3
from datetime import datetime
import os

class HistoryDialog(HemodosDialog):
    def __init__(self, parent=None):
        super().__init__(parent, "Cronologia")
        self.setMinimumSize(800, 500)  # Finestra più grande
        self.init_ui()

    def init_ui(self):
        # Layout principale
        layout = QVBoxLayout()
        
        # Header con selezione anno e pulsante elimina
        header_layout = QHBoxLayout()
        
        # Selezione anno
        year_group = QHBoxLayout()
        year_group.addWidget(QLabel("Anno:"))
        self.year_combo = QComboBox()
        self.load_available_years()
        self.year_combo.currentTextChanged.connect(self.load_history)
        year_group.addWidget(self.year_combo)
        header_layout.addLayout(year_group)
        
        # Pulsante elimina con icona cestino
        delete_btn = QPushButton()
        delete_btn.setFixedSize(40, 40)
        
        # Carica l'icona del cestino
        icon_path = os.path.join(os.path.dirname(get_db_path()), "assets", "trash.png")
        if os.path.exists(icon_path):
            delete_btn.setIcon(QIcon(icon_path))
            delete_btn.setIconSize(QSize(20, 20))
        else:
            delete_btn.setText("🗑️")
        
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                border: 2px solid #004d4d;  /* Bordo color petrolio */
                border-radius: 4px;         /* Bordi leggermente arrotondati */
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #ff0000;
                border-color: #006666;      /* Bordo più chiaro in hover */
            }
        """)
        delete_btn.setToolTip("Elimina cronologia dell'anno")
        delete_btn.clicked.connect(self.delete_history)
        header_layout.addWidget(delete_btn)
        
        self.content_layout.addLayout(header_layout)
        
        # Tabella cronologia
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(3)
        self.history_table.setHorizontalHeaderLabels(["Data e Ora", "Azione", "Dettagli"])
        self.history_table.setColumnWidth(0, 150)
        self.history_table.setColumnWidth(1, 150)
        self.history_table.setColumnWidth(2, 450)
        self.history_table.setAlternatingRowColors(True)
        self.content_layout.addWidget(self.history_table)
        
        # Carica i dati
        self.load_history()

    def load_available_years(self):
        """Carica gli anni disponibili nei file di cronologia"""
        base_path = os.path.dirname(get_db_path())
        years = []
        
        # Cerca tutti i file cronologia_*.db
        for filename in os.listdir(base_path):
            if filename.startswith("cronologia_") and filename.endswith(".db"):
                try:
                    year = int(filename.split("_")[1].split(".")[0])
                    years.append(year)
                except:
                    continue
        
        # Se non ci sono anni, usa l'anno corrente
        if not years:
            years = [datetime.now().year]
        
        # Popola il combo box
        self.year_combo.clear()
        for year in sorted(years, reverse=True):
            self.year_combo.addItem(str(year))

    def load_history(self):
        """Carica la cronologia per l'anno selezionato"""
        try:
            year = int(self.year_combo.currentText())
            results = get_history(year)
            
            self.history_table.setRowCount(len(results))
            for row, (timestamp, action, details) in enumerate(results):
                self.history_table.setItem(row, 0, QTableWidgetItem(timestamp))
                self.history_table.setItem(row, 1, QTableWidgetItem(action))
                self.history_table.setItem(row, 2, QTableWidgetItem(details))
            
        except Exception as e:
            print(f"Errore nel caricamento della cronologia: {str(e)}") 

    def delete_history(self):
        """Elimina la cronologia dell'anno selezionato"""
        year = self.year_combo.currentText()
        
        reply = QMessageBox.warning(
            self,
            "ATTENZIONE!",
            f"Stai per eliminare la cronologia per l'anno {year}.\n"
            "L'operazione è irreversibile.\n\n"
            "Vuoi continuare?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Elimina il file del database della cronologia
                history_db = get_history_db_path(int(year))
                if os.path.exists(history_db):
                    os.remove(history_db)
                    
                    # Aggiorna la lista degli anni disponibili
                    self.load_available_years()
                    
                    # Se non ci sono più anni, mostra tabella vuota
                    if self.year_combo.count() == 0:
                        self.history_table.setRowCount(0)
                    else:
                        # Altrimenti carica la cronologia dell'anno selezionato
                        self.load_history()
                    
                    QMessageBox.information(
                        self,
                        "Successo",
                        f"Cronologia dell'anno {year} eliminata con successo"
                    )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Errore",
                    f"Impossibile eliminare la cronologia: {str(e)}"
                ) 