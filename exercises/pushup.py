"""
exercises/pushup.py
- 카운트: 팔꿈치 각도 기반
- 자세 체크: 몸통 직선 무너지면 경고
- 카운트는 자세 오류 있어도 올라감 (경고만 표시)
"""

from typing import Dict, Tuple
from utils.angle import calculate_angle
from .base import BaseExercise


class PushupAnalyzer(BaseExercise):

    ELBOW_DOWN_MAX = 115
    ELBOW_UP_MIN   = 150
    BODY_LINE_MIN  = 150   # 몸통 직선 최소 각도

    @property
    def name(self) -> str:
        return "Push-up"

    def analyze(self, landmarks: Dict[str, Tuple[float, float]]) -> bool:
        try:
            shoulder = landmarks.get("left_shoulder") or landmarks["right_shoulder"]
            elbow    = landmarks.get("left_elbow")    or landmarks["right_elbow"]
            wrist    = landmarks.get("left_wrist")    or landmarks["right_wrist"]
            hip      = landmarks.get("left_hip")      or landmarks["right_hip"]
            knee     = landmarks.get("left_knee")     or landmarks["right_knee"]
        except KeyError:
            self.feedback   = "Show arms to camera"
            self.is_correct = False
            return False

        elbow_angle = calculate_angle(shoulder, elbow, wrist)
        body_angle  = calculate_angle(shoulder, hip, knee)

        # ── 스테이지 전환 ──
        if elbow_angle < self.ELBOW_DOWN_MAX and self.stage == "up":
            self.stage     = "down"
            self._was_down = True

        if elbow_angle > self.ELBOW_UP_MIN and self.stage == "down":
            self.stage = "up"
            if getattr(self, "_was_down", False):
                self.count += 1   # 자세 오류 있어도 카운트
                self._was_down = False

        # ── 자세 피드백 (카운트와 별개) ──
        errors = []
        if body_angle < self.BODY_LINE_MIN:
            if hip[1] < shoulder[1]:
                errors.append("Hips too high!")
            else:
                errors.append("Hips sagging - core tight!")

        if errors:
            self.feedback   = " | ".join(errors)
            self.is_correct = False
        else:
            self.feedback   = "Push up!" if self.stage == "down" else "Go down!"
            self.is_correct = True

        return self.is_correct
