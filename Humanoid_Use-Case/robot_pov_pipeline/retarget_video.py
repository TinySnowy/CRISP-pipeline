"""
Human POV video → GR-1 robot hand joint angles
Uses MediaPipe Hands (solutions API) + dex-retargeting (DexPilot)
Processes right and left hands separately, matching dex-retargeting's
detect_from_video.py output format exactly.
Output: right_joints.pkl and left_joints.pkl
"""

import argparse
import pickle
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
import tqdm
from dex_retargeting.retargeting_config import RetargetingConfig

SCRIPT_DIR = Path(__file__).parent

OPERATOR2MANO_RIGHT = np.array([[0, 0, -1], [-1, 0, 0], [0, 1, 0]])
OPERATOR2MANO_LEFT  = np.array([[0, 0, -1], [ 1, 0, 0], [0, -1, 0]])


def estimate_frame(kp):
    points = kp[[0, 5, 9], :]
    x_vec = points[0] - points[2]
    pts = points - np.mean(points, axis=0, keepdims=True)
    _, _, v = np.linalg.svd(pts)
    normal = v[2, :]
    x = x_vec - np.sum(x_vec * normal) * normal
    x /= np.linalg.norm(x)
    z = np.cross(x, normal)
    if np.sum(z * (points[1] - points[2])) < 0:
        normal *= -1; z *= -1
    return np.stack([x, normal, z], axis=1)


def parse_kp3d(lm_list):
    return np.array([[lm.x, lm.y, lm.z] for lm in lm_list.landmark], dtype=np.float32)


def do_retarget(retargeting, joint_pos):
    rt = retargeting.optimizer.retargeting_type
    indices = retargeting.optimizer.target_link_human_indices
    if rt == "POSITION":
        ref = joint_pos[indices, :]
    else:
        origin_idx = indices[0, :]
        task_idx   = indices[1, :]
        ref = joint_pos[task_idx, :] - joint_pos[origin_idx, :]
    return retargeting.retarget(ref)


def detect_and_retarget(video_path: str, output_dir: str):
    right_cfg = RetargetingConfig.load_from_file(str(SCRIPT_DIR / "configs/gr1t2_right_hand.yml"))
    left_cfg  = RetargetingConfig.load_from_file(str(SCRIPT_DIR / "configs/gr1t2_left_hand.yml"))
    right_retargeting = right_cfg.build()
    left_retargeting  = left_cfg.build()

    detector = mp.solutions.hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5,
    )

    cap = cv2.VideoCapture(video_path)
    fps   = cap.get(cv2.CAP_PROP_FPS)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Processing {total} frames at {fps:.1f} fps")

    right_data = []
    left_data  = []

    with tqdm.tqdm(total=total) as pbar:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            rgb = frame[..., ::-1]
            results = detector.process(rgb)

            right_qpos = None
            left_qpos  = None

            if results.multi_hand_landmarks and results.multi_handedness:
                for lm, lm_world, handedness in zip(
                    results.multi_hand_landmarks,
                    results.multi_hand_world_landmarks,
                    results.multi_handedness,
                ):
                    label = handedness.classification[0].label

                    kp = parse_kp3d(lm_world)
                    kp = kp - kp[0:1, :]
                    op2mano = OPERATOR2MANO_RIGHT if label == "Right" else OPERATOR2MANO_LEFT
                    frame_rot = estimate_frame(kp)
                    joint_pos = kp @ frame_rot @ op2mano

                    if label == "Right":
                        right_qpos = do_retarget(right_retargeting, joint_pos)
                    else:
                        left_qpos = do_retarget(left_retargeting, joint_pos)

            # Always append — use last known pose if not detected this frame
            if right_qpos is not None:
                right_data.append(right_qpos)
            if left_qpos is not None:
                left_data.append(left_qpos)

            pbar.update(1)

    cap.release()
    detector.close()

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Save in exact same format as dex-retargeting's detect_from_video.py
    right_meta = {
        "config_path": str(SCRIPT_DIR / "configs/gr1t2_right_hand.yml"),
        "dof": len(right_retargeting.optimizer.robot.dof_joint_names),
        "joint_names": list(right_retargeting.optimizer.robot.dof_joint_names),
        "fps": fps,
    }
    left_meta = {
        "config_path": str(SCRIPT_DIR / "configs/gr1t2_left_hand.yml"),
        "dof": len(left_retargeting.optimizer.robot.dof_joint_names),
        "joint_names": list(left_retargeting.optimizer.robot.dof_joint_names),
        "fps": fps,
    }

    right_path = Path(output_dir) / "right_joints.pkl"
    left_path  = Path(output_dir) / "left_joints.pkl"

    with open(right_path, "wb") as f:
        pickle.dump({"meta_data": right_meta, "data": right_data}, f)
    with open(left_path, "wb") as f:
        pickle.dump({"meta_data": left_meta, "data": left_data}, f)

    print(f"\nRight: {len(right_data)} frames → {right_path}")
    print(f"Left:  {len(left_data)} frames → {left_path}")
    print(f"Right joint names: {right_meta['joint_names']}")
    print(f"Left  joint names: {left_meta['joint_names']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--video",      required=True)
    parser.add_argument("--output_dir", default="output")
    args = parser.parse_args()
    detect_and_retarget(args.video, args.output_dir)
