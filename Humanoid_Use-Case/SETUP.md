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
conda install -c conda-forge pybullet -y
```

## 3. Install Python dependencies

```bash
pip install mediapipe==0.10.9 opencv-python tqdm numpy requests
```

> mediapipe must be pinned to 0.10.9 — newer versions removed the `solutions` API.

## 4. Install dex-retargeting

```bash
cd ~/CRISP-pipeline/dex-retargeting
pip install -e ".[all]"
```

## 5. Update URDF paths

Edit these two files and set `urdf_path` to the absolute path on this machine:

- `Humanoid_Use-Case/robot_pov_pipeline/configs/gr1t2_right_hand.yml`
- `Humanoid_Use-Case/robot_pov_pipeline/configs/gr1t2_left_hand.yml`

```yaml
# Example — adjust to your clone location
urdf_path: /home/ubuntu/CRISP-pipeline/Wiki-GRx-URDF/Dexterous_hand/fourier_hand_6dof/urdf/fourier_right_hand_6dof.urdf
```

## 6. Run the pipeline

```bash
cd ~/CRISP-pipeline

# Step 1: retarget
conda run -n robot_pov python Humanoid_Use-Case/robot_pov_pipeline/retarget_video.py \
  --video /path/to/input.mp4 \
  --output_dir Humanoid_Use-Case/robot_pov_pipeline/output

# Step 2: render scaffold
conda run -n robot_pov python Humanoid_Use-Case/robot_pov_pipeline/render_scaffold.py \
  --right Humanoid_Use-Case/robot_pov_pipeline/output/right_joints.pkl \
  --left  Humanoid_Use-Case/robot_pov_pipeline/output/left_joints.pkl \
  --output Humanoid_Use-Case/robot_pov_pipeline/output/scaffold.mp4
```
