import sys
import pathlib

# 1. Dynamische Pfadermittlung
# Diese Datei weiß, dass sie im 'src' Ordner liegt. Der Projektordner ist also eine Ebene drüber (.parent)
SRC_DIR = pathlib.Path(__file__).parent.resolve()
PROJECT_ROOT = SRC_DIR.parent

# 2. Füge den src-Ordner zum Systempfad hinzu, damit die Imports klappen
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from processing.nmr_processor import NMRProcessor
from visualization.nmr_visualizer import NMRVisualizer

def run_pipeline():
    input_csv = PROJECT_ROOT / "nmr_spectrum.csv"
    output_pdf = PROJECT_ROOT / "nmr_report.pdf"

    if not input_csv.exists():
        print(f"Fehler: Konnte {input_csv} nicht finden.")
        sys.exit(1)

    print("Starte Datenverarbeitung...")
    processor = NMRProcessor(str(input_csv))
    
    # Hier kannst du deine PPM-Bereiche anpassen
    ranges = [(1.9, 2.1), (0.9, 1.1)] 
        
    results = []
    for low, high in ranges:
        res = processor.integrate_region(low, high, threshold=99.0)
        if res:
            results.append(res)
    
    print("Erstelle PDF-Report...")
    visualizer = NMRVisualizer(str(output_pdf))
    visualizer.generate_report(processor.df, results)
    
    print(f"Erfolg! Report gespeichert unter: {output_pdf}")

if __name__ == "__main__":
    run_pipeline()