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
import sys
import os

# Importazioni managers
from core.managers.year_manager import YearManager
from core.managers.database_manager import DatabaseManager
from core.managers.autosave_manager import AutosaveManager
from core.managers.menu_manager import MenuManager
from core.managers.theme_manager import ThemeManager
from core.managers.export_manager import ExportManager
from core.managers.calendar_manager import CalendarManager
from core.managers.status_manager import StatusManager
from core.managers.print_manager import PrintManager
from core.managers.database_dir_manager import DatabaseDirManager
from core.managers.cloud_manager import CloudManager

# Importazioni utils
from core.utils import print_data

# Importazioni dialogs
from gui.dialogs.history_dialog import HistoryDialog
from gui.dialogs.info_dialog import InfoDialog
from gui.dialogs.database_dialog import ConfigDatabaseDialog
from gui.dialogs.delete_dialog import DeleteFilesDialog
from gui.dialogs.time_entry_dialog import TimeEntryDialog
from gui.dialogs.statistics_dialog import StatisticsDialog
from gui.dialogs.manual_dialog import ManualDialog
from config.settings import SettingsDialog
from gui.dialogs.daily_reservations_dialog import DailyReservationsDialog
from gui.dialogs.welcome_dialog import WelcomeDialog
from gui.dialogs.first_run_dialog import FirstRunDialog
# Importazioni widgets
from gui.widgets.reservations_widget import ReservationsWidget

# Importazioni core
from core.database import add_donation_time, setup_cloud_monitoring, init_db
from core.logger import logger
from core.paths_manager import PathsManager

class MainWindow(QMainWindow):
    # Costanti della classe
    WINDOW_TITLE = "Hemodos - Prenotazioni Donazioni di Sangue"
    MIN_WINDOW_SIZE = (800, 600)
    DEFAULT_WINDOW_SIZE = (1024, 768)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.settings = QSettings('Hemodos', 'DatabaseSettings')
        self.current_user_db = self.settings.value("current_user_db")
        
        # Inizializza paths_manager prima degli altri manager
        self.paths_manager = PathsManager()
        
        # Inizializza i manager
        self._init_managers()
        
        # Imposta la finestra
        self.setWindowTitle("Hemodos")
        self.setMinimumSize(*self.MIN_WINDOW_SIZE)
        self.resize(*self.DEFAULT_WINDOW_SIZE)
        
        # Inizializza l'interfaccia
        self._init_ui_components()
        
        # Setup connessioni e dati iniziali
        self._setup_connections()
        self._load_initial_data()

    def _init_managers(self):
        """Inizializza i manager dell'applicazione"""
        try:
            # Inizializza prima i manager base
            self.database_dir_manager = DatabaseDirManager(self)
            self.status_manager = StatusManager(self)
            
            # Inizializza il database manager
            self.database_manager = DatabaseManager(self)
            
            # Configura il cloud manager con il percorso dell'utente
            self.cloud_manager = CloudManager(self)
            if self.current_user_db:
                cloud_path = os.path.dirname(self.current_user_db)
                self.cloud_manager.setup_cloud_sync(cloud_path)
                self.cloud_manager.setup_monitoring()
            
            # Inizializza gli altri manager
            self.autosave_manager = AutosaveManager(self)
            self.menu_manager = MenuManager(self)
            self.theme_manager = ThemeManager(self)
            self.export_manager = ExportManager(self)
            self.calendar_manager = CalendarManager(self)
            self.year_manager = YearManager()
            self.print_manager = PrintManager(self)

            # Imposta il percorso del database dell'utente corrente
            self.settings.setValue("cloud_path", os.path.dirname(self.current_user_db))
            self.settings.setValue("database_path", self.current_user_db)
            
        except Exception as e:
            logger.error(f"Errore nell'inizializzazione dei manager: {str(e)}")
            QMessageBox.critical(self, "Errore", f"Errore nell'inizializzazione dei manager: {str(e)}")
            sys.exit(1)

    def _init_ui_components(self):
        """Inizializza i componenti dell'interfaccia"""
        # Widget centrale
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Crea la barra dei menu
        self.menu_manager.create_menu_bar(self)
        
        # Toolbar sopra il calendario
        toolbar_layout = QHBoxLayout()
        
        # Pulsante Salva
        save_btn = QPushButton()
        save_btn.setIcon(QIcon(self.paths_manager.get_asset_path('diskette.png')))
        save_btn.setIconSize(QSize(24, 24))
        save_btn.setToolTip("Salva tutto (Ctrl+S)")
        save_btn.clicked.connect(self.save_current)
        save_btn.setFixedSize(36, 36)
        toolbar_layout.addWidget(save_btn)

        # Pulsante Prossima Donazione
        next_donation_btn = QPushButton()
        next_donation_btn.setIcon(QIcon(self.paths_manager.get_asset_path('blood.png')))
        next_donation_btn.setIconSize(QSize(24, 24))
        next_donation_btn.setToolTip("Vai alla prossima donazione")
        next_donation_btn.clicked.connect(self.calendar_manager.go_to_next_donation)
        next_donation_btn.setFixedSize(36, 36)
        toolbar_layout.addWidget(next_donation_btn)
        
        toolbar_layout.addStretch()
        main_layout.addLayout(toolbar_layout)
        
        # Inizializza calendario
        self.calendar = self.calendar_manager.init_calendar(self)
        main_layout.addWidget(self.calendar)
        
        # Aggiungi shortcut per Ctrl+S
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_current)

    def save_current(self):
        """Salva tutto lo stato dell'applicazione"""
        try:
            #Salva le prenotazioni del giorno corrente
            dialog = self.findChild(DailyReservationsDialog)
            if dialog:
                dialog.save_reservations()

            #Salva le impostazioni
            self.settings.sync()
            
            #Salva lo stato del database
            self.database_manager.save_all()

            #Mostra messaggio di conferma nella status bar
            self.status_manager.show_message("Salvataggio dell'app completato. Ora puoi uscire.", 3000)

        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Si è verificato un errore durante il salvataggio: {str(e)}")
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

    def show_database_dialog(self):
        """Mostra il dialog per la gestione del database"""
        from gui.dialogs.database_dialog import ConfigDatabaseDialog
        dialog = ConfigDatabaseDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # Ricarica il database dopo il cambio di configurazione
            self.database_manager.load_current_day()
            self.calendar_manager.highlight_donation_dates()
            
            # Aggiorna le info del database con la data corrente
            current_date = QDate.currentDate()
            self.status_manager.update_db_info(
                current_date.year(),
                current_date.toString("dd/MM/yyyy")
            )
            
            # Aggiorna il monitoraggio cloud se necessario
        service = self.settings.value("cloud_service", "Locale")
        if service != "Locale":
                    setup_cloud_monitoring(self)

    def _handle_error(self, operation: str, error: Exception, show_dialog: bool = True):
        """Gestisce gli errori in modo centralizzato"""
        error_msg = f"Errore durante {operation}: {str(error)}"
        logger.error(error_msg)
        
        if show_dialog:
            QMessageBox.critical(self, "Errore", error_msg)
        
        return False

    def closeEvent(self, event):
        """Gestisce la chiusura dell'applicazione"""
        try:
            # Prima ferma tutti i processi cloud
            if hasattr(self, 'cloud_manager'):
                self.cloud_manager.cleanup()
            
            # Poi gestisci il salvataggio
            dialog = self.findChild(DailyReservationsDialog)
            if dialog:
                dialog.save_reservations()
                dialog.close()
            
            # Rimuovi il flag della sessione di benvenuto
            if self.settings.contains("welcome_shown_this_session"):
                self.settings.remove("welcome_shown_this_session")
            
            event.accept()
            
        except Exception as e:
            logger.error(f"Errore nella chiusura dell'applicazione: {str(e)}")
            event.accept()

    def reload_database(self):
        """Ricarica il database e aggiorna le informazioni"""
        try:
            # Salva lo stato corrente se necessario
            if self.settings.value("autosave_on_cloud_change", True, type=bool):
                dialog = self.findChild(DailyReservationsDialog)
                if dialog:
                    dialog.save_reservations()
            
            # Ricarica le prenotazioni
            selected_date = self.calendar.selectedDate()
            self.database_manager.load_current_day()
            
            # Aggiorna il calendario
            self.calendar_manager.highlight_donation_dates()
            
            # Aggiorna le informazioni nella status bar
            self.status_manager.update_db_info(
                selected_date.year(),
                selected_date.toString("dd/MM/yyyy")
            )
            
            # Mostra messaggio di conferma
            self.status_manager.show_message(
                f"Database ricaricato: {selected_date.toString('dd/MM/yyyy')}", 
                    3000
                )
            
        except Exception as e:
            self._handle_error("la ricarica del database", e)

    def show_history(self):
        """Mostra la finestra della cronologia"""
        from gui.dialogs.history_dialog import HistoryDialog
        dialog = HistoryDialog(self)
        dialog.exec_()

    def init_ui(self):
        # ... existing code ...
        
        # Toolbar icons
        self.toolbar.addAction(QIcon(self.paths_manager.get_asset_path('new_64px.png')), "Nuovo")
        self.toolbar.addAction(QIcon(self.paths_manager.get_asset_path('save_64px.png')), "Salva")
        # ... altri pulsanti della toolbar ...
