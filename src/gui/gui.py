# Importazioni PyQt
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                            QLabel, QCalendarWidget, QTableWidget, QTableWidgetItem, 
                            QFileDialog, QMessageBox, QMenuBar, QMenu, QAction,
    QDialog, QComboBox, QStatusBar, QShortcut, QGroupBox, QHBoxLayout
)
from PyQt5.QtCore import Qt, QSettings, QDate, QTimer, QTime, QSize
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog

# Importazioni managers
from core.managers.year_manager import YearManager
from core.managers.database_manager import DatabaseManager 
from core.managers.autosave_manager import AutosaveManager
from core.managers.menu_manager import MenuManager
from core.managers.theme_manager import ThemeManager
from core.managers.export_manager import ExportManager
from core.managers.calendar_manager import CalendarManager
from core.managers.status_manager import StatusManager

# Importazioni utils
from core.utils import print_data

# Importazioni dialogs
from gui.dialogs.history_dialog import HistoryDialog
from gui.dialogs.info_dialog import InfoDialog
from gui.dialogs.database_dialog import FirstRunDialog
from gui.dialogs.delete_dialog import DeleteFilesDialog
from gui.dialogs.time_entry_dialog import TimeEntryDialog
from gui.dialogs.statistics_dialog import StatisticsDialog
from gui.dialogs.manual_dialog import ManualDialog
from config.settings import SettingsDialog
from gui.dialogs.daily_reservations_dialog import DailyReservationsDialog

# Importazioni widgets
from gui.widgets.reservations_widget import ReservationsWidget

# Importazioni core
from core.database import add_donation_time, setup_cloud_monitoring, init_db
from core.logger import logger

class MainWindow(QMainWindow):
    # Costanti della classe
    WINDOW_TITLE = "Hemodos - Prenotazioni Donazioni di Sangue"
    MIN_WINDOW_SIZE = (800, 600)
    DEFAULT_WINDOW_SIZE = (1024, 768)

    def __init__(self, config):
        super().__init__()
        self.settings = QSettings('Hemodos', 'DatabaseSettings')

        # Set window properties
        self.setWindowTitle(self.WINDOW_TITLE)
        self.resize(*self.DEFAULT_WINDOW_SIZE)
        self.setMinimumSize(*self.MIN_WINDOW_SIZE)

        # Inizializza i manager
        self._init_managers()
        
        # Inizializza l'interfaccia
        self._init_ui_components()
        
        # Setup connessioni e dati iniziali
        self._setup_connections()
        self._load_initial_data()

    def _init_managers(self):
        """Inizializza i manager dell'applicazione"""
        self.database_manager = DatabaseManager(self)
        self.autosave_manager = AutosaveManager(self)
        self.menu_manager = MenuManager(self)
        self.theme_manager = ThemeManager(self)
        self.export_manager = ExportManager(self)
        self.calendar_manager = CalendarManager(self)
        self.year_manager = YearManager()
        self.status_manager = StatusManager(self)

    def _init_ui_components(self):
        """Inizializza i componenti dell'interfaccia utente"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Inizializza calendario
        self.calendar = self.calendar_manager.init_calendar(self)
        layout.addWidget(self.calendar)
        
        # Crea solo la barra dei menu (la status bar è gestita da StatusManager)
        self.menu_manager.create_menu_bar(self)

    def _setup_connections(self):
        """Configura le connessioni tra segnali e slot"""
        # Collega il cambio data all'apertura della finestra prenotazioni
        self.calendar.clicked.connect(self.show_daily_reservations)
        
        # Setup autosave timer
        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.autosave_manager.auto_save)
        self.autosave_manager.setup_autosave()

    def _load_initial_data(self):
        """Carica i dati iniziali"""
        self.observer = setup_cloud_monitoring(self)
        self.database_manager.load_current_day()
        self.calendar_manager.highlight_donation_dates()
        self.theme_manager.apply_theme()

    # Dialog methods
    def show_time_entry_dialog(self):
        """Mostra il dialog per l'inserimento degli orari"""
        dialog = TimeEntryDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            time = dialog.get_time()
            date = self.calendar.selectedDate().toString("yyyy-MM-dd")
            if add_donation_time(date, time):
                self.database_manager.load_reservations()
                self.calendar_manager.highlight_donation_dates()

    def show_history(self):
        dialog = HistoryDialog(self)
        dialog.exec_()

    def show_info(self):
        dialog = InfoDialog(self)
        dialog.exec_()

    def show_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
                init_db()
        self.theme_manager.apply_theme()
        self.calendar_manager.highlight_donation_dates()
        self.autosave_manager.setup_autosave()

    def show_statistics(self):
        dialog = StatisticsDialog(self)
        dialog.exec_()

    def show_manual(self):
        dialog = ManualDialog(self)
        dialog.exec_()

    def show_delete_dialog(self):
        dialog = DeleteFilesDialog(self)
        dialog.exec_()

    def show_daily_reservations(self, date):
        """Mostra la finestra delle prenotazioni per la data selezionata"""
        dialog = DailyReservationsDialog(self, date)
        dialog.exec_()

    def _handle_error(self, operation: str, error: Exception, show_dialog: bool = True):
        """Gestisce gli errori in modo centralizzato"""
        error_msg = f"Errore durante {operation}: {str(error)}"
        logger.error(error_msg)
        
        if show_dialog:
            QMessageBox.critical(self, "Errore", error_msg)
        
        return False

    def closeEvent(self, event):
        """Gestisce l'evento di chiusura dell'applicazione"""
        try:
            # Trova la finestra delle prenotazioni se è aperta
            dialog = self.findChild(DailyReservationsDialog)
            if dialog:
                # Salva le prenotazioni correnti
                if dialog.save_reservations():
                    # Ferma il monitoraggio cloud se attivo
                    if hasattr(self, 'observer') and self.observer:
                        self.observer.stop()
                    # Ferma l'autosave
                    self.autosave_manager.stop_autosave()
                    event.accept()
                else:
                    # Se il salvataggio fallisce, chiedi conferma
                    reply = QMessageBox.question(
                        self, 'Conferma uscita',
                        'Il salvataggio non è riuscito. Vuoi uscire comunque?',
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )
                    if reply == QMessageBox.Yes:
                        event.accept()
                    else:
                        event.ignore()
            else:
                # Se non c'è una finestra delle prenotazioni aperta, chiudi normalmente
                if hasattr(self, 'observer') and self.observer:
                    self.observer.stop()
                self.autosave_manager.stop_autosave()
                event.accept()
                
        except Exception as e:
            logger.error(f"Errore durante la chiusura: {str(e)}")
            event.accept()  # Chiudi comunque per evitare loop
