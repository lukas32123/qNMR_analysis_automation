import MnovaFramework
import MnovaNMR
from .base import SpectralDataExtractor

class MnovaExtractor:
    """Responsible for extracting raw data from Mnova."""
    
    def __init__(self):
        self.document = MnovaFramework.Framework.instance.activeDocument
        if not self.document:
            raise ValueError("No active document found.")
            
        self.active_item = self.document.getActiveItem("NMR Spectrum")
        if not self.active_item:
            raise ValueError("No active NMR spectrum found.")
            
        self.spectrum = MnovaNMR.NMRItem(self.active_item).activeSpectrum

    def extract_metadata(self):
        """Extracts spectrum metadata, such as spectrometer frequency."""
        spec_freq = None
        try:
            variant = self.spectrum.getParam("Spectrometer Frequency")
            if variant.isValid():
                spec_freq = variant.toDouble()
        except Exception:
            pass
        return {"spectrometer_frequency": spec_freq}

    def extract_peaks(self):
        """Extracts peak picking data."""
        peaks = []
        for peak in self.spectrum.getPeaks():
            peaks.append({
                "shift": peak.shift,
                "intensity": peak.intensity,
                "uuid": peak.uuid
            })
        return peaks

    def extract_integrals(self):
        """Extracts integration data, including normalized values if available."""
        integrals = []
        integral_list = self.spectrum.getIntegrals()
        factor = getattr(integral_list, "normValue", None)
        
        for integ in integral_list:
            try:
                lower, upper = integ.horizontalRange
            except:
                lower, upper = 0, 0
                
            integrals.append({
                "lower": lower,
                "upper": upper,
                "area": integ.area,
                "norm_area": (integ.area / factor) if factor and integ.area else None
            })
        return integrals

    def extract_raw_data(self):
        """Extracts raw intensities and calculates corresponding ppm values."""
        intensities_raw = self.spectrum.reData()
        intensities = []
        try:
            # Fast memory access using the buffer protocol
            intensities = memoryview(intensities_raw).tolist()
        except:
            # Fallback: iterate manually if memoryview fails
            if hasattr(intensities_raw, "size"):
                for i in range(intensities_raw.size()):
                    intensities.append(intensities_raw[i])
                    
        coords = self.spectrum.coords[1]
        raw_data = []
        for i in range(len(intensities)):
            raw_data.append({
                "ppm": coords.ptToPpm(i),
                "intensity": intensities[i]
            })
        return raw_data

    def get_all_data(self):
        """Orchestrates the extraction and returns a clean Data Transfer Object (DTO)."""
        return {
            "metadata": self.extract_metadata(),
            "peaks": self.extract_peaks(),
            "integrals": self.extract_integrals(),
            "raw_data": self.extract_raw_data()
        }
