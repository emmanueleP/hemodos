import os
import subprocess

def build_windows_exe():
    """
    Build Windows executable using PyInstaller through Wine
    """
    try:
        # Assicurati che Wine sia installato
        if subprocess.call(['which', 'wine']) != 0:
            print("Wine non è installato. Installalo con: brew install wine-stable")
            return

        # Installa Python per Windows attraverso Wine
        # Nota: questo passaggio dovrebbe essere fatto manualmente la prima volta
        
        # Percorso all'exe di Python in Wine
        WINE_PYTHON = "wine ~/.wine/drive_c/Python39/python.exe"
        
        # Installa PyInstaller in Windows Python
        os.system(f"{WINE_PYTHON} -m pip install pyinstaller")
        
        # Installa le dipendenze necessarie
        os.system(f"{WINE_PYTHON} -m pip install PyQt5 pandas openpyxl python-docx")
        
        # Comando PyInstaller
        pyinstaller_command = f"{WINE_PYTHON} -m PyInstaller --clean --windowed --onefile " \
                            "--add-data 'src/assets/*:assets' " \
                            "--icon=src/assets/logo.ico " \
                            "--name Hemodos " \
                            "src/main.py"
        
        # Esegui PyInstaller
        os.system(pyinstaller_command)
        
        print("Build completata! L'exe si trova nella cartella dist/")
        
    except Exception as e:
        print(f"Errore durante la build: {str(e)}")

if __name__ == "__main__":
    build_windows_exe() 