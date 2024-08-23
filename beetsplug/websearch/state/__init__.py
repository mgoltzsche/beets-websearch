from typing import Dict, List
from abc import ABC, abstractmethod


class Repository(ABC):

    @abstractmethod
    def list(self) -> List[Dict]:
        pass

    @abstractmethod
    def get(self, id: str) -> Dict:
        pass

    @abstractmethod
    def save(self, res: Dict):
        pass

    @abstractmethod
    def delete(self, id: str):
        pass
