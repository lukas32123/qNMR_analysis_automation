from abc import ABC, abstractmethod

class SpectralDataExtractor(ABC):
    @abstractmethod
    def get_all_data(self) -> dict:
        pass