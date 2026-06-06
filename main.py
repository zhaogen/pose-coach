"""
main.py
AI 홈 트레이닝 보조 프로그램 — 메인 실행 파일

조작법
───────────────────────────────────
  1 / 2 / 3 : 운동 전환 (스쿼트 / 푸시업 / 플랭크)
  r          : 카운트 리셋
  q / ESC    : 종료 + 결과 요약
───────────────────────────────────
"""

import sys
import csv
import time
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

from models import PoseEstimator
from exercises import SquatAnalyzer, PushupAnalyzer, PlankAnalyzer
from utils.drawing import (
    draw_info_panel,
    draw_angle_label,
    draw_stage_indicator,
)
from utils.angle import calculate_angle


# ── 운동 목록 ──────────────────────────────────────────────────
EXERCISES = {
    "1": SquatAnalyzer(),
    "2": PushupAnalyzer(),
    "3": PlankAnalyzer(),
}
KEY_LABELS = "[1]Squat  [2]Push-up  [3]Plank  [r]Reset  [q]Quit"

# ── 정확도 추적용 ──────────────────────────────────────────────
class AccuracyTracker:
    def __init__(self):
        self.total   = 0
        self.correct = 0

    def update(self, is_correct: bool):
        self.total += 1
        if is_correct:
            self.correct += 1

    @property
    def accuracy(self) -> float:
        return (self.correct / self.total * 100) if self.total else 0.0

    def reset(self):
        self.total = self.correct = 0


trackers = {k: AccuracyTracker() for k in EXERCISES}


# ── 관절 각도 표시 ─────────────────────────────────────────────
def get_display_angles(exercise_name: str, landmarks: dict) -> list:
    result = []
    combos = {
        "Squat":   [("left_shoulder","left_hip","left_knee"),
                    ("right_shoulder","right_hip","right_knee")],
        "Push-up": [("left_shoulder","left_elbow","left_wrist"),
                    ("right_shoulder","right_elbow","right_wrist")],
        "Plank":   [("left_shoulder","left_hip","left_ankle"),
                    ("right_shoulder","right_hip","right_ankle")],
    }
    for trio in combos.get(exercise_name, []):
        try:
            a, b, c = [landmarks[k] for k in trio]
            result.append((b, calculate_angle(a, b, c)))
        except KeyError:
            pass
    return result


# ── CSV 저장 ───────────────────────────────────────────────────
def save_results_csv(session_data: list):
    path = Path("workout_log.csv")
    write_header = not path.exists()
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["Date", "Exercise", "Count/Sec", "Accuracy(%)"])
        writer.writerows(session_data)
    print(f"\n[Saved] Results saved to {path.resolve()}")


# ── 결과 요약 화면 ─────────────────────────────────────────────
def show_summary_screen(session_data: list):
    """운동 결과 요약을 OpenCV 창으로 표시합니다."""
    W, H = 640, 480
    canvas = np.zeros((H, W, 3), dtype=np.uint8)

    # 배경 그라데이션
    for y in range(H):
        val = int(20 + y * 0.06)
        canvas[y] = (val, val // 2, val // 3)

    # 타이틀
    cv2.putText(canvas, "=== Workout Summary ===", (80, 60),
                cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 220, 80), 2, cv2.LINE_AA)

    # 날짜
    cv2.putText(canvas, datetime.now().strftime("%Y-%m-%d %H:%M"), (190, 95),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (180, 180, 180), 1, cv2.LINE_AA)

    # 구분선
    cv2.line(canvas, (40, 110), (600, 110), (100, 100, 100), 1)

    # 헤더
    headers = ["Exercise", "Count / Hold(s)", "Accuracy"]
    xs = [50, 240, 460]
    for x, h_txt in zip(xs, headers):
        cv2.putText(canvas, h_txt, (x, 145),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.62, (200, 200, 200), 1, cv2.LINE_AA)
    cv2.line(canvas, (40, 158), (600, 158), (80, 80, 80), 1)

    # 데이터 행
    row_colors = [(100, 220, 100), (100, 180, 255), (255, 180, 80)]
    for i, (_, name, count, acc) in enumerate(session_data):
        y = 192 + i * 52
        color = row_colors[i % len(row_colors)]
        label = f"{count}s" if name == "Plank" else f"{count}x"
        cv2.putText(canvas, name,          (xs[0], y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA)
        cv2.putText(canvas, label,         (xs[1], y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2, cv2.LINE_AA)
        cv2.putText(canvas, f"{acc:.1f}%", (xs[2], y), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (80, 220, 80) if acc >= 70 else (80, 80, 220), 2, cv2.LINE_AA)

    # 구분선
    cv2.line(canvas, (40, H - 80), (600, H - 80), (80, 80, 80), 1)
    cv2.putText(canvas, "Press any key to exit", (190, H - 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (160, 160, 160), 1, cv2.LINE_AA)

    cv2.imshow("AI PT Trainer — Summary", canvas)
    cv2.waitKey(0)
    cv2.destroyWindow("AI PT Trainer — Summary")


# ── 메인 루프 ──────────────────────────────────────────────────
def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] 웹캠을 열 수 없습니다. 카메라 연결을 확인하세요.")
        sys.exit(1)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,  720)

    estimator        = PoseEstimator(min_detection_confidence=0.6, min_tracking_confidence=0.6)
    current_key      = "1"
    current_exercise = EXERCISES[current_key]
    session_start    = time.time()

    print("=" * 52)
    print("  🏋️  AI PT Trainer  시작!")
    print(f"  {KEY_LABELS}")
    print("=" * 52)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)

        landmarks, results = estimator.process(frame)
        estimator.draw_skeleton(frame, results)

        if landmarks:
            is_correct = current_exercise.analyze(landmarks)
            trackers[current_key].update(is_correct)

            for pos, angle in get_display_angles(current_exercise.name, landmarks):
                draw_angle_label(frame, pos, angle)

        # 플랭크는 stage 표시 대신 "HOLD"
        stage_label = "HOLD" if current_exercise.name == "Plank" else current_exercise.stage.upper()

        draw_info_panel(
            frame,
            exercise_name=current_exercise.name,
            count=current_exercise.count,
            feedback=current_exercise.feedback,
            is_correct=current_exercise.is_correct,
        )
        draw_stage_indicator(frame, stage_label)

        # 정확도 우측 상단 표시
        acc = trackers[current_key].accuracy
        cv2.putText(frame, f"Accuracy: {acc:.1f}%",
                    (frame.shape[1] - 220, 38),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (80, 220, 80) if acc >= 70 else (80, 80, 220), 2, cv2.LINE_AA)

        cv2.putText(frame, KEY_LABELS, (10, frame.shape[0] - 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.46, (200, 200, 200), 1, cv2.LINE_AA)

        cv2.imshow("AI PT Trainer", frame)

        key = cv2.waitKey(1) & 0xFF

        if key in (ord("q"), 27):
            break

        elif key == ord("r"):
            current_exercise.reset()
            trackers[current_key].reset()
            print(f"[RESET] {current_exercise.name} reset")

        elif key in (ord("1"), ord("2"), ord("3")):
            new_key = chr(key)
            if new_key != current_key:
                current_key      = new_key
                current_exercise = EXERCISES[current_key]
                print(f"[MODE] {current_exercise.name} 모드 전환")

    cap.release()
    estimator.close()
    cv2.destroyAllWindows()

    # ── 세션 결과 집계 ─────────────────────────────────────────
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    session_data = []
    for k, ex in EXERCISES.items():
        if ex.count > 0 or trackers[k].total > 0:
            session_data.append((today, ex.name, ex.count, round(trackers[k].accuracy, 1)))

    if session_data:
        show_summary_screen(session_data)
        save_results_csv(session_data)
    else:
        print("\nNo workout recorded - try harder next time! 💪")


if __name__ == "__main__":
    main()
