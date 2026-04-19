import sys
import subprocess
import pathlib

SCRIPT_PATH = pathlib.Path(__file__).parent.resolve()
SRC_PATH = SCRIPT_PATH / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from extractors.mnova import MnovaExtractor
from exporters.csv_exporter import CSVExporter
from MnovaNMR import NMRPlugin # NEU: Um die Markierungen aus Mnova zu lesen

def get_python_executable():
    if sys.platform == "win32":
        return SCRIPT_PATH / "venv" / "Scripts" / "python.exe"
    return SCRIPT_PATH / "venv" / "bin" / "python"

def export_integration_ranges(filepath):
    """Liest die aktuell gezogenen Integrale aus Mnova aus."""
    nmrPlg = NMRPlugin()
    activeItem = nmrPlg.activeNMRItem()
    if not activeItem:
        return False
        
    spectrum = activeItem.activeSpectrum
    integrals = spectrum.getIntegrals()
    
    with open(filepath, 'w', encoding='utf-8') as f:
        for integral in integrals:
            # Dank unserer Debug-Ausgabe wissen wir jetzt: 
            # Die Attribute heißen 'rangeMin' und 'rangeMax'
            
            # Sicherheitscheck: Mnova mischt manchmal Properties (Wert) und Methoden (Funktion).
            # Wir prüfen kurz, ob wir Klammern () anhängen müssen oder nicht.
            p1 = integral.rangeMin() if callable(integral.rangeMin) else integral.rangeMin
            p2 = integral.rangeMax() if callable(integral.rangeMax) else integral.rangeMax
            
            # Sicherstellen, dass Start der kleinere Wert ist
            start = min(p1, p2)
            end = max(p1, p2)
            f.write(f"{start};{end}\n")
            
    return True

def main():
    print("--- NMR Pipeline gestartet ---")
    
    try:
        csv_path = SCRIPT_PATH / "nmr_spectrum.csv"
        ranges_path = SCRIPT_PATH / "ranges.csv"
        
        print("Schritt 1: Extrahiere Spektrum und Integrationsbereiche...")
        # 1. Spektrum exportieren
        extractor = MnovaExtractor()
        exporter = CSVExporter(str(csv_path))
        exporter.export(extractor.get_all_data())
        
        # 2. Ranges exportieren (NEU)
        export_integration_ranges(str(ranges_path))
        
        print("Schritt 2: Starte Hintergrund-Berechnungen...")
        python_bin = get_python_executable()
        orchestrator_script = SRC_PATH / "orchestrator.py"
        
        result = subprocess.run(
            [str(python_bin), str(orchestrator_script)], 
            capture_output=True, 
            text=True
        )
        
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