from gui.dialogs.base_dialog import HemodosDialog
from PyQt5.QtWidgets import (QVBoxLayout, QTableWidget, QTableWidgetItem,
                            QPushButton, QHBoxLayout, QComboBox, QLabel)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import os
from core.database import get_history, get_db_path
from core.delete_db_logic import get_available_years
import sqlite3
from datetime import datetime
from core.logger import logger

class HistoryDialog(HemodosDialog):
    def __init__(self, parent=None):
        super().__init__(parent, "Cronologia")
        self.setMinimumSize(800, 500)
        self.init_ui()

    def init_ui(self):
        # Header con selezione anno
        header_layout = QHBoxLayout()
        
        # Selezione anno
        year_group = QHBoxLayout()
        year_label = QLabel("Anno:")
        year_label.setStyleSheet("color: #ffffff;")  # Testo bianco per tema scuro
        year_group.addWidget(year_label)
        
        self.year_combo = QComboBox()
        self.year_combo.setStyleSheet("""
            QComboBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #404040;
                padding: 5px;
                border-radius: 3px;
                min-width: 100px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: url(assets/arrow_down.png);
                width: 12px;
                height: 12px;
            }
            QComboBox:hover {
                border-color: #006666;
            }
        """)
        
        # Carica gli anni disponibili
        available_years = get_available_years()
        if available_years:
            for year in available_years:
                self.year_combo.addItem(str(year))
        else:
            current_year = datetime.now().year
            self.year_combo.addItem(str(current_year))
            
        self.year_combo.currentTextChanged.connect(self.load_history)
        year_group.addWidget(self.year_combo)
        header_layout.addLayout(year_group)
        
        header_layout.addStretch()
        self.content_layout.addLayout(header_layout)
        
        # Tabella cronologia
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(3)
        self.history_table.setHorizontalHeaderLabels(["Data e Ora", "Azione", "Dettagli"])
        self.history_table.setColumnWidth(0, 150)
        self.history_table.setColumnWidth(1, 150)
        self.history_table.setColumnWidth(2, 450)
        self.history_table.setAlternatingRowColors(True)
        
        # Stile per la tabella
        self.history_table.setStyleSheet("""
            QTableWidget {
                background-color: #1a1a1a;
                color: #ffffff;
                gridline-color: #404040;
                border: 1px solid #404040;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #004d4d;
            }
            QHeaderView::section {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 5px;
                border: 1px solid #404040;
            }
            QTableWidget::item:alternate {
                background-color: #262626;
            }
        """)
        
        self.content_layout.addWidget(self.history_table)
        
        # Carica i dati iniziali
        self.load_history()

    def load_history(self):
        """Carica la cronologia per l'anno selezionato"""
        try:
            year = int(self.year_combo.currentText())
            self.history_table.setRowCount(0)
            
            # Crea una data fittizia per l'anno
            from PyQt5.QtCore import QDate
            dummy_date = QDate(year, 1, 1)
            
            # Ottieni il percorso base dell'anno
            year_path = os.path.dirname(get_db_path(dummy_date))
            
            # Crea la directory dell'anno se non esiste
            os.makedirs(year_path, exist_ok=True)
            
            # Crea/verifica il database principale della cronologia
            history_db_path = os.path.join(year_path, f"cronologia_{year}.db")
            if not os.path.exists(history_db_path):
                conn = sqlite3.connect(history_db_path)
                c = conn.cursor()
                c.execute('''CREATE TABLE IF NOT EXISTS history
                            (timestamp text, action text, details text)''')
                conn.commit()
                conn.close()
                logger.info(f"Creato nuovo database cronologia per l'anno {year}")
            
            # Raccogli la cronologia da tutti i database dell'anno
            all_history = []
            
            # Prima dal database principale della cronologia
            conn = sqlite3.connect(history_db_path)
            c = conn.cursor()
            c.execute("SELECT * FROM history ORDER BY timestamp DESC")
            all_history.extend(c.fetchall())
            conn.close()
            
            # Poi da tutti gli altri database dell'anno
            for filename in os.listdir(year_path):
                if filename.endswith('.db') and not filename.startswith('cronologia_'):
                    db_path = os.path.join(year_path, filename)
                    try:
                        conn = sqlite3.connect(db_path)
                        c = conn.cursor()
                        c.execute('''CREATE TABLE IF NOT EXISTS history
                                    (timestamp text, action text, details text)''')
                        c.execute("SELECT * FROM history ORDER BY timestamp DESC")
                        all_history.extend(c.fetchall())
                        conn.close()
                    except sqlite3.Error as e:
                        logger.error(f"Errore nel leggere {filename}: {str(e)}")
                        continue
            
            # Ordina per timestamp decrescente e rimuovi duplicati
            all_history.sort(key=lambda x: x[0], reverse=True)
            unique_history = []
            seen = set()
            for entry in all_history:
                if entry not in seen:
                    unique_history.append(entry)
                    seen.add(entry)
            
            # Popola la tabella
            for timestamp, action, details in unique_history:
                row = self.history_table.rowCount()
                self.history_table.insertRow(row)
                
                # Formatta il timestamp
                dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                formatted_date = dt.strftime("%d/%m/%Y %H:%M")
                
                self.history_table.setItem(row, 0, QTableWidgetItem(formatted_date))
                self.history_table.setItem(row, 1, QTableWidgetItem(action))
                self.history_table.setItem(row, 2, QTableWidgetItem(details))
                
        except Exception as e:
            logger.error(f"Errore nel caricamento della cronologia: {str(e)}") 