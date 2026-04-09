# CRISP Pipeline — Claude Code Context

## What This Project Is

We are showcasing **SeedAnce 2.0** (a video generation model by ByteDance) by demonstrating that its generated videos can serve as monocular input to the **CRISP Real2Sim pipeline**, producing physically valid simulation assets. The audience is a major robotics company. The output goal is a post-Isaac Gym simulation render showing a humanoid agent executing physically valid motion in a reconstructed scene — proving that synthetic video → sim-ready robotics training data is viable.

---

## CRISP Framework — What It Does

CRISP takes a monocular RGB video of a human and produces simulation-ready assets. It is **not** a visual reconstruction tool — it produces geometry that works in physics engines.

### 4-Stage Pipeline

```
Video → [Perception] → [Contact Hallucination] → [Planar Fitting] → [RL Physics Refinement]
```

**Stage 1 — Perception Front-end** (`scripts/1_video2imgs.sh` through `scripts/5_grav.sh`)
- `DPVO` — deep visual SLAM, tracks camera pose
- `MoGe-2` — metric-scale 3D geometry from frames (DINOv2 ViT-L backbone)
- `GVHMR` — recovers human body mesh (SMPL format) in world/gravity frame, not camera frame

**Stage 2 — Contact Hallucination** (`scripts/0_interactvlm.sh`, optional)
- `InteractVLM` predicts where the human body contacts the scene (feet on floor, pelvis on chair)
- Generates synthetic contact point cloud even for occluded surfaces
- Merged with visible point cloud before fitting
- **Note:** This step is optional and runs in a separate conda env (`setup_crisp_contact.sh`) due to dependency conflicts

**Stage 3 — Planar Fitting** (`scripts/7_glue_sqs.sh`)
- KMeans + DBSCAN clustering by normal orientation
- RANSAC plane fitting per cluster
- Outputs clean convex boxes (0.05m thick) instead of triangle meshes
- Exports as URDF

**Stage 4 — RL Physics Refinement** (`MotionTracking/`)
- Isaac Gym loads the URDF
- PPO trains humanoid agent to track reference motion
- ~15,000 FPS due to primitive geometry
- **Note:** Requires separate env (`setup_crisp_rl.sh`)

### Full Pipeline Execution

```bash
# Without contact hallucination (standard):
bash run_crisp_video.sh /path/to/data/YOUR_SEQUENCE

# With demo video:
bash run_crisp_video.sh --demo

# The wrapper calls scripts/all_gv.sh which runs stages 1-8 in sequence:
# 1_video2imgs → 2_get_mask → 3_megasam → 4_post_camera → 5_grav → 0_ufm → 6_align → 7_glue_sqs → 8_postprocessing
```

### Input Convention (CRITICAL)
Videos must live in a folder ending with `_videos`. Pass the **base name without the suffix**:
```
data/parkour_videos/jump.mp4   →   bash run_crisp_video.sh data/parkour
```
If you pass `data/parkour_videos` it will search for `data/parkour_videos_videos` and fail.

### Output Structure
```
results/output/scene/          # raw CRISP reconstruction
results/output/post_scene/     # z-up aligned version → used for RL bridge
  └── <SEQ>/gv/
      ├── hmr/human_motion.npz
      └── scene_mesh_sqs/scene_mesh_sqs.urdf
```

---

## Infrastructure

**Compute:** RunPod H100 PCIe 80GB (~$2.39/hr)
**Persistent storage:** Network volume mounted at `/workspace`
**Everything lives at:** `/workspace/CRISP-Real2Sim/`

All work should happen under `/workspace` — this survives pod restarts. Do not store important files outside `/workspace`.

---

## Environment Setup (Run Once on Pod)

### CUDA / Python Requirements
- CUDA: 12.4 (setup script installs this via conda)
- Python: 3.10 (setup script creates conda env)
- PyTorch: 2.4.1 + cu124 (from requirements-crisp-video.txt)

### Step 1 — Clone repo
```bash
cd /workspace
git clone --recursive https://github.com/Z1hanW/CRISP-Real2Sim.git
cd CRISP-Real2Sim
```

### Step 2 — Place body models
Body models must be uploaded from local Mac via SCP. They live in 3 locations:

```bash
# Location 1
inputs/checkpoints/body_models/smpl/SMPL_{NEUTRAL,MALE,FEMALE}.pkl
inputs/checkpoints/body_models/smplx/SMPLX_{NEUTRAL,MALE,FEMALE}.npz

# Location 2
prep/HMR/inputs/checkpoints/body_models/smpl/SMPL_{NEUTRAL,MALE,FEMALE}.pkl
prep/HMR/inputs/checkpoints/body_models/smplx/SMPLX_{NEUTRAL,MALE,FEMALE}.npz

# Location 3
prep/data/smpl/SMPL_NEUTRAL.pkl
prep/data/smplx/SMPLX_{NEUTRAL,MALE,FEMALE}.npz
```

SCP command from local Mac (after pod SSH is set up):
```bash
scp -P <PORT> -r ./CRISP-Real2Sim/inputs/ root@<POD-IP>:/workspace/CRISP-Real2Sim/inputs/
scp -P <PORT> -r ./CRISP-Real2Sim/prep/data/ root@<POD-IP>:/workspace/CRISP-Real2Sim/prep/data/
scp -P <PORT> -r ./CRISP-Real2Sim/prep/HMR/inputs/ root@<POD-IP>:/workspace/CRISP-Real2Sim/prep/HMR/inputs/
```

The local Mac already has these files prepared at `/Users/bytedance/Documents/trae_projects/CRISP-pipeline/CRISP-Real2Sim/`.

### Step 3 — Run environment setup + fetch assets
```bash
# This does everything in one command:
bash setups/setup_crisp_video_env.sh --with-assets
```

This runs `setup_crisp.sh` (conda env, CUDA 12.4, Python 3.10, all pip installs, CUDA extension builds) then `fetch_crisp_assets.sh` (downloads GVHMR, SAM2, MogeSAM checkpoints, co-tracker, DINOv2).

**If you run them separately:**
```bash
bash setups/setup_crisp.sh        # ~20-30 min, compiles CUDA extensions
conda activate crisp
bash setups/fetch_crisp_assets.sh # downloads ~3-4GB of checkpoints
```

### Step 4 — Validate environment
```bash
bash setups/validate_crisp_video_env.sh
```

---

## What `fetch_crisp_assets.sh` Downloads

| Asset | Destination | Source |
|---|---|---|
| SAM2 (AutoMask) | `prep/AutoMask/checkpoints/` | Auto via download_ckpts.sh |
| TapIP3D | `prep/MogeSAM/checkpoints/` | Hugging Face |
| Depth-Anything ViT-L | `prep/MogeSAM/third_party/...` | Hugging Face |
| RAFT-things | `prep/MogeSAM/third_party/...` | Google Drive |
| GVHMR weights | `prep/HMR/inputs/checkpoints/gvhmr/` | Google Drive |
| SMPL neutral | `prep/HMR/inputs/checkpoints/body_models/smpl/` | Google Drive |
| Co-tracker | `~/.cache/torch/hub/` | GitHub clone |
| DINOv2 | `~/.cache/torch/hub/` | GitHub clone |
| Co-tracker checkpoint | `~/.cache/torch/hub/checkpoints/` | Hugging Face |

---

## Key Pitfalls

1. **CUDA_HOME** — The setup script sets `CUDA_HOME=$CONDA_PREFIX`. This must be set before compiling DPVO/HMR extensions. The setup script handles this automatically if run correctly.

2. **`conda activate` in scripts** — On some systems `conda activate` doesn't work inside bash scripts. The setup uses `eval "$(conda shell.bash hook)"` first. If you hit activation issues, run this manually before activating.

3. **Input path suffix** — Always pass the base name without `_videos` to `run_crisp_video.sh`. This is the most common user error.

4. **`scene` vs `post_scene`** — The RL bridge (`MotionTracking`) only works with `post_scene` output, not `scene`. Always use the post-processed version.

5. **Contact hallucination is optional and unstable** — The authors note it "may not produce reasonable results for every video." Skip it for first runs. Run without it first, validate the output, then try adding contact hallucination.

6. **RL training needs a separate env** — `MotionTracking` (Isaac Gym) uses `setup_crisp_rl.sh`, not the main `crisp` conda env. Do not mix them.

7. **MoGe-2 model** — Loaded from Hugging Face (`Ruicheng/moge-2-vitl-normal`). Requires internet on first run. Will be cached at `~/.cache/huggingface/` after that — make sure this cache is on `/workspace` or it will be lost on pod restart.

---

## Input Video Requirements (for SeedAnce Videos)

For CRISP to work well, input videos need:
- Full human body in frame at all times (GVHMR fails if person exits frame)
- No motion blur (breaks MoGe-2 depth estimation)
- Stable camera — no shake/jitter (DPVO SLAM needs stable feature tracking)
- No fisheye/lens distortion (DPVO assumes pinhole camera model)
- Visible foot-ground contact (needed for contact hallucination)
- Textured surfaces in scene (SLAM needs visual features)

**SeedAnce 2.0 prompt used:**
> A person wearing bright green full-body tights bounds energetically up a concrete staircase on a city street. The person is the only green object in the scene. A smooth, stabilized tracking camera follows from approximately three meters behind at slight elevation, maintaining a consistent third-person perspective. The person's entire body — including feet — remains fully within frame throughout. Camera movement is fluid with zero shake or jitter, like a cinematic dolly shot. Natural daylight illumination with soft, even shadows. The concrete steps and surrounding pavement have clearly visible surface texture and material detail. Foot-to-step contact is physically accurate and clearly visible — no sliding, no floating, feet fully planted on each step. Sharp focus throughout, no motion blur, no fisheye or lens distortion, natural rectilinear perspective.

---

## Demo Video (Quickest Test)

Before running on SeedAnce videos, validate the full pipeline works with the built-in demo:

```bash
# First download demo data
cd /workspace/CRISP-Real2Sim
mkdir -p data
gdown --folder "https://drive.google.com/drive/folders/1xj28zTlCyCtOAZCw_JQxn6pyi5KmPt83" -O data

# Then run demo
bash run_crisp_video.sh --demo
```

This uses `data/demo_videos/wall-kicking.mp4`. If this works end-to-end, the environment is correctly set up.

---

## Repository Structure (Key Paths)

```
CRISP-Real2Sim/
├── run_crisp_video.sh          # main entry point
├── scripts/                    # pipeline stages 1-8
│   ├── all_gv.sh               # runs stages 1-8 in sequence
│   ├── 1_video2imgs.sh
│   ├── 2_get_mask.sh           # SAM2 masking
│   ├── 3_megasam.sh            # MoGe + SLAM reconstruction
│   ├── 4_post_camera.sh
│   ├── 5_grav.sh               # GVHMR human pose
│   ├── 0_ufm.sh                # UFM feature matching
│   ├── 6_align.sh              # human-scene alignment
│   ├── 7_glue_sqs.sh           # planar fitting → URDF
│   └── 8_postprocessing.sh     # z-up alignment for RL bridge
├── setups/
│   ├── setup_crisp.sh          # main env setup
│   ├── setup_crisp_video_env.sh # setup + optional asset fetch
│   ├── fetch_crisp_assets.sh   # checkpoint downloads
│   ├── validate_crisp_video_env.sh
│   ├── setup_crisp_contact.sh  # separate env for contact hallucination
│   └── setup_crisp_rl.sh       # separate env for Isaac Gym RL
├── prep/
│   ├── HMR/                    # GVHMR + DPVO
│   ├── MogeSAM/                # MoGe-2 + SAM2 + SLAM
│   ├── Contact-Predictor/      # InteractVLM
│   ├── AutoMask/               # SAM2 masking
│   └── data/                   # body models live here
│       ├── smpl/
│       └── smplx/
├── inputs/checkpoints/         # additional checkpoint location
│   └── body_models/
├── data/                       # input videos go here
│   └── YOUR_videos/            # folder must end in _videos
│       └── sequence.mp4
├── results/                    # outputs
│   └── output/
│       ├── scene/
│       └── post_scene/         # use this for RL
└── MotionTracking/             # Isaac Gym RL (separate env)
```

---

## Current Status (as of project start on pod)

- [ ] Pod deployed (H100 PCIe 80GB on RunPod)
- [ ] Repo cloned to `/workspace`
- [ ] Body models transferred via SCP (files ready on local Mac)
- [ ] `setup_crisp_video_env.sh --with-assets` completed
- [ ] Environment validated
- [ ] Demo video test passed
- [ ] SeedAnce video processed
