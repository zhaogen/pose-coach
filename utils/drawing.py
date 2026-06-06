"""
utils/drawing.py
화면 시각화 유틸리티 (스켈레톤, 텍스트, UI 패널)
"""

import cv2
import numpy as np


COLOR_GREEN  = (0, 220, 100)
COLOR_RED    = (0, 60, 220)
COLOR_YELLOW = (0, 200, 255)
COLOR_WHITE  = (255, 255, 255)
COLOR_BLACK  = (0, 0, 0)
COLOR_PANEL  = (30, 30, 30)


def draw_info_panel(frame, exercise_name: str, count: int, feedback: str, is_correct: bool):
    h, w = frame.shape[:2]
    panel_w, panel_h = 300, 160
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (10 + panel_w, 10 + panel_h), COLOR_PANEL, -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

    cv2.putText(frame, exercise_name, (20, 42),
                cv2.FONT_HERSHEY_DUPLEX, 0.9, COLOR_WHITE, 2, cv2.LINE_AA)

    cv2.putText(frame, f"Count : {count}", (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, COLOR_YELLOW, 2, cv2.LINE_AA)

    status_color = COLOR_GREEN if is_correct else COLOR_RED
    status_text  = "GOOD FORM" if is_correct else "CHECK FORM"
    cv2.putText(frame, status_text, (20, 115),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2, cv2.LINE_AA)

    feedback_color = COLOR_GREEN if is_correct else COLOR_RED
    _draw_multiline_text(frame, feedback, (20, 145), 0.52, feedback_color, 1, max_width=panel_w - 10)


def draw_angle_label(frame, point, angle: float, color=COLOR_YELLOW):
    x, y = int(point[0]), int(point[1])
    cv2.putText(frame, f"{int(angle)}", (x + 8, y - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)


def draw_stage_indicator(frame, stage: str):
    h, w = frame.shape[:2]
    text = f"Stage: {stage}"
    (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
    x, y = w - tw - 20, h - 20
    cv2.putText(frame, text, (x, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLOR_WHITE, 2, cv2.LINE_AA)


def _draw_multiline_text(frame, text: str, origin, font_scale, color, thickness, max_width=280):
    words = text.split()
    line, x0, y0 = "", origin[0], origin[1]
    line_h = int(font_scale * 28)
    for word in words:
        test = (line + " " + word).strip()
        (tw, _), _ = cv2.getTextSize(test, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
        if tw > max_width and line:
            cv2.putText(frame, line, (x0, y0),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness, cv2.LINE_AA)
            y0 += line_h
            line = word
        else:
            line = test
    if line:
        cv2.putText(frame, line, (x0, y0),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness, cv2.LINE_AA)
