"""
Human POV video → Inspire hand robot joint angles
Calls dex-retargeting's detect_from_video.py directly for right hand.
Output: right_joints.pkl
"""

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT      = Path(__file__).parent.parent.parent
DETECT_SCRIPT  = REPO_ROOT / "dex-retargeting" / "example" / "vector_retargeting" / "detect_from_video.py"
ROBOT_DIR      = REPO_ROOT / "dex-retargeting" / "assets" / "robots" / "hands"


def retarget_video(video_path: str, output_dir: str):
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    for hand in ["right", "left"]:
        out_pkl = str(Path(output_dir) / f"{hand}_joints.pkl")
        cmd = [
            sys.executable, str(DETECT_SCRIPT),
            "--robot-name",       "inspire",
            "--video-path",       video_path,
            "--output-path",      out_pkl,
            "--retargeting-type", "dexpilot",
            "--hand-type",        hand,
        ]
        print(f"\n--- Retargeting {hand} hand ---")
        print(f"Running: {' '.join(cmd)}")

        env = {"URDF_DIR": str(ROBOT_DIR)}
        import os
        full_env = {**os.environ, **env}

        # detect_from_video.py must be run from its own directory (imports single_hand_detector)
        subprocess.run(cmd, check=True, cwd=str(DETECT_SCRIPT.parent))
        print(f"Saved → {out_pkl}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--video",      required=True)
    parser.add_argument("--output_dir", default="output")
    args = parser.parse_args()
    retarget_video(args.video, args.output_dir)
