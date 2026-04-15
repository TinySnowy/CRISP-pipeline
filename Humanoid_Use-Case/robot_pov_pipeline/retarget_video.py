"""
Human POV video → Inspire hand robot joint angles
Thin wrapper around dex-retargeting's detect_from_video.py logic.
Processes right and left hands separately.
Output: right_joints.pkl and left_joints.pkl
"""

import argparse
import pickle
import sys
from pathlib import Path

import cv2
import numpy as np
import tqdm

# Add dex-retargeting example dir to path for SingleHandDetector
REPO_ROOT = Path(__file__).parent.parent.parent
DEX_EXAMPLE_DIR = REPO_ROOT / "dex-retargeting" / "example" / "vector_retargeting"
sys.path.insert(0, str(DEX_EXAMPLE_DIR))

from dex_retargeting.constants import RobotName, RetargetingType, HandType, get_default_config_path
from dex_retargeting.retargeting_config import RetargetingConfig
from single_hand_detector import SingleHandDetector


def retarget_video(video_path: str, output_dir: str):
    # Load inspire hand configs (built-in, no custom URDF needed)
    right_config_path = get_default_config_path(RobotName.inspire, RetargetingType.vector, HandType.right)
    left_config_path  = get_default_config_path(RobotName.inspire, RetargetingType.vector, HandType.left)

    # Set default URDF dir to dex-retargeting assets
    robot_dir = REPO_ROOT / "dex-retargeting" / "assets" / "robots" / "hands"
    RetargetingConfig.set_default_urdf_dir(str(robot_dir))

    right_cfg = RetargetingConfig.load_from_file(str(right_config_path))
    left_cfg  = RetargetingConfig.load_from_file(str(left_config_path))
    right_retargeting = right_cfg.build()
    left_retargeting  = left_cfg.build()

    right_detector = SingleHandDetector(hand_type="Right", selfie=True)
    left_detector  = SingleHandDetector(hand_type="Left",  selfie=True)

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

            for detector, retargeting, data_list in [
                (right_detector, right_retargeting, right_data),
                (left_detector,  left_retargeting,  left_data),
            ]:
                num_box, joint_pos, _, _ = detector.detect(rgb)
                if num_box == 0:
                    pbar.update(0)
                    continue

                indices = retargeting.optimizer.target_link_human_indices
                if retargeting.optimizer.retargeting_type == "POSITION":
                    ref = joint_pos[indices, :]
                else:
                    origin_idx = indices[0, :]
                    task_idx   = indices[1, :]
                    ref = joint_pos[task_idx, :] - joint_pos[origin_idx, :]

                qpos = retargeting.retarget(ref)
                data_list.append(qpos)

            pbar.update(1)

    cap.release()

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    for hand, retargeting, data, config_path in [
        ("right", right_retargeting, right_data, right_config_path),
        ("left",  left_retargeting,  left_data,  left_config_path),
    ]:
        meta = {
            "config_path": str(config_path),
            "dof": len(retargeting.optimizer.robot.dof_joint_names),
            "joint_names": list(retargeting.optimizer.robot.dof_joint_names),
            "fps": fps,
        }
        out_path = Path(output_dir) / f"{hand}_joints.pkl"
        with open(out_path, "wb") as f:
            pickle.dump({"meta_data": meta, "data": data}, f)
        print(f"{hand.capitalize()}: {len(data)} frames → {out_path}")
        print(f"  joint names: {meta['joint_names']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--video",      required=True)
    parser.add_argument("--output_dir", default="output")
    args = parser.parse_args()
    retarget_video(args.video, args.output_dir)
