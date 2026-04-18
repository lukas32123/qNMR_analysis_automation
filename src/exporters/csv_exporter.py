import csv

class CSVExporter:
    """Responsible for formatting and writing the extracted data to a CSV file."""
    
    def __init__(self, filepath):
        self.filepath = filepath

    def export(self, data):
        """Writes the provided data dictionary to the specified CSV filepath."""
        with open(self.filepath, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=',') 
            
            # Metadata
            freq = data["metadata"].get("spectrometer_frequency")
            if freq:
                writer.writerow(["SPECTROMETER FREQUENCY (MHz)", freq])
            writer.writerow([])
            
            # Peaks
            writer.writerow(["PEAK DATA"])
            writer.writerow(["shift_ppm", "intensity", "uuid"])
            for p in data["peaks"]:
                writer.writerow([
                    round(p["shift"], 2) if p["shift"] is not None else "", 
                    round(p["intensity"], 4) if p["intensity"] is not None else "", 
                    p["uuid"] or ""
                ])
            writer.writerow([])
            
            # Integrals
            writer.writerow(["INTEGRAL DATA"])
            writer.writerow(["lower_ppm", "upper_ppm", "norm_integral", "raw_area"])
            for i in data["integrals"]:
                writer.writerow([
                    round(i["lower"], 2) if i["lower"] is not None else "",
                    round(i["upper"], 2) if i["upper"] is not None else "",
                    round(i["norm_area"], 2) if i["norm_area"] is not None else "",
                    round(i["area"], 2) if i["area"] is not None else ""
                ])
            writer.writerow([])
            
            # Raw Data
            writer.writerow(["RAW SPECTRUM"])
            writer.writerow(["ppm", "intensity"])
            for r in data["raw_data"]:
                writer.writerow([r["ppm"], r["intensity"]])
                
        print(f"Data successfully exported to: {self.filepath}")

