import matplotlib.pyplot as plt
import pathlib

"""
Dieses Modul übernimmt die visuelle Repräsentation von NMR-Daten.

Die Architektur wurde so optimiert, dass globale Übersichtsbilder von 
peakspezifischen Detailanalysen (Zoom-Ansichten) getrennt werden, um die 
analytische Aussagekraft der Berichte zu maximieren.
"""

class NMRVisualizer:
    def __init__(self, output_dir, x_range_global=(10, 0)):
        """
        Initialisiert den Visualizer.

        Args:
            output_dir (str/Path): Zielordner für die PDFs.
            x_range_global (tuple): Der Bereich für das globale Rohspektrum.
        """
        self.output_dir = pathlib.Path(output_dir)
        self.x_range_global = x_range_global

    def generate_all_reports(self, full_df, results):
        """
        Steuert die Berichterstellung gemäß GRASP-Prinzipien. 
        Erzeugt ein globales Rohspektrum und individuelle Analysen pro Peak.

        Args:
            full_df (pd.DataFrame): Vollständiger Datensatz.
            results (list): Liste der Peak-Ergebnisse.
        """
        # 1. Globales Rohspektrum nur einmal erzeugen (außerhalb der Schleife)
        self._plot_raw_spectrum(full_df)

        # 2. Iteration über die Ergebnisse für spezialisierte Peak-Berichte
        for i, peak_result in enumerate(results):
            peak_id = i + 1
            self._plot_integrated_spectrum(full_df, peak_result, peak_id)
            self._plot_area_growth(peak_result, peak_id)

    def _plot_raw_spectrum(self, full_df):
        """Erzeugt ein einzelnes, globales PDF des gesamten Rohspektrums."""
        plt.figure(figsize=(10, 6))
        plt.plot(full_df['ppm'], full_df['intensity'], color='black', lw=0.7)
        
        plt.xlim(self.x_range_global)
        plt.xlabel('Chemical Shift [ppm]')
        plt.ylabel('Intensity [a.u.]')
        plt.title('Global Raw NMR Spectrum')
        
        plt.savefig(self.output_dir / "Raw_Spectrum.pdf")
        plt.close()

    def _plot_integrated_spectrum(self, full_df, res, peak_id):
        """
        Erzeugt eine Detailansicht des integrierten Peaks. 
        Die X-Achse wird dynamisch auf den Peak-Bereich ± 2 ppm gezoomt.
        """
        plt.figure(figsize=(10, 6))
        plt.plot(full_df['ppm'], full_df['intensity'], color='black', lw=0.5)
        
        peak_ppm = res['peak_ppm']
        label_text = (f"Peak {peak_id} at {peak_ppm:.3f} ppm\n"
                      f"Range: {res['lower_ppm']} - {res['upper_ppm']}\n"
                      f"Avg Area: {res['average_above']:.2f}")
        
        plt.fill_between(res['region_df']['ppm'], res['region_df']['intensity'], 
                         alpha=0.3, color='steelblue', label=label_text)
        
        # Dynamischer Zoom: Peak-Zentrum +/- 2 ppm
        # NMR-Konvention: Höherer Wert links (peak_ppm + 2), niedrigerer rechts (peak_ppm - 2)
        plt.xlim(peak_ppm + 0.5, peak_ppm - 0.5)
        
        plt.xlabel('Chemical Shift [ppm]')
        plt.ylabel('Intensity [a.u.]')
        plt.title(f'Integration - Peak {peak_id}')
        plt.legend(loc='upper right', fontsize=8)
        
        filename = f"Peak_{peak_id}_Integrated_Spectrum.pdf"
        plt.savefig(self.output_dir / filename)
        plt.close()

    def _plot_area_growth(self, res, peak_id):
        """Visualisiert die Integrationsstabilität für den spezifischen Peak."""
        plt.figure(figsize=(10, 6))
        steps = range(1, len(res['percent_growth']) + 1)
        
        plt.plot(steps, res['percent_growth'], marker='.', markersize=2, 
                 color='darkgreen', label='Area Growth')
        
        plt.axhline(y=res['threshold'], color='red', linestyle='--', lw=1, 
                    label=f'Threshold {res["threshold"]}%')
            
        plt.xlabel('Integration Step (Datapoints)')
        plt.ylabel('Area [%]')
        plt.ylim(97, 100) 
        plt.grid(True, alpha=0.3)
        plt.title(f'Area Stability Analysis - Peak {peak_id}')
        plt.legend(loc='lower right', fontsize=8)
        
        filename = f"Peak_{peak_id}_Area_Growth.pdf"
        plt.savefig(self.output_dir / filename)
        plt.close()