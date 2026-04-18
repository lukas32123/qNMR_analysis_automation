import sys
import os
import subprocess

# 1. Pfade zum src-Ordner für die Mnova-Extraktoren
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from extractors.mnova import MnovaExtractor
from exporters.csv_exporter import CSVExporter

# ==========================================
# KONFIGURATION (Hier passt du die Pfade für das Deployment an)
# ==========================================
# Der Hauptordner deines Projekts
PROJECT_ROOT = "/Users/lukas/FH_Aachen_Job" 

# Der Name deines Virtual Environments (oft ".venv" oder "venv")
VENV_NAME = "venv" # <--- Bitte anpassen, falls dein venv anders heißt!

export_path = os.path.join(PROJECT_ROOT, "nmr_spectrum.csv")
pipeline_script = os.path.join(PROJECT_ROOT, "src", "pipeline.py")

def get_venv_python():
    """Findet den korrekten Python-Interpreter je nach Betriebssystem."""
    if sys.platform == "win32":
        # Windows Pfad: venv\Scripts\python.exe
        return os.path.join(PROJECT_ROOT, VENV_NAME, "Scripts", "python.exe")
    else:
        # macOS / Linux Pfad: venv/bin/python
        return os.path.join(PROJECT_ROOT, VENV_NAME, "bin", "python")

def main():
    print("--- Starting One-Click NMR Pipeline ---")
    
    try:
        # SCHRITT 1 & 2: EXTRAKTION UND EXPORT (läuft in Mnova)
        print("Schritt 1: Extrahiere Daten...")
        extractor = MnovaExtractor()
        data = extractor.get_all_data()
        
        print(f"Schritt 2: Speichere CSV unter {export_path}...")
        exporter = CSVExporter(export_path)
        exporter.export(data)

        # SCHRITT 3: DIE BRÜCKE ZUM EXTERNEN PYTHON (läuft im OS)
        print("Schritt 3: Starte externe Verarbeitung (PDF-Generierung)...")
        
        python_executable = get_venv_python()
        
        # Sicherheitscheck: Existiert das venv überhaupt auf diesem PC?
        if not os.path.exists(python_executable):
            print(f"\n[FEHLER] Konnte die Python-Umgebung nicht finden: {python_executable}")
            print("Bitte stelle sicher, dass das Virtual Environment eingerichtet ist.")
            return

        # Führe die externe pipeline.py im Hintergrund aus
        # subprocess.run wartet, bis die PDF fertig ist
        result = subprocess.run(
            [python_executable, pipeline_script], 
            capture_output=True, 
            text=True
        )

        # Überprüfen, ob das externe Skript gecrasht ist
        if result.returncode == 0:
            print("\n>>> ERFOLG! Pipeline abgeschlossen.")
            print("Die externe Ausgabe war:")
            print(result.stdout)
        else:
            print("\n>>> FEHLER bei der PDF-Erstellung!")
            print(result.stderr)
            
    except Exception as e:
        print(f"KRITISCHER FEHLER: {e}")

if __name__ == "__main__":
    main()