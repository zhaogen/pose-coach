"""
utils/angle.py
관절 각도 계산 유틸리티
"""

import numpy as np


def calculate_angle(a, b, c) -> float:
    """
    세 점(a, b, c)으로 이루어진 각도를 계산합니다.
    b가 꼭짓점(관절)입니다.

    Args:
        a, b, c: (x, y) 좌표 튜플 또는 리스트

    Returns:
        float: 0~180도 사이의 각도
    """
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    c = np.array(c, dtype=float)

    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
    angle = np.degrees(np.arccos(cosine_angle))
    return float(angle)
