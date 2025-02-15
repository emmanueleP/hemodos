# Installa requisiti Python
pip install -r requirements.txt

# Build con PyInstaller
pyinstaller hemodos.spec

# Crea cartella per l'installer
New-Item -ItemType Directory -Force -Path dist/installer

# Copia i file necessari per l'installer
Copy-Item setup.iss -Destination dist/installer/
Copy-Item dist/Hemodos/* -Destination dist/installer/ -Recurse
Copy-Item LICENSE.md -Destination dist/installer/
Copy-Item README.md -Destination dist/installer/

# Verifica se Inno Setup è installato
$InnoSetup = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if (-not (Test-Path $InnoSetup)) {
    $InnoSetup = "C:\Program Files\Inno Setup 6\ISCC.exe"
}

if (-not (Test-Path $InnoSetup)) {
    Write-Host "Inno Setup non trovato. Installalo da: https://jrsoftware.org/isdl.php"
    exit 1
}

# Build dell'installer
& $InnoSetup setup.iss

# Sposta l'installer nella cartella dist
Move-Item Output/HemodosSetup.exe -Destination dist/ -Force

# Pulisci le cartelle temporanee
Remove-Item Output -Recurse -Force
Remove-Item dist/installer -Recurse -Force

Write-Host "Build completata! L'installer si trova in dist/HemodosSetup.exe" 