from gui.dialogs.base_dialog import HemodosDialog
from PyQt5.QtWidgets import (QVBoxLayout, QTableWidget, QTableWidgetItem,
                            QPushButton, QHBoxLayout, QComboBox, QLabel, QMessageBox)
from PyQt5.QtCore import Qt, QDate, QSettings, QSize
from PyQt5.QtGui import QIcon
import os
import sqlite3
from datetime import datetime
from core.database import get_db_path
from core.delete_db_logic import get_available_years, get_base_path
from core.logger import logger

class HistoryDialog(HemodosDialog):
    def __init__(self, parent=None):
        super().__init__(parent, "Cronologia Prenotazioni")
        self.settings = QSettings('Hemodos', 'DatabaseSettings')
        self.setMinimumSize(850, 600)
        self.resize(850, 600)
        self.init_ui()

    def init_ui(self):
        # Layout principale
        layout = QVBoxLayout()
        
        # Header con selezione anno
        header_layout = QHBoxLayout()
        
        # Selezione anno
        year_label = QLabel("Anno:")
        header_layout.addWidget(year_label)
        
        self.year_combo = QComboBox()
        available_years = get_available_years()
        if available_years:
            for year in sorted(available_years, reverse=True):
                self.year_combo.addItem(str(year))
        else:
            current_year = datetime.now().year
            self.year_combo.addItem(str(current_year))
            
        self.year_combo.currentTextChanged.connect(self.load_history)
        header_layout.addWidget(self.year_combo)
        
        header_layout.addStretch()
        
        # Pulsante elimina
        delete_btn = QPushButton()
        delete_btn.setIcon(QIcon('src/assets/trash.png'))
        delete_btn.setIconSize(QSize(24, 24))
        delete_btn.setToolTip("Elimina cronologia dell'anno")
        delete_btn.clicked.connect(self.delete_history)
        delete_btn.setFixedSize(36, 36)
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
        
        # Applica il tema alla tabella
        if self.parent().theme_manager.get_current_theme().name == "dark":
            self.history_table.setStyleSheet("""
                QTableWidget {
                    background-color: #2b2b2b;
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
                    background-color: #353535;
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
            
            # Ottieni il percorso base dell'anno
            base_path = get_base_path()
            year_path = os.path.join(base_path, str(year))
            
            # Crea la directory dell'anno se non esiste
            os.makedirs(year_path, exist_ok=True)
            
            # Crea/verifica il database principale della cronologia
            history_db_path = os.path.join(year_path, f"cronologia_{year}.db")
            
            # Crea la tabella history se non esiste
            conn = sqlite3.connect(history_db_path)
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS history
                        (timestamp text, action text, details text)''')
            conn.commit()
            
            # Raccogli la cronologia da tutti i database dell'anno
            all_history = []
            
            # Prima dal database principale della cronologia
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

    def delete_history(self):
        """Elimina la cronologia dell'anno corrente"""
        try:
            reply = QMessageBox.question(
                self,
                'Conferma eliminazione',
                'Sei sicuro di voler eliminare tutta la cronologia di quest\'anno?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Ottieni l'anno corrente
                current_year = QDate.currentDate().year()
                
                # Percorso del database cronologia
                base_path = get_base_path()
                db_path = os.path.join(base_path, str(current_year), f"cronologia_{current_year}.db")
                
                # Elimina i dati dalla tabella
                conn = sqlite3.connect(db_path)
                c = conn.cursor()
                c.execute("DELETE FROM history")
                conn.commit()
                conn.close()
                
                # Aggiorna la visualizzazione
                self.load_history()
                
                QMessageBox.information(
                    self,
                    "Successo",
                    "Cronologia eliminata con successo"
                )
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore durante l'eliminazione della cronologia: {str(e)}"
            ) 