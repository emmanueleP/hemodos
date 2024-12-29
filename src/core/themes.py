from PyQt5.QtGui import QColor

class Theme:
    def __init__(self, name, primary_color, bg_color, text_color, accent_color, table_grid_color, 
                 secondary_bg_color, hover_color, border_color, disabled_color):
        self.name = name
        self.primary_color = primary_color
        self.bg_color = bg_color
        self.text_color = text_color
        self.accent_color = accent_color
        self.table_grid_color = table_grid_color
        self.secondary_bg_color = secondary_bg_color
        self.hover_color = hover_color
        self.border_color = border_color
        self.disabled_color = disabled_color

    def get_stylesheet(self):
        return f"""
            QMainWindow, QDialog, QWidget {{
                background-color: {self.bg_color};
                color: {self.text_color};
            }}
            
            QGroupBox {{
                border: 2px solid {self.primary_color};
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 10px;
                color: {self.text_color};
                background-color: {self.secondary_bg_color};
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
                color: {self.primary_color};
                background-color: {self.secondary_bg_color};
            }}
            
            QPushButton {{
                background-color: {self.primary_color};
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }}
            
            QPushButton:hover {{
                background-color: {self.hover_color};
            }}
            
            QPushButton:disabled {{
                background-color: {self.disabled_color};
            }}
            
            QTableWidget {{
                gridline-color: {self.table_grid_color};
                background-color: {self.secondary_bg_color};
                color: {self.text_color};
                border: 1px solid {self.border_color};
            }}
            
            QTableWidget::item:selected {{
                background-color: {self.primary_color};
                color: white;
            }}
            
            QHeaderView::section {{
                background-color: {self.primary_color};
                color: white;
                padding: 5px;
                border: 1px solid {self.border_color};
            }}
            
            QLabel, QCheckBox {{
                color: {self.text_color};
            }}
            
            QComboBox {{
                background-color: {self.secondary_bg_color};
                color: {self.text_color};
                border: 1px solid {self.border_color};
                padding: 2px;
                border-radius: 3px;
            }}
            
            QComboBox:hover {{
                border-color: {self.primary_color};
            }}
            
            QComboBox::drop-down {{
                border: none;
                background-color: {self.primary_color};
                width: 20px;
            }}
            
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
                margin-right: 5px;
            }}
            
            QCalendarWidget {{
                background-color: {self.secondary_bg_color};
                color: {self.text_color};
            }}
            
            QCalendarWidget QToolButton {{
                color: {self.text_color};
                background-color: {self.secondary_bg_color};
                border: 1px solid {self.border_color};
                border-radius: 3px;
            }}
            
            QCalendarWidget QMenu {{
                background-color: {self.secondary_bg_color};
                color: {self.text_color};
                border: 1px solid {self.border_color};
            }}
            
            QCalendarWidget QSpinBox {{
                background-color: {self.secondary_bg_color};
                color: {self.text_color};
                border: 1px solid {self.border_color};
            }}
            
            QMenuBar {{
                background-color: {self.secondary_bg_color};
                color: {self.text_color};
                border-bottom: 1px solid {self.border_color};
            }}
            
            QMenuBar::item:selected {{
                background-color: {self.primary_color};
                color: white;
            }}
            
            QMenu {{
                background-color: {self.secondary_bg_color};
                color: {self.text_color};
                border: 1px solid {self.border_color};
            }}
            
            QMenu::item:selected {{
                background-color: {self.primary_color};
                color: white;
            }}
            
            QStatusBar {{
                background-color: {self.secondary_bg_color};
                color: {self.text_color};
                border-top: 1px solid {self.border_color};
            }}
            
            QScrollBar {{
                background-color: {self.secondary_bg_color};
                border: 1px solid {self.border_color};
                width: 12px;
            }}
            
            QScrollBar::handle {{
                background-color: {self.primary_color};
                border-radius: 3px;
                min-height: 20px;
            }}
            
            QScrollBar::handle:hover {{
                background-color: {self.hover_color};
            }}
            
            QCalendarWidget QWidget {{
                alternate-background-color: {self.secondary_bg_color};
            }}
            
            QCalendarWidget QAbstractItemView:enabled {{
                background-color: {self.bg_color};
                color: {self.text_color};
                selection-background-color: {self.primary_color};
                selection-color: white;
            }}
            
            QCalendarWidget QAbstractItemView:disabled {{
                color: {self.disabled_color};
            }}
            
            QDialog {{
                background-color: {self.bg_color};
                color: {self.text_color};
                border: none;
            }}
            
            QDialog QLabel {{
                color: {self.text_color};
            }}
            
            QDialog QPushButton {{
                background-color: {self.primary_color};
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
                min-width: 80px;
            }}
            
            QDialog QPushButton:hover {{
                background-color: {self.hover_color};
            }}
            
            QDialog QPushButton:disabled {{
                background-color: {self.disabled_color};
            }}
            
            QDialog QLineEdit {{
                background-color: {self.secondary_bg_color};
                color: {self.text_color};
                border: 1px solid {self.border_color};
                padding: 5px;
                border-radius: 3px;
            }}
            
            QDialog QLineEdit:focus {{
                border-color: {self.primary_color};
            }}
            
            QDialog QTextEdit, QDialog QPlainTextEdit {{
                background-color: {self.secondary_bg_color};
                color: {self.text_color};
                border: 1px solid {self.border_color};
                border-radius: 3px;
            }}
            
            QDialog QListWidget {{
                background-color: {self.secondary_bg_color};
                color: {self.text_color};
                border: 1px solid {self.border_color};
                border-radius: 3px;
            }}
            
            QDialog QListWidget::item:selected {{
                background-color: {self.primary_color};
                color: white;
            }}
            
            QDialog QTreeWidget {{
                background-color: {self.secondary_bg_color};
                color: {self.text_color};
                border: 1px solid {self.border_color};
                border-radius: 3px;
            }}
            
            QDialog QTreeWidget::item:selected {{
                background-color: {self.primary_color};
                color: white;
            }}
            
            QMessageBox {{
                background-color: {self.bg_color};
                color: {self.text_color};
            }}
            
            QMessageBox QLabel {{
                color: {self.text_color};
            }}
            
            /* Stili per le scrollbar nei dialoghi */
            QDialog QScrollBar:vertical {{
                background-color: {self.secondary_bg_color};
                width: 12px;
                margin: 0px;
            }}
            
            QDialog QScrollBar::handle:vertical {{
                background-color: {self.primary_color};
                border-radius: 6px;
                min-height: 20px;
            }}
            
            QDialog QScrollBar::handle:vertical:hover {{
                background-color: {self.hover_color};
            }}
            
            QFrame {{
                border: none;
                background-color: {self.bg_color};
            }}
            
            QTabWidget::pane {{
                border: 1px solid {self.border_color};
                background-color: {self.bg_color};
            }}
            
            QTabBar::tab {{
                background-color: {self.secondary_bg_color};
                color: {self.text_color};
                padding: 8px 12px;
                border: 1px solid {self.border_color};
                border-bottom: none;
            }}
            
            QTabBar::tab:selected {{
                background-color: {self.primary_color};
                color: white;
            }}
            
            QTabBar::tab:!selected {{
                margin-top: 2px;
            }}
        """

# Definizione dei temi disponibili
THEMES = {
    "light": Theme(
        name="Chiaro",
        primary_color="#004d4d",
        bg_color="#ffffff",
        text_color="#000000",
        accent_color="#006666",
        table_grid_color="#d0d0d0",
        secondary_bg_color="#f5f5f5",
        hover_color="#006666",
        border_color="#cccccc",
        disabled_color="#a0a0a0"
    ),
    "dark": Theme(
        name="Scuro",
        primary_color="#004d4d",      # Colore petrolio
        bg_color="#1a1a1a",          # Sfondo principale scuro
        text_color="#ffffff",
        accent_color="#00a3a3",      # Versione più chiara del petrolio
        table_grid_color="#2d2d2d",
        secondary_bg_color="#222222", # Leggermente più scuro
        hover_color="#006666",       # Versione più scura per hover
        border_color="#333333",      # Bordo più scuro
        disabled_color="#4d4d4d"
    )
} 