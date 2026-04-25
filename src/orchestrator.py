import sys
import pathlib

SRC_DIR = pathlib.Path(__file__).parent.resolve()
PROJECT_ROOT = SRC_DIR.parent

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from processing.nmr_processor import NMRProcessor
from visualization.nmr_visualizer import NMRVisualizer

def run_pipeline():
    input_csv = PROJECT_ROOT / "nmr_spectrum.csv"
    ranges_csv = PROJECT_ROOT / "ranges.csv"

    if not input_csv.exists():
        print(f"Fehler: Konnte {input_csv} nicht finden.")
        sys.exit(1)

    # Lese die dynamischen Ranges aus Mnova ein (NEU)
    ranges = []
    if ranges_csv.exists():
        with open(ranges_csv, 'r') as f:
            for line in f:
                parts = line.strip().split(';')
                if len(parts) == 2:
                    p1, p2 = float(parts[0]), float(parts[1])
                    ranges.append((min(p1, p2), max(p1, p2)))
    
    if not ranges:
        print("Keine Integrale markiert! Breche Verarbeitung ab.")
        sys.exit(1)

    print(f"Gefundene Integrationsbereiche: {ranges}")
    print("Starte Datenverarbeitung...")
    processor = NMRProcessor(str(input_csv))
        
    results = []
    for low, high in ranges:
        res = processor.integrate_region(low, high, threshold=99.7)
        if res:
            results.append(res)
    
    print("Erstelle PDF-Reports...")
    visualizer = NMRVisualizer(PROJECT_ROOT)
    visualizer.generate_all_reports(processor.df, results)
    
    print(f"Erfolg! PDFs für die Analyse gespeichert in: {PROJECT_ROOT}")

if __name__ == "__main__":
    run_pipeline()