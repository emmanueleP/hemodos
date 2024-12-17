from dialog_base import HemodosDialog
from PyQt5.QtWidgets import (QVBoxLayout, QTabWidget, QWidget, 
                            QComboBox, QLabel)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import sqlite3
import os
from database import get_db_path
from datetime import datetime

class StatisticsDialog(HemodosDialog):
    def __init__(self, parent=None):
        super().__init__(parent, "Statistiche Donazioni")
        self.setMinimumSize(800, 600)
        self.init_ui()

    def init_ui(self):
        tab_widget = QTabWidget()
        
        # Tab mensile
        monthly_tab = QWidget()
        monthly_layout = QVBoxLayout()
        self.monthly_canvas = self.create_monthly_chart()
        monthly_layout.addWidget(self.monthly_canvas)
        monthly_tab.setLayout(monthly_layout)
        tab_widget.addTab(monthly_tab, "Mensile")
        
        # Tab trimestrale
        quarterly_tab = QWidget()
        quarterly_layout = QVBoxLayout()
        self.quarterly_canvas = self.create_quarterly_chart()
        quarterly_layout.addWidget(self.quarterly_canvas)
        quarterly_tab.setLayout(quarterly_layout)
        tab_widget.addTab(quarterly_tab, "Trimestrale")
        
        # Tab annuale
        yearly_tab = QWidget()
        yearly_layout = QVBoxLayout()
        self.yearly_canvas = self.create_yearly_chart()
        yearly_layout.addWidget(self.yearly_canvas)
        yearly_tab.setLayout(yearly_layout)
        tab_widget.addTab(yearly_tab, "Annuale")
        
        self.content_layout.addWidget(tab_widget)

    def create_monthly_chart(self):
        fig = Figure(figsize=(8, 6))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        
        # Recupera i dati mensili
        data = self.get_monthly_stats()
        months = range(1, 13)
        
        # Crea le barre
        x = list(months)
        width = 0.25
        
        ax.bar([i-width for i in x], [data[m]['total'] for m in months], 
               width, label='Totale Prenotazioni', color='#0073e6')
        ax.bar(x, [data[m]['completed'] for m in months], 
               width, label='Donazioni Effettuate', color='#00cc66')
        ax.bar([i+width for i in x], [data[m]['first'] for m in months], 
               width, label='Prime Donazioni', color='#ff9933')
        
        ax.set_xlabel('Mese')
        ax.set_ylabel('Numero di Donazioni')
        ax.set_title('Statistiche Mensili')
        ax.set_xticks(x)
        ax.set_xticklabels(['Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu', 
                            'Lug', 'Ago', 'Set', 'Ott', 'Nov', 'Dic'])
        ax.legend()
        
        # Aggiungi griglia
        ax.grid(True, linestyle='--', alpha=0.7)
        
        return canvas

    def create_quarterly_chart(self):
        fig = Figure(figsize=(8, 6))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        
        # Recupera e aggrega i dati trimestrali
        monthly_data = self.get_monthly_stats()
        quarters = {
            1: {'total': 0, 'completed': 0, 'first': 0},
            2: {'total': 0, 'completed': 0, 'first': 0},
            3: {'total': 0, 'completed': 0, 'first': 0},
            4: {'total': 0, 'completed': 0, 'first': 0}
        }
        
        for month, data in monthly_data.items():
            quarter = (month - 1) // 3 + 1
            quarters[quarter]['total'] += data['total']
            quarters[quarter]['completed'] += data['completed']
            quarters[quarter]['first'] += data['first']
        
        # Crea il grafico
        quarters_range = range(1, 5)
        ax.plot(quarters_range, [quarters[q]['total'] for q in quarters_range], 
                label='Totale Prenotazioni', marker='o')
        ax.plot(quarters_range, [quarters[q]['completed'] for q in quarters_range], 
                label='Donazioni Effettuate', marker='s')
        ax.plot(quarters_range, [quarters[q]['first'] for q in quarters_range], 
                label='Prime Donazioni', marker='^')
        
        ax.set_xlabel('Trimestre')
        ax.set_ylabel('Numero di Donazioni')
        ax.set_title('Statistiche Trimestrali')
        ax.legend()
        
        return canvas

    def create_yearly_chart(self):
        fig = Figure(figsize=(8, 6))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        
        # Recupera i totali annuali
        yearly_stats = self.get_yearly_stats()
        
        # Verifica che ci siano dati da visualizzare
        if yearly_stats['total'] == 0:
            ax.text(0.5, 0.5, 'Nessun dato disponibile per quest\'anno',
                    ha='center', va='center')
            return canvas
        
        # Crea il grafico a torta
        labels = ['Prime Donazioni', 'Donazioni Ripetute', 'Non Effettuate']
        sizes = [
            yearly_stats['first'],
            yearly_stats['completed'] - yearly_stats['first'],
            yearly_stats['total'] - yearly_stats['completed']
        ]
        
        # Rimuovi le sezioni con valore 0
        non_zero = [(size, label) for size, label in zip(sizes, labels) if size > 0]
        if non_zero:
            sizes, labels = zip(*non_zero)
            ax.pie(sizes, labels=labels, autopct='%1.1f%%')
        else:
            ax.text(0.5, 0.5, 'Nessun dato disponibile',
                    ha='center', va='center')
        
        ax.set_title('Riepilogo Annuale')
        
        return canvas

    def get_monthly_stats(self):
        year = datetime.now().year
        base_path = os.path.dirname(get_db_path())
        stats = {}
        
        # Inizializza tutti i mesi con valori zero
        for month in range(1, 13):
            stats[month] = {'total': 0, 'completed': 0, 'first': 0}
        
        # Scansiona tutti i file di prenotazione dell'anno
        for filename in os.listdir(base_path):
            if filename.startswith('prenotazioni_') and filename.endswith('.db'):
                try:
                    db_path = os.path.join(base_path, filename)
                    conn = sqlite3.connect(db_path)
                    c = conn.cursor()
                    
                    # Estrai il giorno e il mese dal nome del file
                    day = int(filename.split('_')[1])
                    month = int(filename.split('_')[2].split('.')[0])
                    
                    # Conta le prenotazioni
                    c.execute("SELECT COUNT(*) FROM reservations WHERE name != ''")
                    total = c.fetchone()[0]
                    
                    c.execute("SELECT COUNT(*) FROM reservations WHERE name != '' AND stato = 'Sì'")
                    completed = c.fetchone()[0]
                    
                    c.execute("""SELECT COUNT(*) FROM reservations 
                               WHERE name != '' AND stato = 'Sì' 
                               AND first_donation = 1""")
                    first = c.fetchone()[0]
                    
                    # Aggiorna le statistiche del mese
                    stats[month]['total'] += total
                    stats[month]['completed'] += completed
                    stats[month]['first'] += first
                    
                    conn.close()
                except Exception as e:
                    print(f"Errore nel leggere {filename}: {str(e)}")
        
        return stats

    def get_yearly_stats(self):
        year = datetime.now().year
        stats = {'total': 0, 'completed': 0, 'first': 0}
        
        monthly_stats = self.get_monthly_stats()
        for month_stats in monthly_stats.values():
            stats['total'] += month_stats['total']
            stats['completed'] += month_stats['completed']
            stats['first'] += month_stats['first']
        
        return stats 