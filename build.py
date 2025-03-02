#!/usr/bin/env python3
import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path

APP_NAME = 'Hemodos'
APP_VERSION = '1.0.9'
BASE_DIR = Path(__file__).parent.absolute()

def clean_build():
    """Pulisce le directory di build"""
    print("Pulizia delle directory di build...")
    paths = ['build', 'dist', 'installer']
    for path in paths:
        if os.path.exists(path):
            shutil.rmtree(path)

def copy_assets():
    """Copia gli assets nella directory dist"""
    print("Copiando gli assets...")
    
    # Crea le directory necessarie
    directories = [
        os.path.join('dist', 'assets'),
        os.path.join('dist', 'templates'),
        os.path.join('dist', 'static')
    ]
    
    for directory in directories:
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.makedirs(directory)
    
    # Copia gli assets se esistono
    if os.path.exists('src/assets'):
        for item in os.listdir('src/assets'):
            s = os.path.join('src/assets', item)
            d = os.path.join('dist/assets', item)
            if os.path.isdir(s):
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)
    
    # Copia i templates se esistono
    if os.path.exists('src/gui/templates'):
        for item in os.listdir('src/gui/templates'):
            s = os.path.join('src/gui/templates', item)
            d = os.path.join('dist/templates', item)
            if os.path.isdir(s):
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)
    
    # Copia i file statici se esistono
    if os.path.exists('src/static'):
        for item in os.listdir('src/static'):
            s = os.path.join('src/static', item)
            d = os.path.join('dist/static', item)
            if os.path.isdir(s):
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)

def run_pyinstaller():
    """Esegue PyInstaller con il file spec"""
    print("Creazione del pacchetto con PyInstaller...")
    try:
        subprocess.run(['pyinstaller', 'hemodos.spec', '--noconfirm'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Errore durante l'esecuzione di PyInstaller: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("ERRORE: PyInstaller non trovato!")
        print("Installa PyInstaller con: pip install pyinstaller")
        sys.exit(1)

def create_installer():
    """Crea l'installer usando Inno Setup"""
    print("Creazione dell'installer...")
    try:
        iscc_paths = [
            r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
            r"C:\Program Files\Inno Setup 6\ISCC.exe",
            "iscc"
        ]
        
        iscc_exe = None
        for path in iscc_paths:
            if os.path.exists(path):
                iscc_exe = path
                break
            elif path == "iscc":
                try:
                    subprocess.run(['iscc', '/?'], capture_output=True, check=True)
                    iscc_exe = path
                    break
                except:
                    continue
        
        if iscc_exe:
            subprocess.run([iscc_exe, 'setup.iss'], check=True)
            print("\nInstaller creato con successo in: Output/Hemodos_Setup.exe")
        else:
            print("ERRORE: Inno Setup non trovato!")
            print("Installa Inno Setup da: https://jrsoftware.org/isdl.php")
    except subprocess.CalledProcessError as e:
        print(f"Errore durante la creazione dell'installer: {e}")
        sys.exit(1)

def main():
    """Funzione principale"""
    try:
        clean_build()
        copy_assets()
        run_pyinstaller()
        create_installer()
        
        print("\nBuild completata con successo!")
        print(f"Trovi l'applicazione in: dist/{APP_NAME}/")
        if os.path.exists('Output/Hemodos_Setup.exe'):
            print(f"Trovi l'installer in: Output/Hemodos_Setup.exe")
    except Exception as e:
        print(f"Errore durante la build: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 