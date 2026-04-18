import matplotlib.pyplot as plt
import os

class NMRVisualizer:
    """Responsible for generating plots and saving them as PDF."""
    
    def __init__(self, output_path):
        self.output_path = output_path

    def generate_report(self, full_df, results):
        """Plots the spectrum and highlights integrated areas."""
        plt.figure(figsize=(12, 6))
        plt.plot(full_df['ppm'], full_df['intensity'], color='black', lw=0.7, label='Spectrum')
        
        for i, res in enumerate(results):
            # Fill the area under the peak
            plt.fill_between(res['region_df']['ppm'], res['region_df']['intensity'], 
                             alpha=0.3, label=f"Peak {i+1} Area: {res['stable_area']:.2f}")
            
        plt.gca().invert_xaxis()
        plt.xlabel('Chemical Shift [ppm]')
        plt.ylabel('Intensity [a.u.]')
        plt.title('Automated NMR Integration Report')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.savefig(self.output_path)
        plt.close()