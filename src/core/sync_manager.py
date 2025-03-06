import os
import shutil
from PyQt5.QtWidgets import QDialog, QProgressBar, QLabel, QVBoxLayout, QPushButton, QMessageBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from core.logger import logger

class SyncWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self, source_dir, dest_dir):
        super().__init__()
        self.source_dir = source_dir
        self.dest_dir = dest_dir
        
    def run(self):
        try:
            # Lista tutti i file da sincronizzare
            files_to_sync = []
            for root, _, files in os.walk(self.source_dir):
                for file in files:
                    source_path = os.path.join(root, file)
                    rel_path = os.path.relpath(source_path, self.source_dir)
                    dest_path = os.path.join(self.dest_dir, rel_path)
                    files_to_sync.append((source_path, dest_path))
            
            total_files = len(files_to_sync)
            for i, (source, dest) in enumerate(files_to_sync):
                # Crea le directory necessarie
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                # Copia il file
                shutil.copy2(source, dest)
                # Aggiorna il progresso
                progress = int((i + 1) / total_files * 100)
                self.progress.emit(progress)
                
            self.finished.emit()
            
        except Exception as e:
            logger.error(f"Errore durante la sincronizzazione: {str(e)}")
            self.error.emit(str(e))

class SyncDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sincronizzazione")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)
        self.setModal(True)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.label = QLabel("Sincronizzazione in corso con il cloud...\nNon chiudere l'applicazione.")
        layout.addWidget(self.label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        layout.addWidget(self.progress_bar)
        
        self.cancel_button = QPushButton("Annulla")
        self.cancel_button.clicked.connect(self.reject)
        layout.addWidget(self.cancel_button)
        
    def update_progress(self, value):
        self.progress_bar.setValue(value)
        
    def sync_completed(self):
        self.label.setText("Sincronizzazione completata!")
        self.cancel_button.setText("Chiudi")
        
    def sync_error(self, error_msg):
        QMessageBox.critical(self, "Errore", f"Errore durante la sincronizzazione:\n{error_msg}")
        self.reject()

class CloudSync:
    def __init__(self, paths_manager):
        self.paths_manager = paths_manager
        
    def sync_on_exit(self, parent_widget=None):
        """
        Esegue la sincronizzazione prima della chiusura dell'app
        
        Returns:
            bool: True se la sincronizzazione è avvenuta con successo o è stata annullata
        """
        cloud_path = self.paths_manager.get_cloud_path()
        if not cloud_path:
            return True
            
        # Chiedi conferma solo se il salvataggio automatico è disattivato
        if not self.paths_manager.is_auto_sync_enabled():
            reply = QMessageBox.question(
                parent_widget,
                "Sincronizzazione",
                "Prima di chiudere Hemodos, verrà eseguita la sincronizzazione con il cloud. "
                "Al termine, l'app verrà chiusa.\n\nProcedere?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.No:
                return True
        
        dialog = SyncDialog(parent_widget)
        worker = SyncWorker(
            self.paths_manager.get_database_path(),
            os.path.join(cloud_path, "db")
        )
        
        worker.progress.connect(dialog.update_progress)
        worker.finished.connect(dialog.sync_completed)
        worker.finished.connect(worker.deleteLater)
        worker.error.connect(dialog.sync_error)
        
        worker.start()
        result = dialog.exec_()
        
        return result == QDialog.Accepted 