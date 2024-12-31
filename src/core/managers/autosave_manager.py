from PyQt5.QtCore import QObject, QTimer
from datetime import datetime
from core.logger import logger
from gui.dialogs.daily_reservations_dialog import DailyReservationsDialog

class AutosaveManager(QObject):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.timer = QTimer()
        self.timer.timeout.connect(self.auto_save)
        
        # Valori di default
        self.DEFAULT_INTERVAL = 5  # minuti
        self.MIN_INTERVAL = 1      # minuto
        self.MAX_INTERVAL = 60     # minuti

    def setup_autosave(self):
        """Configura il timer per il salvataggio automatico"""
        try:
            enabled = self.main_window.settings.value("autosave_enabled", False, type=bool)
            interval = self.main_window.settings.value("autosave_interval", self.DEFAULT_INTERVAL, type=int)
            
            # Valida l'intervallo
            interval = max(self.MIN_INTERVAL, min(interval, self.MAX_INTERVAL))
            
            if enabled:
                # Converti minuti in millisecondi
                interval_ms = interval * 60 * 1000
                self.timer.setInterval(interval_ms)
                self.timer.start()
                logger.info(f"Autosave attivato: salvataggio ogni {interval} minuti")
            else:
                self.timer.stop()
                logger.info("Autosave disattivato")
                
        except Exception as e:
            logger.error(f"Errore nella configurazione dell'autosave: {str(e)}")
            self.timer.stop()

    def auto_save(self):
        """Esegue il salvataggio automatico"""
        try:
            # Trova la finestra delle prenotazioni se è aperta
            dialog = self.main_window.findChild(DailyReservationsDialog)
            if dialog:
                # Salva le prenotazioni correnti
                table = dialog.reservations_widget.get_table()
                date = dialog.selected_date.toString("yyyy-MM-dd")
                if self.main_window.database_manager.save_reservations(table, date, False):
                    self.main_window.status_manager.update_last_save_info()
                    logger.debug("Autosave completato")
                else:
                    logger.error("Errore durante l'autosave")
                    
        except Exception as e:
            logger.error(f"Errore durante l'autosave: {str(e)}")

    def is_autosave_enabled(self):
        """Controlla se l'autosave è attivo"""
        return self.timer.isActive()

    def get_autosave_interval(self):
        """Restituisce l'intervallo corrente di autosave in minuti"""
        return self.timer.interval() // (60 * 1000) if self.timer.isActive() else 0

    def stop_autosave(self):
        """Ferma il timer dell'autosave"""
        if self.timer.isActive():
            self.timer.stop()
            logger.info("Autosave fermato")

    def __del__(self):
        """Assicura che il timer venga fermato quando l'oggetto viene distrutto"""
        try:
            if hasattr(self, 'timer') and self.timer is not None:
                self.stop_autosave()
        except:
            pass  # Ignore errors during shutdown 