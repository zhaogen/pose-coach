"""
models/pose_estimator.py
MediaPipe Pose 래퍼 클래스
"""

import cv2
import mediapipe as mp
import numpy as np
from typing import Optional, Tuple, Dict


class PoseEstimator:
    """
    MediaPipe Pose를 감싸는 래퍼 클래스.
    프레임을 입력받아 랜드마크 좌표 딕셔너리를 반환합니다.
    """

    # MediaPipe 랜드마크 인덱스 → 이름 매핑
    LANDMARK_NAMES = {
        0:  "nose",
        11: "left_shoulder",  12: "right_shoulder",
        13: "left_elbow",     14: "right_elbow",
        15: "left_wrist",     16: "right_wrist",
        23: "left_hip",       24: "right_hip",
        25: "left_knee",      26: "right_knee",
        27: "left_ankle",     28: "right_ankle",
    }

    def __init__(
        self,
        static_image_mode: bool = False,
        model_complexity: int = 1,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ):
        self.mp_pose    = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_styles  = mp.solutions.drawing_styles

        self.pose = self.mp_pose.Pose(
            static_image_mode=static_image_mode,
            model_complexity=model_complexity,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

    def process(self, frame) -> Tuple[Optional[Dict[str, Tuple[float, float]]], any]:
        """
        프레임을 처리하여 랜드마크 좌표를 반환합니다.

        Returns:
            landmarks_dict: {이름: (x_pixel, y_pixel)} 또는 None (미검출 시)
            results: MediaPipe raw results (스켈레톤 드로잉에 사용)
        """
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = self.pose.process(rgb)
        rgb.flags.writeable = True

        if not results.pose_landmarks:
            return None, results

        lm = results.pose_landmarks.landmark
        landmarks_dict: Dict[str, Tuple[float, float]] = {}
        for idx, name in self.LANDMARK_NAMES.items():
            landmarks_dict[name] = (lm[idx].x * w, lm[idx].y * h)

        return landmarks_dict, results

    def draw_skeleton(self, frame, results):
        """MediaPipe 기본 스켈레톤을 프레임에 그립니다."""
        if results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing.DrawingSpec(
                    color=(80, 200, 80), thickness=2, circle_radius=3
                ),
                connection_drawing_spec=self.mp_drawing.DrawingSpec(
                    color=(200, 200, 200), thickness=2
                ),
            )

    def close(self):
        self.pose.close()
