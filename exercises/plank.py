"""
exercises/plank.py
- 카운트: 올바른 자세 유지 시간(초)
- 자세 체크: 몸통 각도, 엉덩이 높낮이 경고
"""

import time
from typing import Dict, Tuple
from utils.angle import calculate_angle
from .base import BaseExercise


class PlankAnalyzer(BaseExercise):

    BODY_LINE_MIN = 150
    HOLD_INTERVAL = 1.0

    @property
    def name(self) -> str:
        return "Plank"

    def __init__(self):
        super().__init__()
        self._last_tick: float = 0.0
        self.feedback = "Get into plank position"

    def analyze(self, landmarks: Dict[str, Tuple[float, float]]) -> bool:
        try:
            shoulder = landmarks.get("left_shoulder") or landmarks["right_shoulder"]
            hip      = landmarks.get("left_hip")      or landmarks["right_hip"]
            knee     = landmarks.get("left_knee")     or landmarks["right_knee"]
        except KeyError:
            self.feedback   = "Show body to camera"
            self.is_correct = False
            return False

        body_angle = calculate_angle(shoulder, hip, knee)

        now = time.time()
        if body_angle > self.BODY_LINE_MIN:
            if self._last_tick == 0.0:
                self._last_tick = now
            elif now - self._last_tick >= self.HOLD_INTERVAL:
                self.count += int((now - self._last_tick) / self.HOLD_INTERVAL)
                self._last_tick = now
            mins, secs = divmod(self.count, 60)
            self.feedback   = f"Hold! {mins:02d}:{secs:02d} - Keep going!"
            self.is_correct = True
        else:
            self._last_tick = 0.0
            if hip[1] < shoulder[1]:
                self.feedback = "Hips too high - lower them!"
            else:
                self.feedback = "Hips sagging - core tight!"
            self.is_correct = False

        return self.is_correct

    def reset(self):
        super().reset()
        self._last_tick = 0.0
        self.feedback   = "Get into plank position"
        self.stage      = "hold"
