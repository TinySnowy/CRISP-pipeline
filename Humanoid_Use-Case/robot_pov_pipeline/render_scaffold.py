"""
Renders scaffold video of GR-1 Fourier hands using PyBullet.
Mirrors dex-retargeting's render_robot_hand.py (SAPIEN) logic exactly,
but using PyBullet DIRECT as the renderer.

Renders right and left hands side by side from a fixed camera.
Input:  output/right_joints.pkl, output/left_joints.pkl
Output: output/scaffold.mp4
"""

import argparse
import pickle
from pathlib import Path

import cv2
import numpy as np
import pybullet as p
import pybullet_data
import tqdm

RIGHT_URDF = "/Users/bytedance/Documents/trae_projects/CRISP-pipeline/Wiki-GRx-URDF/Dexterous_hand/fourier_hand_6dof/urdf/fourier_right_hand_6dof.urdf"
LEFT_URDF  = "/Users/bytedance/Documents/trae_projects/CRISP-pipeline/Wiki-GRx-URDF/Dexterous_hand/fourier_hand_6dof/urdf/fourier_left_hand_6dof.urdf"

IMG_W, IMG_H = 800, 600


def get_active_joint_map(robot_id):
    """Return ordered list of (joint_index, joint_name) for non-fixed joints."""
    joints = []
    for i in range(p.getNumJoints(robot_id)):
        info = p.getJointInfo(robot_id, i)
        jtype = info[2]
        name  = info[1].decode()
        if jtype != p.JOINT_FIXED:
            joints.append((i, name))
    return joints


def build_retargeting_to_pybullet_index(retargeting_joint_names, pybullet_joints):
    """
    Map retargeting joint order → pybullet joint order.
    Mirrors the retargeting_to_sapien index map in render_robot_hand.py.
    """
    pb_names = [name for _, name in pybullet_joints]
    index_map = []
    for pb_name in pb_names:
        if pb_name in retargeting_joint_names:
            index_map.append(retargeting_joint_names.index(pb_name))
        else:
            index_map.append(None)
    return index_map


# Mimic relationships: mimic_joint_name -> (source_joint_name, multiplier)
# Extracted directly from fourier_hand_6dof URDF
MIMIC_RIGHT = {
    "R_thumb_distal_joint":        ("R_thumb_proximal_pitch_joint", 1.06),
    "R_index_intermediate_joint":  ("R_index_proximal_joint",       0.975),
    "R_middle_intermediate_joint": ("R_middle_proximal_joint",      0.975),
    "R_ring_intermediate_joint":   ("R_ring_proximal_joint",        0.975),
    "R_pinky_intermediate_joint":  ("R_pinky_proximal_joint",       0.975),
}
MIMIC_LEFT = {
    "L_thumb_distal_joint":        ("L_thumb_proximal_pitch_joint", 1.06),
    "L_index_intermediate_joint":  ("L_index_proximal_joint",       0.975),
    "L_middle_intermediate_joint": ("L_middle_proximal_joint",      0.975),
    "L_ring_intermediate_joint":   ("L_ring_proximal_joint",        0.975),
    "L_pinky_intermediate_joint":  ("L_pinky_proximal_joint",       0.975),
}


def set_qpos(robot_id, pybullet_joints, index_map, qpos, mimic_map):
    # Build name->angle dict for this frame
    joint_angles = {}
    for (joint_idx, name), retarget_idx in zip(pybullet_joints, index_map):
        if retarget_idx is not None:
            angle = qpos[retarget_idx]
            p.resetJointState(robot_id, joint_idx, angle)
            joint_angles[name] = angle

    # Enforce mimic joints manually (PyBullet ignores URDF mimic tags)
    name_to_idx = {name: idx for idx, name in pybullet_joints}
    for mimic_name, (source_name, multiplier) in mimic_map.items():
        if source_name in joint_angles and mimic_name in name_to_idx:
            mimic_angle = joint_angles[source_name] * multiplier
            p.resetJointState(robot_id, name_to_idx[mimic_name], mimic_angle)


def render_scaffold(right_pkl: str, left_pkl: str, output_path: str):
    with open(right_pkl, "rb") as f:
        right = pickle.load(f)
    with open(left_pkl, "rb") as f:
        left = pickle.load(f)

    right_data         = right["data"]
    left_data          = left["data"]
    right_joint_names  = right["meta_data"]["joint_names"]
    left_joint_names   = left["meta_data"]["joint_names"]
    fps                = right["meta_data"].get("fps", 24.0)
    n_frames           = min(len(right_data), len(left_data))

    print(f"Rendering {n_frames} frames at {fps:.1f} fps")

    # PyBullet headless
    p.connect(p.DIRECT)
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.setGravity(0, 0, 0)

    # Place right hand to the right, left hand to the left
    # Orientation: palm facing camera (along -Y axis), fingers pointing up (+Z)
    right_pos = [0.12, 0.0, 0.0]
    left_pos  = [-0.12, 0.0, 0.0]
    palm_orn  = p.getQuaternionFromEuler([1.5708, 0, 0])   # palm facing +Y (toward camera)
    left_orn  = p.getQuaternionFromEuler([1.5708, 0, 3.14159])

    right_id = p.loadURDF(RIGHT_URDF, right_pos, palm_orn, useFixedBase=True)
    left_id  = p.loadURDF(LEFT_URDF,  left_pos,  left_orn, useFixedBase=True)

    right_pb_joints = get_active_joint_map(right_id)
    left_pb_joints  = get_active_joint_map(left_id)

    right_index_map = build_retargeting_to_pybullet_index(right_joint_names, right_pb_joints)
    left_index_map  = build_retargeting_to_pybullet_index(left_joint_names,  left_pb_joints)

    # Fixed camera — looking straight at the hands from the front
    # Matches SAPIEN's cam.set_local_pose([0.50, 0, 0.0])
    view_matrix = p.computeViewMatrix(
        cameraEyePosition    = [0.0, -0.45, 0.0],
        cameraTargetPosition = [0.0,  0.0,  0.0],
        cameraUpVector       = [0.0,  0.0,  1.0],
    )
    proj_matrix = p.computeProjectionMatrixFOV(
        fov=55, aspect=IMG_W/IMG_H, nearVal=0.05, farVal=2.0
    )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(
        output_path,
        cv2.VideoWriter_fourcc(*"avc1"),
        fps,
        (IMG_W, IMG_H),
    )

    for i in tqdm.tqdm(range(n_frames)):
        set_qpos(right_id, right_pb_joints, right_index_map, right_data[i], MIMIC_RIGHT)
        set_qpos(left_id,  left_pb_joints,  left_index_map,  left_data[i], MIMIC_LEFT)

        p.stepSimulation()

        _, _, rgba, _, _ = p.getCameraImage(
            IMG_W, IMG_H,
            viewMatrix=view_matrix,
            projectionMatrix=proj_matrix,
            renderer=p.ER_TINY_RENDERER,
            lightDirection=[1, 2, 3],
            lightColor=[1, 1, 1],
            lightDistance=3,
            lightAmbientCoeff=0.6,
            lightDiffuseCoeff=0.8,
            lightSpecularCoeff=0.1,
        )

        img = np.array(rgba, dtype=np.uint8).reshape(IMG_H, IMG_W, 4)
        bgr = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
        writer.write(bgr)

    writer.release()
    p.disconnect()
    print(f"Done → {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--right",  default="output/right_joints.pkl")
    parser.add_argument("--left",   default="output/left_joints.pkl")
    parser.add_argument("--output", default="output/scaffold.mp4")
    args = parser.parse_args()
    render_scaffold(args.right, args.left, args.output)
