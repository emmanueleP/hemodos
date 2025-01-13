from gui.dialogs.base_dialog import HemodosDialog
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                            QGroupBox, QCheckBox, QProgressBar, QMessageBox)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QIcon
import os
from core.updater import UpdateChecker
from core.logger import logger

class UpdateDialog(HemodosDialog):
    def __init__(self, parent=None):
        super().__init__(parent, "Aggiornamenti")
        self.settings = QSettings('Hemodos', 'DatabaseSettings')
        self.checker = None
        #Rimuovi ok e annulla da HemodosDialog
        for i in reversed(range(self.buttons_layout.count())):
            widget = self.buttons_layout.itemAt(i).widget()
            if isinstance(widget, QPushButton):
                widget.setParent(None)
                widget.deleteLater()
        self.init_ui()

    def init_ui(self):
        # Gruppo controllo aggiornamenti
        update_group = QGroupBox("Controllo Aggiornamenti")
        update_layout = QVBoxLayout()

        # Checkbox per il controllo automatico
        self.auto_check = QCheckBox("Controlla automaticamente gli aggiornamenti")
        self.auto_check.setChecked(self.settings.value("check_updates", True, type=bool))
        update_layout.addWidget(self.auto_check)

        # Versione corrente
        version_label = QLabel(f"Versione corrente: {self.get_current_version()}")
        update_layout.addWidget(version_label)

        # Pulsante controllo manuale
        check_button = QPushButton("Controlla aggiornamenti")
        check_button.clicked.connect(self.check_updates_manually)
        update_layout.addWidget(check_button)

        # Progress bar (inizialmente nascosta)
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        update_layout.addWidget(self.progress_bar)

        update_group.setLayout(update_layout)
        self.content_layout.addWidget(update_group)

        # Aggiungi spazio elastico
        self.content_layout.addStretch()

    def get_current_version(self):
        """Restituisce la versione corrente dell'applicazione"""
        return "1.0.6"

    def check_updates_manually(self):
        """Controlla manualmente gli aggiornamenti"""
        try:
            self.progress_bar.show()
            self.progress_bar.setRange(0, 0)
            
            # Se c'è già un checker attivo, fermalo
            if self.checker is not None:
                self.checker.stop()
                self.checker.deleteLater()
            
            # Crea il nuovo checker
            self.checker = UpdateChecker(
                current_version=self.get_current_version(),
                owner="emmanueleP",
                repo="hemodos",
                main_window=self.parent()
            )
            self.checker.update_available.connect(self.show_update_available)
            self.checker.no_update_available.connect(self.show_no_update)
            self.checker.error_occurred.connect(self.show_check_error)
            self.checker.start()
            
        except Exception as e:
            logger.error(f"Errore nel controllo aggiornamenti: {str(e)}")
            self.show_check_error(str(e))

    def show_update_available(self, version, notes, url):
        """Mostra il dialogo quando è disponibile un aggiornamento"""
        self.progress_bar.hide()
        reply = QMessageBox.question(
            self,
            "Aggiornamento Disponibile",
            f"È disponibile la versione {version}.\n\nNote di rilascio:\n{notes}\n\nVuoi aggiornare ora?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            # Avvia l'aggiornamento
            self.start_update(url)

    def show_no_update(self):
        """Mostra il messaggio quando non ci sono aggiornamenti"""
        self.progress_bar.hide()
        QMessageBox.information(
            self,
            "Nessun Aggiornamento",
            "Stai utilizzando l'ultima versione disponibile."
        )

    def show_check_error(self, error):
        """Mostra il messaggio di errore"""
        self.progress_bar.hide()
        QMessageBox.warning(
            self,
            "Errore",
            f"Errore nel controllo degli aggiornamenti:\n{error}"
        )

    def accept(self):
        """Salva le impostazioni quando si chiude il dialog"""
        self.settings.setValue("check_updates", self.auto_check.isChecked())
        super().accept() 

    def closeEvent(self, event):
        """Gestisce la chiusura del dialog"""
        if self.checker is not None:
            self.checker.stop()
            self.checker.deleteLater()
        super().closeEvent(event) 