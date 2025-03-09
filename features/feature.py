from abc import ABC, abstractmethod

class Feature(ABC):
    @abstractmethod
    def execute(self):
        pass