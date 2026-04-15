"""
Renders scaffold video of Inspire hand using SAPIEN.
Delegates directly to dex-retargeting's render_robot_hand.py.

Input:  output/right_joints.pkl  (or left)
Output: output/scaffold.mp4
"""

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT    = Path(__file__).parent.parent.parent
RENDER_SCRIPT = REPO_ROOT / "dex-retargeting" / "example" / "vector_retargeting" / "render_robot_hand.py"


def render_scaffold(pkl_path: str, output_path: str):
    cmd = [
        sys.executable, str(RENDER_SCRIPT),
        "--pickle-path",       pkl_path,
        "--output-video-path", output_path,
        "--headless",
    ]
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pkl",    required=True, help="Path to right_joints.pkl or left_joints.pkl")
    parser.add_argument("--output", default="output/scaffold.mp4")
    args = parser.parse_args()
    render_scaffold(args.pkl, args.output)
