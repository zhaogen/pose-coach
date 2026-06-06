"""
exercises/squat.py
- 카운트: 어깨-힙-무릎 각도 기반 (발목 불필요)
- 자세 체크: 무릎이 너무 안 굽혀지거나 상체가 너무 숙여지면 경고
- 카운트는 자세 오류 있어도 올라감 (경고만 표시)
"""

import math
from typing import Dict, Tuple
from utils.angle import calculate_angle
from .base import BaseExercise


class SquatAnalyzer(BaseExercise):

    HIP_DOWN_MAX = 110   # 이 각도 이하면 DOWN 인정
    HIP_UP_MIN   = 150   # 이 각도 이상이면 UP 인정
    HIP_DOWN_DEEP = 60   # 이보다 작으면 너무 깊이 내려간 것
    LEAN_MAX     = 55    # 상체 전경 최대 허용 각도

    @property
    def name(self) -> str:
        return "Squat"

    def analyze(self, landmarks: Dict[str, Tuple[float, float]]) -> bool:
        try:
            shoulder = landmarks.get("left_shoulder") or landmarks["right_shoulder"]
            hip      = landmarks.get("left_hip")      or landmarks["right_hip"]
            knee     = landmarks.get("left_knee")     or landmarks["right_knee"]
        except KeyError:
            self.feedback   = "Show upper body to camera"
            self.is_correct = False
            return False

        hip_angle = calculate_angle(shoulder, hip, knee)

        # 상체 기울기 계산
        dx = abs(shoulder[0] - hip[0])
        dy = abs(shoulder[1] - hip[1]) + 1e-6
        lean_angle = math.degrees(math.atan2(dx, dy))

        # ── 스테이지 전환 ──
        if hip_angle < self.HIP_DOWN_MAX and self.stage == "up":
            self.stage     = "down"
            self._was_down = True

        if hip_angle > self.HIP_UP_MIN and self.stage == "down":
            self.stage = "up"
            if getattr(self, "_was_down", False):
                self.count += 1   # 자세 오류 있어도 카운트
                self._was_down = False

        # ── 자세 피드백 (카운트와 별개) ──
        errors = []
        if self.stage == "down":
            if hip_angle < self.HIP_DOWN_DEEP:
                errors.append("Too deep!")
            if lean_angle > self.LEAN_MAX:
                errors.append("Keep back straight!")

        if errors:
            self.feedback   = " | ".join(errors)
            self.is_correct = False
        else:
            self.feedback   = "Hold it!" if self.stage == "down" else "Squat down!"
            self.is_correct = True

        return self.is_correct
