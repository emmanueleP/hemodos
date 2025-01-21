import os
import sys
from PyQt5.QtCore import QSettings
import argparse

def reset_first_run():
    """Resetta l'applicazione come se fosse al primo avvio"""
    settings = QSettings('Hemodos', 'DatabaseSettings')
    
    # Rimuovi tutte le impostazioni
    settings.clear()
    
    # Imposta first_run_completed a False
    settings.setValue("first_run_completed", False)
    
    print("✅ Applicazione resettata al primo avvio")
    
    # Avvia l'applicazione
    os.system(f"{sys.executable} src/main.py")

def simulate_second_run():
    "Simula l'app come se fosse al secondo avvio"
    settings = QSettings('Hemodos', 'DatabaseSettings')
    settings.setValue("first_run", False)
    
    print("✅ Applicazione resettata al secondo avvio")
    os.system(f"{sys.executable} src/main.py")

def main():
    parser = argparse.ArgumentParser(description='Hemodos Development Tools')
    parser.add_argument('--first-run', action='store_true', 
                       help='Resetta l\'applicazione come se fosse al primo avvio')
    parser.add_argument('--second-run', action='store_true', 
                       help='Simula l\'applicazione come se fosse al secondo avvio')
    

    args = parser.parse_args()
    
    if args.first_run:
        reset_first_run()
    elif args.second_run:
        simulate_second_run()
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 

#Per usare dev.py: python dev.py --first-run
#Per usare dev.py senza primo avvio: python dev.py
#Per info: python dev.py --help
#Per simulare il secondo avvio: python dev.py --second-run
