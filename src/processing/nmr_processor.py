import pandas as pd
import numpy as np

class NMRProcessor:
    """Handles calculations like integration and threshold analysis."""
    
    def __init__(self, csv_path):
        # 1. Wir suchen die Zeile, in der die echten Rohdaten beginnen
        skip_lines = 0
        with open(csv_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if "RAW SPECTRUM" in line:
                    # Wir überspringen alles bis einschließlich der "RAW SPECTRUM" Überschrift
                    skip_lines = i + 1 
                    break
        
        if skip_lines == 0:
            raise ValueError("Konnte den Abschnitt 'RAW SPECTRUM' in der CSV nicht finden.")

        # 2. Wir lassen Pandas erst ab dieser Zeile lesen
        self.df = pd.read_csv(csv_path, skiprows=skip_lines)
        
        # 3. Sicherheitscheck und Formatierung
        # Wir entfernen eventuelle Leerzeichen in den Spaltennamen (z.B. " ppm" -> "ppm")
        self.df.columns = self.df.columns.str.strip() 
        
        if 'ppm' not in self.df.columns or 'intensity' not in self.df.columns:
            raise ValueError(f"Spalten 'ppm' oder 'intensity' fehlen. Gefunden: {list(self.df.columns)}")

        # Sortieren nach ppm absteigend (NMR Standard)
        self.df = self.df.sort_values('ppm', ascending=False).reset_index(drop=True)

    def integrate_region(self, lower_ppm, upper_ppm, threshold=99.0):
        """Calculates stable area within a ppm range based on a percentage threshold."""
        mask = (self.df['ppm'] >= lower_ppm) & (self.df['ppm'] <= upper_ppm)
        region = self.df[mask].copy()
        
        if region.empty:
            return None
            
        intensities = region['intensity'].values
        cumulative_area = np.cumsum(intensities)
        total_area = cumulative_area[-1]
        
        # Find the index where threshold is reached
        threshold_value = (threshold / 100.0) * total_area
        idx_threshold = np.where(cumulative_area >= threshold_value)[0][0]
        
        return {
            "total_area": total_area,
            "stable_area": cumulative_area[idx_threshold],
            "cutoff_ppm": region.iloc[idx_threshold]['ppm'],
            "region_df": region
        }