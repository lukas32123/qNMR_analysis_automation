import sys
import subprocess
import pathlib

# Pfade ermitteln
SCRIPT_PATH = pathlib.Path(__file__).parent.resolve()
SRC_PATH = SCRIPT_PATH / "src"

# Damit wir MnovaExtractor importieren können
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from extractors.mnova import MnovaExtractor
from exporters.csv_exporter import CSVExporter

def get_python_executable():
    """Findet das venv systemübergreifend."""
    if sys.platform == "win32":
        return SCRIPT_PATH / "venv" / "Scripts" / "python.exe"
    return SCRIPT_PATH / "venv" / "bin" / "python"

def main():
    print("--- NMR Pipeline gestartet ---")
    
    try:
        # SCHRITT 1: Extraktion in Mnova
        csv_path = SCRIPT_PATH / "nmr_spectrum.csv"
        extractor = MnovaExtractor()
        exporter = CSVExporter(str(csv_path))
        exporter.export(extractor.get_all_data())
        
        # SCHRITT 2: Subprozess starten
        python_bin = get_python_executable()
        orchestrator_script = SRC_PATH / "orchestrator.py"
        
        if not python_bin.exists():
            print(f"\n[FEHLER] Virtual environment nicht gefunden unter {python_bin}")
            return

        print("Starte Hintergrund-Berechnungen...")
        
        # NEU: Wir rufen einfach die Datei auf, das ist absolut fehlerfrei!
        result = subprocess.run(
            [str(python_bin), str(orchestrator_script)], 
            capture_output=True, 
            text=True
        )
        
        # Konsolenausgabe des Subprozesses anzeigen
        if result.returncode == 0:
            print("\n>>> PIPELINE ERFOLGREICH BEENDET!")
            print(result.stdout)
        else:
            print("\n>>> FEHLER IM BACKEND:")
            print(result.stderr)
            
    except Exception as e:
        print(f"Kritischer Systemfehler: {e}")

if __name__ == "__main__":
    main()