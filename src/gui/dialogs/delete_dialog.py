from gui.dialogs.base_dialog import HemodosDialog
from PyQt5.QtWidgets import (QVBoxLayout, QTreeWidget, QTreeWidgetItem, 
                            QPushButton, QHBoxLayout, QMessageBox)
from PyQt5.QtCore import Qt, QSettings
import os
from datetime import datetime

class DeleteFilesDialog(HemodosDialog):
    def __init__(self, parent=None):
        super().__init__(parent, "Elimina Database")
        self.init_ui()

    def init_ui(self):
        # Tree widget per mostrare i file
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Anno", "Data Modifica", "Dimensione"])
        self.tree.setSelectionMode(QTreeWidget.SingleSelection)  # Solo selezione singola
        self.content_layout.addWidget(self.tree)

        # Pulsanti
        button_layout = QHBoxLayout()
        delete_btn = QPushButton("Elimina Database")
        delete_btn.clicked.connect(self.delete_selected)
        delete_btn.setStyleSheet(self.button_style)
        button_layout.addWidget(delete_btn)
        self.content_layout.addLayout(button_layout)

        # Carica i file
        self.load_files()

    def load_files(self):
        base_dir = self._get_base_dir()
        if not base_dir or not os.path.exists(base_dir):
            QMessageBox.warning(self, "Attenzione", 
                              f"La directory {base_dir} non esiste ancora.\n"
                              "Nessun database da eliminare.")
            return

        try:
            self.tree.clear()
            for year in sorted(os.listdir(base_dir)):
                year_path = os.path.join(base_dir, year)
                if os.path.isdir(year_path):
                    db_file = f"hemodos_{year}.db"
                    db_path = os.path.join(year_path, db_file)
                    
                    if os.path.exists(db_path):
                        mod_time = datetime.fromtimestamp(
                            os.path.getmtime(db_path)
                        ).strftime("%d/%m/%Y %H:%M")
                        size = f"{os.path.getsize(db_path) / 1024:.1f} KB"
                        
                        item = QTreeWidgetItem([year, mod_time, size])
                        item.setData(0, Qt.UserRole, db_path)
                        self.tree.addTopLevelItem(item)

            self.tree.expandAll()
        except Exception as e:
            QMessageBox.warning(self, "Errore", f"Errore nel caricamento dei file: {str(e)}")

    def _get_base_dir(self):
        settings = QSettings('Hemodos', 'DatabaseSettings')
        service = settings.value("cloud_service", "Locale")
        
        if service == "Locale":
            return os.path.expanduser("~/Documents/Hemodos")
        else:
            return os.path.join(settings.value("cloud_path", ""), "Hemodos")

    def delete_selected(self):
        selected_items = self.tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Attenzione", "Seleziona un anno da eliminare")
            return

        item = selected_items[0]  # Prendiamo il primo (e unico) item selezionato
        year = item.text(0)
        db_path = item.data(0, Qt.UserRole)

        # Prima conferma
        reply = QMessageBox.warning(
            self,
            "Conferma eliminazione",
            f"Stai per eliminare il database dell'anno {year}.\n\n"
            "Questa operazione non può essere annullata.\n"
            "Sei sicuro di voler procedere?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Seconda conferma con anno specifico
            confirm = QMessageBox.critical(
                self,
                "Conferma definitiva",
                f"ATTENZIONE! Procedendo verranno persi tutti i dati per l'anno {year}.\n\n"
                "Vuoi davvero eliminare definitivamente il database?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if confirm == QMessageBox.Yes:
                try:
                    os.remove(db_path)
                    self.load_files()  # Ricarica la lista
                    QMessageBox.information(self, "Successo", f"Database dell'anno {year} eliminato con successo")
                except Exception as e:
                    QMessageBox.warning(
                        self,
                        "Errore",
                        f"Errore nell'eliminazione del database: {str(e)}"
                    )