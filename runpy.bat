@echo off
:: Cerca il primo file .py nella cartella
for %%f in (*.py) do (
    
    :: Avvia il file python in modalità "windowless" (senza console)
    :: Le virgolette vuote "" servono per la sintassi del comando start
    start "" pythonw "%%f"
    
    :: Chiude immediatamente questo file bat
    exit
)