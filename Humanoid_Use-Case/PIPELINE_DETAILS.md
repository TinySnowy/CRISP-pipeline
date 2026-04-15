# Pipeline Technical Details

## Step 1 — `retarget_video.py`

**Input:** Human POV `.mp4` video
**Output:** `right_joints.pkl`, `left_joints.pkl`

### What it does

1. Loads dex-retargeting configs for left and right GR-1T2 hands
2. Opens video with OpenCV, processes each frame through MediaPipe Hands
3. For each detected hand:
   - Extracts 21 3D world landmarks (wrist-relative, in metres)
   - Estimates a coordinate frame from wrist/index/middle positions (SVD-based)
   - Rotates landmarks into MANO convention via `OPERATOR2MANO` matrix
   - Passes selected landmark positions to dex-retargeting POSITION optimizer
   - Gets back 6 joint angles for that hand
4. Saves separate `.pkl` files for right and left hands

### Output format (matches dex-retargeting's `detect_from_video.py`)

```python
{
  "meta_data": {
    "config_path": "...",
    "dof": 6,
    "joint_names": ["R_thumb_proximal_yaw_joint", ...],
    "fps": 30.0
  },
  "data": [array(6,), array(6,), ...]   # one per frame
}
```

### Retargeting config (`gr1t2_right_hand.yml`)

```yaml
retargeting:
  type: position
  urdf_path: /path/to/fourier_right_hand_6dof.urdf
  target_joint_names: [
    R_thumb_proximal_yaw_joint, R_thumb_proximal_pitch_joint,
    R_index_proximal_joint, R_middle_proximal_joint,
    R_ring_proximal_joint, R_pinky_proximal_joint
  ]
  target_link_names: [
    R_thumb_tip_link, R_index_tip_link, R_middle_tip_link,
    R_ring_tip_link, R_pinky_tip_link,
    R_thumb_proximal_pitch_link, R_index_proximal_link, R_middle_proximal_link
  ]
  target_link_human_indices: [4, 8, 12, 16, 20, 2, 6, 10]
  add_dummy_free_joint: True
  low_pass_alpha: 0.6
```

**MediaPipe landmark indices:**
- 4 = thumb tip, 8 = index tip, 12 = middle tip, 16 = ring tip, 20 = pinky tip
- 2 = thumb intermediate, 6 = index proximal, 10 = middle proximal

---

## Step 2 — `render_scaffold.py`

**Input:** `right_joints.pkl`, `left_joints.pkl`
**Output:** `scaffold.mp4` (800×600, same fps as input)

### What it does

1. Loads PyBullet in headless `DIRECT` mode (no display required)
2. Loads both hand URDFs at fixed positions (right at +X, left at -X)
3. For each frame:
   - Maps retargeting joint order → PyBullet joint indices
   - Sets joint angles via `resetJointState`
   - **Manually enforces mimic joints** (PyBullet ignores URDF mimic tags):
     - `thumb_distal = thumb_proximal_pitch × 1.06`
     - `{index,middle,ring,pinky}_intermediate = proximal × 0.975`
   - Renders camera image with fixed overhead view
4. Writes frames to H.264 mp4 via OpenCV VideoWriter

### Why mimic joints must be set manually

PyBullet loads URDF mimic constraints but does not enforce them during `resetJointState` calls. Without manual enforcement, distal/intermediate joints stay at 0 (fully open) regardless of proximal angle, making fingers look broken.

### Camera setup

```python
cameraEyePosition    = [0.0, -0.45, 0.0]
cameraTargetPosition = [0.0,  0.0,  0.0]
cameraUpVector       = [0.0,  0.0,  1.0]
fov = 55, aspect = 800/600
```

---

## Step 3 — SeedAnce 2.0 API

**Input:** `scaffold.mp4` (reference video) + reference images of robot/scene
**Output:** Photorealistic robot POV video

### Asset upload

Assets must be uploaded to BytePlus asset store first. Use the BytePlus console or API to get `asset://asset-XXXXX` IDs.

### API call

```python
from seedance_2.0.pipeline import SeedancePipeline

pipeline = SeedancePipeline()
result = pipeline.submit_task(
    model_id="ep-20260406144100-86clt",
    prompt="First-person POV robot hand performing [task]. Follow the motion in the reference video exactly.",
    videos=["asset-XXXXX"],   # scaffold.mp4
    images=["asset-YYYYY"],   # reference image of robot hand
    config={"ratio": "16:9"}
)
task_id = result["id"]
final = pipeline.wait_for_completion(task_id)
print(final["content"]["video_url"])
```

### Key API details

- Base URL: `https://ark.ap-southeast.bytepluses.com/api/v3`
- Model: `ep-20260406144100-86clt`
- Asset references: `asset://asset-ID` or direct HTTPS URLs
- `role: "reference_video"` — motion reference (scaffold)
- `role: "reference_image"` — appearance reference

---

## Known Limitations

| Issue | Status |
|-------|--------|
| Hand wrist position not tracked | By design — dex-retargeting only outputs finger joints, not arm pose. Hands are stationary in scaffold. |
| Input video quality matters | Poor finger movement in input → limited joint angle range in output. Use video with deliberate pinch/spread/grasp gestures. |
| URDF paths are absolute | Must update `.yml` configs on each new machine. |
| mediapipe version pinned to 0.10.9 | Newer versions removed `solutions` API. |
