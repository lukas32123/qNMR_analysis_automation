import pandas as pd
import numpy as np

class NMRProcessor:
    def __init__(self, csv_path, spectrometer_freq_mhz=500):
        self.spectrometer_freq_mhz = spectrometer_freq_mhz

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

    def _hz_to_ppm(self, hz):
        """Rechnet Frequenz in ppm um, basierend auf der Spektrometer-Frequenz."""
        return hz / self.spectrometer_freq_mhz

    def _get_idx_for_ppm(self, region_df, target_ppm):
        """Gibt den Array-Index zurück, der dem target_ppm am nächsten liegt."""
        return (region_df['ppm'] - target_ppm).abs().idxmin()

    def integrate_region(self, lower_ppm, upper_ppm, threshold=99.7, threshold_p2=99.3):
        """
        Koordinator-Methode (Facade): Findet das Peak-Zentrum, definiert ein 
        ausreichend breites Fenster für die Satelliten und delegiert die Berechnung.
        """
        # 1. Den Peak im übergebenen (oft zu schmalen) Bereich finden
        narrow_mask = (self.df['ppm'] >= lower_ppm) & (self.df['ppm'] <= upper_ppm)
        narrow_region = self.df[narrow_mask]
        
        if narrow_region.empty:
            return None
            
        peak_idx = narrow_region['intensity'].idxmax()
        peak_ppm = narrow_region.loc[peak_idx, 'ppm']
        
        # 1.5 Dynamisches "Safe-Window": Wir nehmen +/- 0.3 ppm um das Zentrum herum.
        # Das garantiert bei 500/600 MHz, dass die 220 Hz (+/- 0.22 ppm) locker reinpassen.
        safe_margin = 0.3 
        wide_mask = (self.df['ppm'] >= (peak_ppm - safe_margin)) & (self.df['ppm'] <= (peak_ppm + safe_margin))
        region = self.df[wide_mask].copy().reset_index(drop=True)

        if region.empty:
            return None

        # 2. Physikalische Fenster berechnen (40 Hz Core und 220 Hz Total)
        core_offset = self._hz_to_ppm(20)   # +/- 20 Hz ergibt das 40 Hz Fenster [cite: 79]
        total_offset = self._hz_to_ppm(110) # +/- 110 Hz ergibt das 220 Hz Fenster [cite: 70, 77]

        # Beachte: ppm ist absteigend sortiert! Links = höherer ppm-Wert, Rechts = niedrigerer ppm-Wert.
        core_idx_left = self._get_idx_for_ppm(region, peak_ppm + core_offset)
        core_idx_right = self._get_idx_for_ppm(region, peak_ppm - core_offset)
        total_idx_left = self._get_idx_for_ppm(region, peak_ppm + total_offset)
        total_idx_right = self._get_idx_for_ppm(region, peak_ppm - total_offset)
            
        # Debugging Output (jetzt an der richtigen Stelle innerhalb der Funktion)
        print(f"--- DEBUG PEAK {peak_ppm:.3f} ---")
        print(f"New Wide Region Borders: {region['ppm'].iloc[0]:.3f} to {region['ppm'].iloc[-1]:.3f}")
        print(f"Core Offset in ppm: {core_offset:.5f}")
        print(f"Total Offset in ppm: {total_offset:.5f}")
        print(f"Core Indices: Links={core_idx_left}, Rechts={core_idx_right}")
        print(f"Total Indices: Links={total_idx_left}, Rechts={total_idx_right}")
        print("---------------------------------")

        # 3. Delegation der mathematischen Profile
        profile_1_growth = self._calc_profile_1(region, core_idx_left, core_idx_right, total_idx_left, total_idx_right)
        profile_2_growth = self._calc_profile_2(region, core_idx_left, core_idx_right, total_idx_left, total_idx_right)
        
        # 4. Statistik für Profil 1 berechnen
        idx_threshold_arr = np.where(profile_1_growth >= threshold)[0]
        if len(idx_threshold_arr) == 0:
            return None
            
        idx_threshold = idx_threshold_arr[0]
        areas_above_threshold = profile_1_growth[idx_threshold:]
        
        return {
            "lower_ppm": lower_ppm,
            "upper_ppm": upper_ppm,
            "peak_ppm": peak_ppm,
            "total_area": region['intensity'].sum(),
            "average_above": np.mean(areas_above_threshold),
            "std_above": np.std(areas_above_threshold),
            "percent_growth": profile_1_growth,
            "percent_growth_p2": profile_2_growth,  
            "threshold": threshold,
            "threshold_p2": threshold_p2,           
            "region_df": region
        }

    def _calc_profile_1(self, region, core_idx_left, core_idx_right, total_idx_left, total_idx_right):
        """
        Profil 1: Sukzessive Integration (gleichzeitige Ausdehnung von den Rändern des Core-Signals). [cite: 80]
        """
        intensities = region['intensity'].values
        left_idx = core_idx_left
        right_idx = core_idx_right
        
        areas = []
        # Nach außen wandern, bis die Total-Grenzen erreicht sind
        while left_idx >= total_idx_left and right_idx <= total_idx_right:
            current_area = np.sum(intensities[left_idx:right_idx+1])
            areas.append(current_area)
            left_idx -= 1
            right_idx += 1
            
        areas = np.array(areas)
        total_area = areas[-1] if len(areas) > 0 else 1
        return (areas / total_area) * 100

    def _calc_profile_2(self, region, core_idx_left, core_idx_right, total_idx_left, total_idx_right):
        """
        Profil 2: Konsekutive Integration in zwei entgegengesetzte Richtungen ausgehend vom Core-Signal. [cite: 81]
        """
        intensities = region['intensity'].values

        # Teil 1: Ausdehnung vom Core nach rechts
        areas_right = []
        right_idx = core_idx_right
        while right_idx <= total_idx_right:
            current_area = np.sum(intensities[core_idx_left:right_idx+1])
            areas_right.append(current_area)
            right_idx += 1

        # Teil 2: Ausdehnung vom Core nach links (startet eins neben dem Core)
        areas_left = []
        left_idx = core_idx_left - 1 
        while left_idx >= total_idx_left:
            current_area = np.sum(intensities[left_idx:core_idx_right+1])
            areas_left.append(current_area)
            left_idx -= 1

        # Kombinieren der beiden Teile zu einer Kurve [cite: 82]
        # Um die visuelle Symmetrie (wie in MATLAB und im Paper) zu erzeugen, wird die linke Seite gespiegelt
        areas_right.reverse()
        combined_areas = np.array(areas_left + areas_right)
        
        total_area = np.max(combined_areas) if len(combined_areas) > 0 else 1
        return (combined_areas / total_area) * 100