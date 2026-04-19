import pandas as pd
import numpy as np

class NMRProcessor:
    def __init__(self, csv_path):
        skip_lines = 0
        with open(csv_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if "RAW SPECTRUM" in line:
                    skip_lines = i + 1 
                    break
        
        if skip_lines == 0:
            raise ValueError("Konnte den Abschnitt 'RAW SPECTRUM' in der CSV nicht finden.")

        self.df = pd.read_csv(csv_path, skiprows=skip_lines)
        self.df.columns = self.df.columns.str.strip() 
        self.df = self.df.sort_values('ppm', ascending=False).reset_index(drop=True)

    def integrate_region(self, lower_ppm, upper_ppm, threshold=99.7):
        """Erweiterte Mathematik nach dem Vorbild der Vorgängerin."""
        mask = (self.df['ppm'] >= lower_ppm) & (self.df['ppm'] <= upper_ppm)
        region = self.df[mask].copy()
        
        if region.empty:
            return None
            
        # 1. Höchsten Peak im Bereich finden
        peak_ppm = region.loc[region['intensity'].idxmax(), 'ppm']
            
        # 2. Flächenwachstum (Kumulativ) berechnen
        intensities = region['intensity'].values
        cumulative_area = np.cumsum(intensities)
        total_area = cumulative_area[-1]
        
        # In Prozent umrechnen (Growth)
        percent_growth = (cumulative_area / total_area) * 100
        
        # 3. Statistik über dem Threshold berechnen
        idx_threshold_arr = np.where(percent_growth >= threshold)[0]
        if len(idx_threshold_arr) == 0:
            return None
            
        idx_threshold = idx_threshold_arr[0]
        
        # Alle Flächenwerte ab dem Threshold-Punkt bis zum Ende
        areas_above_threshold = cumulative_area[idx_threshold:]
        average_above_threshold = np.mean(areas_above_threshold)
        std_above_threshold = np.std(areas_above_threshold)
        
        return {
            "lower_ppm": lower_ppm,
            "upper_ppm": upper_ppm,
            "peak_ppm": peak_ppm,
            "total_area": total_area,
            "stable_area": cumulative_area[idx_threshold],
            "average_above": average_above_threshold,
            "std_above": std_above_threshold,
            "percent_growth": percent_growth,
            "threshold": threshold,
            "region_df": region
        }