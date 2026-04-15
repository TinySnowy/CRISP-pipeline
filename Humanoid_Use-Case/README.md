# Humanoid Use-Case: Human POV → Robot POV Video Pipeline

Converts a human first-person POV video into a photorealistic robot POV video using the Fourier GR-1T2 humanoid's dexterous hands.

## Pipeline Overview

```
Human POV Video
      ↓
[1] retarget_video.py   — MediaPipe hand detection + dex-retargeting
      ↓
right_joints.pkl / left_joints.pkl   (robot joint angles per frame)
      ↓
[2] render_scaffold.py  — PyBullet URDF renderer
      ↓
scaffold.mp4   (3D robot hand animation)
      ↓
[3] SeedAnce 2.0 API    — scaffold + reference images → photorealistic video
      ↓
Robot POV Video
```

## Directory Structure

```
Humanoid_Use-Case/
├── README.md                        ← this file
├── SETUP.md                         ← environment setup instructions
├── robot_pov_pipeline/
│   ├── retarget_video.py            ← Step 1: video → joint angles
│   ├── render_scaffold.py           ← Step 2: joint angles → scaffold video
│   ├── configs/
│   │   ├── gr1t2_right_hand.yml     ← dex-retargeting config (right)
│   │   └── gr1t2_left_hand.yml      ← dex-retargeting config (left)
│   └── output/                      ← generated outputs (gitignored)
│       ├── right_joints.pkl
│       ├── left_joints.pkl
│       └── scaffold.mp4
├── chef_images/                     ← reference images for SeedAnce
└── Deep_Research.md                 ← background research notes
```

## Robot

**Fourier GR-1T2** with 6-DOF Fourier dexterous hand (per hand):
- 6 actuated joints: thumb yaw, thumb pitch, index/middle/ring/pinky proximal
- 5 mimic joints: thumb distal (1.06× thumb pitch), finger intermediates (0.975× proximal)
- URDF: `Wiki-GRx-URDF/Dexterous_hand/fourier_hand_6dof/urdf/fourier_{left,right}_hand_6dof.urdf`

## Quick Start

See [SETUP.md](SETUP.md) for environment setup.

```bash
# Step 1: Retarget human video → robot joint angles
conda run -n robot_pov python robot_pov_pipeline/retarget_video.py \
  --video /path/to/input.mp4 \
  --output_dir robot_pov_pipeline/output

# Step 2: Render scaffold video
conda run -n robot_pov python robot_pov_pipeline/render_scaffold.py \
  --right robot_pov_pipeline/output/right_joints.pkl \
  --left  robot_pov_pipeline/output/left_joints.pkl \
  --output robot_pov_pipeline/output/scaffold.mp4

# Step 3: Upload scaffold.mp4 + reference images to SeedAnce asset store
# then run the API call (see seedance_2.0/pipeline.py)
```
