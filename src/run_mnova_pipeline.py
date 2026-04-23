import sys
import os
import subprocess

# ==========================================
# DYNAMISCHE PFADERMITTLUNG
# ==========================================
# __file__ ist der absolute Pfad zu diesem Skript (run_mnova_pipeline.py).
# os.path.dirname schneidet den Dateinamen ab und gibt uns den Ordner, in dem das Skript liegt.
# Wir gehen davon aus, dass dieses Skript direkt im Projekt-Hauptordner liegt.
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 1. Pfade für die Mnova-Extraktoren zum Systempfad hinzufügen, 
# damit Python die Module "extractors" und "exporters" findet.
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from extractors.mnova import MnovaExtractor
from exporters.csv_exporter import CSVExporter

# ==========================================
# KONFIGURATION 
# ==========================================
# Der Name deines Virtual Environments (oft ".venv" oder "venv")
VENV_NAME = "venv" 

export_path = os.path.join(PROJECT_ROOT, "nmr_spectrum.csv")
pipeline_script = os.path.join(PROJECT_ROOT, "src", "pipeline.py")

def get_venv_python():
    """Findet den korrekten Python-Interpreter je nach Betriebssystem dynamisch im Projektordner."""
    if sys.platform == "win32":
        # Windows Pfad: venv\Scripts\python.exe
        return os.path.join(PROJECT_ROOT, VENV_NAME, "Scripts", "python.exe")
    else:
        # macOS / Linux Pfad: venv/bin/python
        return os.path.join(PROJECT_ROOT, VENV_NAME, "bin", "python")

def main():
    print("--- Starting One-Click NMR Pipeline ---")
    print(f"Projektverzeichnis erkannt als: {PROJECT_ROOT}") # Hilfreich fürs Debugging bei neuen Usern!
    
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