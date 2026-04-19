import matplotlib.pyplot as plt
import pathlib

class NMRVisualizer:
    def __init__(self, output_dir):
        # Wir erwarten jetzt einen Ordner-Pfad, keinen Datei-Pfad
        self.output_dir = pathlib.Path(output_dir)

    def generate_all_reports(self, full_df, results):
        """Erstellt alle drei PDFs wie von der Vorgängerin definiert."""
        
        # PDF 1: Nacktes Spektrum
        plt.figure(figsize=(10, 6))
        plt.plot(full_df['ppm'], full_df['intensity'], color='black', lw=0.7)
        plt.gca().invert_xaxis()
        plt.xlabel('Chemical Shift [ppm]')
        plt.ylabel('Intensity [a.u.]')
        plt.title('Raw NMR Spectrum')
        plt.savefig(self.output_dir / "1_Raw_Spectrum.pdf")
        plt.close()

        # PDF 2: Integriertes Spektrum (mit Peak-Infos)
        plt.figure(figsize=(10, 6))
        plt.plot(full_df['ppm'], full_df['intensity'], color='black', lw=0.5)
        for i, res in enumerate(results):
            label_text = (f"Peak {i+1} at {res['peak_ppm']:.3f} ppm\n"
                          f"Range: {res['lower_ppm']} - {res['upper_ppm']}\n"
                          f"Avg Area (>{res['threshold']}%): {res['average_above']:.2f}")
            plt.fill_between(res['region_df']['ppm'], res['region_df']['intensity'], 
                             alpha=0.3, label=label_text)
        plt.gca().invert_xaxis()
        plt.xlabel('Chemical Shift [ppm]')
        plt.ylabel('Intensity [a.u.]')
        plt.title('NMR Spectrum with Integrated Areas')
        plt.legend(loc='upper right', fontsize=8)
        plt.savefig(self.output_dir / "2_Integrated_Spectrum.pdf")
        plt.close()

        # PDF 3: Normalized Area Growth (Threshold Plot)
        plt.figure(figsize=(10, 6))
        colors = ['orange', 'steelblue', 'darkgreen', 'red', 'purple']
        
        for i, res in enumerate(results):
            c = colors[i % len(colors)]
            steps = range(1, len(res['percent_growth']) + 1)
            plt.plot(steps, res['percent_growth'], marker='.', markersize=2, 
                     color=c, label=f'Peak {i+1} Area Growth')
            
            # Die Threshold-Linie der Vorgängerin
            plt.axhline(y=res['threshold'], color=c, linestyle='--', lw=1, 
                        label=f'Threshold {res["threshold"]}%')
            
        plt.xlabel('Integration Step (Datapoints)')
        plt.ylabel('Area [%]')
        plt.ylim(97, 100) # Fokus auf die obersten Prozent, wie bei der Vorgängerin
        plt.grid(True, alpha=0.3)
        plt.title('Normalized Increase of Area by Integration Step')
        plt.legend(loc='lower right', fontsize=8)
        plt.savefig(self.output_dir / "3_Area_Growth_Plot.pdf")
        plt.close()