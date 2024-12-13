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
    def create(self, res: Dict):
        pass

    @abstractmethod
    def update(self, res: Dict):
        pass

    @abstractmethod
    def delete(self, id: str):
        pass
