from PyQt5.QtWidgets import QMenuBar, QMenu, QAction, QStatusBar, QLabel, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from gui.dialogs.daily_reservations_dialog import DailyReservationsDialog

class MenuManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def create_menu_bar(self, main_window):
        """Crea la barra dei menu"""
        menubar = main_window.menuBar()

        # Menu File
        file_menu = menubar.addMenu('File')
        
        # Add Time Entry action
        add_time_action = QAction(QIcon('assets/add_time.png'), 'Aggiungi Orario', main_window)
        add_time_action.setShortcut('Ctrl+T')
        add_time_action.triggered.connect(main_window.show_time_entry_dialog)
        file_menu.addAction(add_time_action)
        
        # Save action
        save_action = QAction(QIcon('assets/diskette.png'), 'Salva', main_window)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self._save_current_reservations)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()

        # Export action
        export_action = QAction(QIcon('assets/doc.png'), 'Esporta in Word (.docx)', main_window)
        export_action.setShortcut('Ctrl+W')
        export_action.triggered.connect(self.main_window.export_manager.export_to_docx)
        file_menu.addAction(export_action)

        # Print action
        print_action = QAction(QIcon('assets/printer.png'), 'Stampa', main_window)
        print_action.setShortcut('Ctrl+P')
        print_action.triggered.connect(self.main_window.export_manager.print_table)
        file_menu.addAction(print_action)
        
        file_menu.addSeparator()

        # Database dialog
        database_action = QAction(QIcon('assets/refresh_data.png'), 'Database', main_window)
        database_action.setShortcut('Ctrl+D')
        database_action.triggered.connect(main_window.show_database_dialog)
        file_menu.addAction(database_action)
        
        # Exit action
        exit_action = QAction('Esci', main_window)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(main_window.close)
        file_menu.addAction(exit_action)

        # Menu Tools
        tools_menu = menubar.addMenu('Strumenti')
        
        # History action
        history_action = QAction(QIcon('assets/history.png'), 'Cronologia', main_window)
        history_action.triggered.connect(main_window.show_history)
        tools_menu.addAction(history_action)
        
        # Delete action
        delete_action = QAction(QIcon('assets/trash.png'), 'Elimina Database...', main_window)
        delete_action.triggered.connect(main_window.show_delete_dialog)
        tools_menu.addAction(delete_action)
        
        tools_menu.addSeparator()
        
        # Statistics action
        statistics_action = QAction(QIcon('assets/stats.png'), 'Statistiche', main_window)
        statistics_action.triggered.connect(main_window.show_statistics)
        tools_menu.addAction(statistics_action)

        # Menu Settings
        settings_menu = menubar.addMenu('Impostazioni')
        
        # Preferences action
        preferences_action = QAction(QIcon('assets/cogwheel.png'), 'Preferenze', main_window)
        preferences_action.triggered.connect(main_window.show_settings)
        settings_menu.addAction(preferences_action)

        # Menu Info
        info_menu = menubar.addMenu('Info')
        
        # Manual action
        manual_action = QAction(QIcon('assets/user_guide.png'), 'Manuale', main_window)
        manual_action.setShortcut('F1')
        manual_action.triggered.connect(main_window.show_manual)
        info_menu.addAction(manual_action)
        
        # About action
        about_action = QAction('Informazioni su Hemodos', main_window)
        about_action.triggered.connect(main_window.show_info)
        info_menu.addAction(about_action)

    def _save_current_reservations(self):
        """Salva le prenotazioni della finestra corrente"""
        dialog = self.main_window.findChild(DailyReservationsDialog)
        if dialog:
            dialog.save_reservations()
        else:
            QMessageBox.warning(
                self.main_window,
                "Attenzione",
                "Apri prima una finestra delle prenotazioni"
            )

    # Rimuovi il metodo create_status_bar() poiché ora è gestito da StatusManager 