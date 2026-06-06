"""
exercises/base.py
Base class for all exercise analyzers
"""

from abc import ABC, abstractmethod
from typing import Dict, Tuple


class BaseExercise(ABC):

    def __init__(self):
        self.count: int       = 0
        self.stage: str       = "up"
        self.feedback: str    = "Get ready"
        self.is_correct: bool = False

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def analyze(self, landmarks: Dict[str, Tuple[float, float]]) -> bool:
        pass

    def reset(self):
        self.count      = 0
        self.stage      = "up"
        self.feedback   = "Get ready"
        self.is_correct = False
