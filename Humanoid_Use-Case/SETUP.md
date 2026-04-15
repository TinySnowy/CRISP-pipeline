# Setup — Ubuntu 24.04

## 1. Install Miniconda

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b
~/miniconda3/bin/conda init bash
source ~/.bashrc
```

## 2. Create environment

```bash
conda create -n robot_pov python=3.9 -y
conda activate robot_pov
```

## 3. Install dex-retargeting with all dependencies (includes SAPIEN)

```bash
cd ~/CRISP-pipeline/dex-retargeting
pip install -e ".[example]"
```

## 4. Install remaining dependencies

```bash
pip install mediapipe==0.10.9 opencv-python tqdm numpy requests
```

> mediapipe must be pinned to 0.10.9 — newer versions removed the `solutions` API.

## 5. Download robot assets

```bash
cd ~/CRISP-pipeline/dex-retargeting
python -m dex_retargeting.download_assets
```

## 6. Run the pipeline

```bash
cd ~/CRISP-pipeline

# Step 1: retarget human video → inspire hand joint angles
conda run -n robot_pov python Humanoid_Use-Case/robot_pov_pipeline/retarget_video.py \
  --video Human_POV_videos/test1.mp4 \
  --output_dir Humanoid_Use-Case/robot_pov_pipeline/output

# Step 2: render scaffold video (SAPIEN, headless)
conda run -n robot_pov python Humanoid_Use-Case/robot_pov_pipeline/render_scaffold.py \
  --pkl    Humanoid_Use-Case/robot_pov_pipeline/output/right_joints.pkl \
  --output Humanoid_Use-Case/robot_pov_pipeline/output/scaffold.mp4
```
