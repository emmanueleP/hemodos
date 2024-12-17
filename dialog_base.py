from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt

class HemodosDialog(QDialog):
    def __init__(self, parent=None, title=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(500)
        
        # Layout principale con margini uniformi
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)
        
        # Header con logo/titolo
        self.header_layout = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #004d4d;
                padding: 10px;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        self.header_layout.addStretch()
        self.header_layout.addWidget(title_label)
        self.header_layout.addStretch()
        self.main_layout.addLayout(self.header_layout)
        
        # Contenuto (da sovrascrivere nelle classi figlie)
        self.content_layout = QVBoxLayout()
        self.main_layout.addLayout(self.content_layout)
        
        # Pulsanti standard
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.addStretch()
        
        # Stile comune per i pulsanti
        self.button_style = """
            QPushButton {
                background-color: #004d4d;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #006666;
            }
        """
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        ok_button.setStyleSheet(self.button_style)
        self.buttons_layout.addWidget(ok_button)
        
        cancel_button = QPushButton("Annulla")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setStyleSheet(self.button_style)
        self.buttons_layout.addWidget(cancel_button)
        
        self.main_layout.addLayout(self.buttons_layout)
        self.setLayout(self.main_layout)
        
        # Stile generale
        self.setStyleSheet("""
            QDialog {
                background-color: palette(window);
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
        """)