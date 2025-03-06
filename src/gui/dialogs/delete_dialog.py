from gui.dialogs.base_dialog import HemodosDialog
from PyQt5.QtWidgets import (QVBoxLayout, QTreeWidget, QTreeWidgetItem, 
                            QPushButton, QHBoxLayout, QMessageBox)
from PyQt5.QtCore import Qt
from core.delete_db_logic import get_available_years, delete_year_directory
from core.logger import logger
from PyQt5.QtGui import QIcon

class DeleteFilesDialog(HemodosDialog):
    def __init__(self, parent=None):
        super().__init__(parent, "Elimina Database")
        self.init_ui()

    def init_ui(self):
        # Tree widget per mostrare gli anni
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Anni disponibili")
        self.content_layout.addWidget(self.tree)
        
        # Carica gli anni
        self.load_years()
        
        # Pulsante elimina
        delete_btn = QPushButton("Elimina")
        delete_btn.setStyleSheet(self.button_style)
        delete_btn.clicked.connect(self.delete_selected)
        
        # Icone dei pulsanti
        delete_btn.setIcon(QIcon(self.paths_manager.get_asset_path('delete_64px.png')))
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(delete_btn)
        self.content_layout.addLayout(btn_layout)

    def load_years(self):
        """Carica la lista degli anni disponibili"""
        self.tree.clear()
        for year in get_available_years():
            item = QTreeWidgetItem([str(year)])
            self.tree.addTopLevelItem(item)

    def delete_selected(self):
        """Elimina l'anno selezionato"""
        selected = self.tree.currentItem()
        if not selected:
            QMessageBox.warning(
                self,
                "Attenzione",
                "Seleziona un anno da eliminare"
            )
            return
            
        year = int(selected.text(0))
        
        # Chiedi conferma
        reply = QMessageBox.question(
            self,
            "Conferma eliminazione",
            f"Vuoi davvero eliminare tutti i dati dell'anno {year}?\n"
            "Questa operazione non può essere annullata.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if delete_year_directory(year):
                    # Rimuovi dall'albero
                    self.tree.takeTopLevelItem(
                        self.tree.indexOfTopLevelItem(selected)
                    )
                    QMessageBox.information(
                        self,
                        "Successo",
                        f"Tutti i dati dell'anno {year} sono stati eliminati"
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Attenzione",
                        f"Directory dell'anno {year} non trovata"
                    )
                    
            except Exception as e:
                logger.error(f"Errore nell'eliminazione dell'anno {year}: {str(e)}")
                QMessageBox.critical(
                    self,
                    "Errore",
                    f"Errore nell'eliminazione dell'anno {year}: {str(e)}"
                )