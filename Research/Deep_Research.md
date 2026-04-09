# Engineering and Deployment Analysis of the CRISP Framework for Contact-Guided Real-to-Sim Synthesis

The transformation of monocular video into physically valid simulation environments represents a cornerstone challenge in the fields of computer vision, robotics, and embodied artificial intelligence. The CRISP framework—**Contact-guided Real2Sim from Monocular Video with Planar Scene Primitives**—addresses this gap by synthesizing human motion recovery, 4D scene reconstruction, and contact-based geometric completion into a unified pipeline. In contrast to previous methodologies that often relied on visually plausible but physically unstable dense triangle meshes, the CRISP architecture prioritizes the creation of "simulation-ready assets" through the use of compact planar primitives. This technical report examines the infrastructure requirements, architectural components, and execution protocols necessary to deploy the CRISP framework in a local GPU-accelerated environment.

---

## Infrastructure Prerequisites and GPU Compute Profiling

The deployment of the CRISP framework requires a robust computational environment capable of managing high-fidelity perception models and parallelized physics simulations. Given the complexity of the underlying modules—including vision-language models for contact prediction and transformer-based human pose regressors—hardware selection is a critical determinant of system throughput and training stability.

### Core Compute and CUDA Requirements

Local execution of the CRISP pipeline is optimized for NVIDIA GPU architectures, specifically those supporting CUDA 12.1 or 12.4. These versions provide the necessary primitives for the high-performance kernels used in the deep visual SLAM (DPVO) and the metric geometry estimation (MoGe) components. The framework is built upon the PyTorch ecosystem, requiring version 2.3.0 or higher to leverage recent advancements in distributed training and memory-efficient attention mechanisms.

| Component | Technical Specification | Functional Rationale |
|---|---|---|
| Operating System | Ubuntu 20.04 or 22.04 LTS | Standard for CUDA-based robotics frameworks |
| CUDA Toolkit | 12.1 / 12.4 | Support for specialized C++ extensions and kernels |
| PyTorch | 2.3.0+ (CUDA-enabled) | Back-end for perception and RL optimization |
| Python Environment | 3.10 (via Conda or Pixi) | Compatibility with transformer libraries |
| GCC / G++ | 9.0+ | Required for compiling third-party C++ bindings |
| Eigen Library | 3.4.0 | Prerequisite for DPVO visual odometry |

A significant infrastructure bottleneck identified in local deployments involves the `CUDA_HOME` environment variable. The framework relies on several custom CUDA extensions that must be compiled during the environment setup stage. If the `CUDA_HOME` path is not correctly exported to the system shell, the compilation of the DPVO and HMR modules will fail, preventing the initialization of the perception front-end.

### VRAM Utilization and GPU Memory Profiling

The CRISP pipeline is memory-intensive due to the concurrent execution of several large-scale foundation models. Effective profiling of VRAM requirements is essential for researchers operating on consumer-grade hardware. The framework is most stable on GPUs with 24 GB of VRAM, such as the RTX 3090 or RTX 4090, which provide sufficient headroom for the ViT-Large backbones used in depth and pose estimation.

| Pipeline Stage | VRAM Allocation (Estimated) | Memory Consumers |
|---|---|---|
| Perception Front-end | 14.5 GB | MoGe-2 (ViT-L), GVHMR, DPVO |
| Contact Hallucination | 9.0 GB | InteractVLM (Visual Question Answering) |
| Planar Fitting | 3.5 GB | Point cloud clustering and RANSAC logic |
| RL Training | 11.0 GB | Isaac Gym Parallel Humanoid Actors |
| **Aggregate Peak** | **~20.0 GB – 24.0 GB** | Concurrent Front-end and Simulation |

The transition from the perception front-end to the reinforcement learning training loop involves a hand-off of data that can be managed sequentially to reduce peak VRAM pressure. However, during the integrated "all-in-one" execution mode, the 24 GB threshold becomes a rigid requirement for maintaining high training throughput (FPS).

---

## Architectural Components: Perception and Reconstruction

The front-end of the CRISP framework is an intricate assembly of specialized modules designed to extract metric-accurate 3D information from 2D RGB streams. This process involves establishing a world-grounded coordinate system where the human and the scene can interact physically.

### Metric Geometry and Depth Estimation via MoGe-2

A central innovation in the CRISP pipeline is the integration of MoGe (Monocular Geometry Estimation), specifically the MoGe-2 iteration. MoGe-2 addresses the inherent scale ambiguity of monocular images by predicting metric-scale 3D point maps. This model utilizes a DINOv2 backbone, where the global semantics encoded in the CLS token are leveraged to estimate scene-type-aware priors for metric scale.

During the training of MoGe-2, a two-step preprocessing approach is employed to improve geometric accuracy on real-world data, involving the removal of incorrect depth estimates and the inpainting of missing values. For local deployment, the framework expects the pre-trained weights to be loaded from Hugging Face or a local cache, with the ViT-L variant (`Ruicheng/moge-2-vitl-normal`) being the preferred model for high-fidelity normal map estimation.

### World-Grounded Human Mesh Recovery (GVHMR)

Standard Human Mesh Recovery (HMR) techniques typically operate in a camera-centric coordinate system, which fails to capture global trajectory and scene-relative motion. CRISP incorporates GVHMR (Gravity-View Human Motion Recovery), a transformer-based model that predicts SMPL pose parameters `θ_t` and root motion `(r_t, π_t)` within a gravity-aligned world frame.

The human body is represented using the SMPL model, defined by:

```
M_t = M(θ_t, β, r_t, π_t) ∈ R^(6890×3)
```

In this formulation, `θ_t ∈ R^(23×3)` represents relative joint rotations, while `β ∈ R^10` encodes body shape identity. By lifting the camera-space reconstructions into the world frame using calibrated camera parameters `{K, T_i}`, the framework ensures that the human motion and scene geometry share a single metric coordinate system.

---

## Asset Acquisition and Data Architecture

The deployment of CRISP requires a meticulous approach to asset management, as the framework relies on several proprietary and research-licensed models. The directory structure must be precisely organized to allow the internal path-resolution logic to function.

### Downloading Foundational Models

Researchers must register for access to the SMPL and SMPL-X body models through the Max Planck Institute (TUE MPG) portal. These models are fundamental to the humanoid agent's physical properties and the metric scale recovery process.

| Model Name | Source / Provider | Registration Required |
|---|---|---|
| SMPL | smpl.is.tue.mpg.de | Yes |
| SMPL-X | smpl-x.is.tue.mpg.de | Yes |
| GVHMR Weights | Google Drive (Zju3dv) | No |
| MoGe-2 | Hugging Face (Ruicheng) | No |
| DPVO Weights | Google Drive (Zju3dv) | No |

### Required Directory Structure

The repository architecture is designed to locate checkpoints and body models within a central `inputs/` directory. Failure to adhere to this structure will result in initialization errors when running the `run_crisp_video.sh` wrapper.

```
CRISP-Real2Sim/
├── inputs/
│   ├── checkpoints/
│   │   ├── body_models/
│   │   │   ├── smpl/
│   │   │   │   └── SMPL_{GENDER}.pkl
│   │   │   └── smplx/
│   │   │       └── SMPLX_{GENDER}.npz
│   │   ├── dpvo/
│   │   │   └── dpvo.pth
│   │   ├── gvhmr/
│   │   │   └── gvhmr_siga24_release.ckpt
│   │   ├── yolo/
│   │   │   └── yolov8x.pt
│   │   └── vitpose/
│   │       └── vitpose-h-multi-coco.pth
│   └── data/
│       └── _videos/
│           └── sequence.mp4
```

A critical distinction in the data architecture is the separation of `scene` and `post_scene` results. The `scene` output contains the raw reconstruction data, while the `post_scene` directory contains the aligned, rotated z-up version required for the reinforcement learning bridge in the MotionTracking module.

---

## Geometry Synthesis: Contact-Guided Planar Fitting

The core technical advantage of the CRISP framework is its ability to produce "clean, convex, and simulation-ready geometry" by fitting planar primitives to the scene point cloud. This representation avoids the instability inherent in triangle meshes during physics simulation.

### Normal-Guided Clustering and Fitting

The geometry synthesis pipeline follows a structured mathematical approach to transform the point cloud `P` into a set of primitives:

1. **Normal Field Estimation** — A normal field `F` is estimated from the point set `P` using local neighborhood analysis.
2. **Clustering** — The system executes KMeans followed by DBSCAN to cluster points based on spatial proximity and normal orientation, effectively isolating distinct surfaces like floors, walls, and furniture.
3. **Axis Alignment** — For each identified cluster, the local z-axis is aligned with the scene normal `n`, while PCA (Principal Component Analysis) is used to determine the in-plane axes `(x, y)`.
4. **Expansion and Fitting** — RANSAC is applied to fit the geometric plane, which is then expanded along `(x, y)` to cover the inlier points. A fixed thickness of 0.05 m is applied to create a 3D collision box.

### Contact-Guided Completion

Occlusions are a primary failure mode in monocular scene reconstruction. CRISP addresses this by predicting body-scene contacts. These contact points serve as geometric anchors. For instance, if the HMR module predicts a sitting pose, the contact prediction identifies the interface between the pelvis and the (occluded) chair seat. A "contact point cloud" is then hallucinated at these coordinates and merged with the visible scene point cloud before planar fitting. This ensures that the simulated environment contains the necessary supporting surfaces for the human's observed interactions.

---

## Physics Simulation and Reinforcement Learning

The `MotionTracking/` module serves as the interface between the kinematic perception results and the dynamic physics-based simulator. This stage utilizes reinforcement learning to refine the human motion and enforce physical plausibility.

### Isaac Gym and URDF Integration

The planar primitives generated by the front-end are exported as a URDF (Unified Robot Description Format) file. This format is natively supported by Isaac Gym, allowing for high-performance collision detection and contact resolution. The use of primitives instead of meshes results in a **1.9x speedup** in simulation throughput, achieving approximately 15,000 FPS on standard hardware.

### Reward Function and Policy Optimization

The reinforcement learning agent is trained using Asynchronous Proximal Policy Optimization (PPO) to track the reference motion sequence while avoiding self-penetration and respecting environmental constraints. The reward function is formulated as:

```
r_t = w_gp * r_t^gp + w_gr * r_t^gr + w_rh * r_t^rh + w_jv * r_t^jv + w_jav * r_t^jav + w_cg * r_t^cg
```

The individual components encourage the imitation of:
- **gp** — global joint positions
- **gr** — global joint rotations
- **rh** — root height

Penalties are applied for excessive joint velocities (`jv`, `jav`) or violations of planar boundaries (`cg`). The policy observes the character's current state (joint orientations and velocities) and a look-ahead of `N` future target poses to predict the next set of actuator torques.

---

## Execution Flow and Operational Commands

For a successful local deployment, the researcher must follow a specific sequence of commands to navigate the perception, fitting, and training stages.

### Environment Initialization

```bash
# Clone the repository with all submodules
git clone --recursive https://github.com/Z1hanW/CRISP-Real2Sim.git
cd CRISP-Real2Sim

# Run the automated setup script
bash setups/setup_crisp.sh
conda activate crisp
```

### Perception and Reconstruction Pipeline

To process a custom video, ensure the video is placed in a folder with the `_videos` suffix. The script `run_crisp_video.sh` manages the visual SLAM, GVHMR, and planar fitting steps.

```bash
# Process a custom sequence (omit the _videos suffix in the command)
# Example sequence at: data/parkour_videos/jump.mp4
bash run_crisp_video.sh data/parkour
```

### Reinforcement Learning Loop

Once the `post_scene` assets are generated, the RL training can be initiated within the MotionTracking directory.

```bash
cd MotionTracking
# Refer to MotionTracking/README.md for specific sequence-based training commands
# Standard training initialization:
python train_agent.py --seq parkour --scene_urdf ../results/output/post_scene/parkour/scene.urdf
```

### Visualization and Rendering via Viser

Local visualization of the reconstructed assets is handled by the `viser` library, which provides an interactive web interface. Viser is particularly effective for debugging the alignment between the human mesh and the planar primitives.

```bash
# Compile the local viser visualizer
cd vis_scripts/viser_m
pip install -e .

# Launch the human-scene visualization
cd ../..
bash vis.sh ${SEQ_NAME}
```

The visualization can be customized with flags such as `--scene_name` to test different primitive configurations or `USE_CONTACT=on` to inspect the hallucinated contact point clouds. The default configuration launches a local server accessible via `localhost:8080`, allowing for real-time inspection of the 4D reconstruction.

---

## Deployment Bottlenecks and Mitigation Strategies

Analysis of the repository activity and user issues reveals several recurring bottlenecks that can impede the deployment of the CRISP framework.

### Dependency and Conflict Resolution

A primary issue arises from the intersection of PyTorch versions and C++ extension builds. Many users report errors when attempting to compile the DPVO module in environments where the CUDA toolkit version does not match the PyTorch CUDA runtime.

> **Mitigation:** Use a clean Conda environment for each major module if conflicts persist. Specifically, `setup_crisp.sh` should be executed in a shell where `nvcc --version` matches the CUDA version specified in the torch installation.

### Pathing and Suffix Errors

The framework uses a strict naming convention for input data. A common error involves passing the full directory name (including the `_videos` suffix) to the execution scripts.

> **Mitigation:** The wrapper scripts are designed to append the suffix internally. If the user provides `data/demo_videos` as the argument, the script may search for `data/demo_videos_videos`, resulting in a "file not found" error. Users should always provide the **base name** of the data folder.

### VRAM Overflows during RL Training

When training agents on complex scenes with many planar primitives, some users experience out-of-memory (OOM) errors on 8 GB or 12 GB GPUs.

> **Mitigation:** Reducing the number of parallel environments in the Isaac Gym configuration (typically found in the `cfg` files of the MotionTracking module) can significantly lower VRAM usage at the cost of longer training times.

---

## Synthesis and Conclusion

The CRISP framework represents a significant advancement in the Real2Sim pipeline, providing a robust methodology for converting unconstrained monocular videos into simulation-ready assets. By prioritizing planar primitives over dense meshes and leveraging contact prediction to resolve occlusions, CRISP achieves a success rate of over **97%** on standard benchmarks—a substantial improvement over prior state-of-the-art methods.

For the AI infrastructure researcher, successful local deployment hinges on the meticulous orchestration of CUDA-enabled environments, the accurate acquisition of licensed body models, and the strategic management of GPU VRAM across the perception and simulation stages. As monocular perception continues to evolve, the principles established by the CRISP framework—specifically the focus on physically stable geometric representations—will remain essential for the future of robotic imitation and humanoid control.

---

## References

- CRISP paper (ICLR 2026): [arXiv 2512.14696](https://arxiv.org/abs/2512.14696)
- CRISP GitHub repository: [Z1hanW/CRISP-Real2Sim](https://github.com/Z1hanW/CRISP-Real2Sim)
- CRISP on OpenReview: [openreview.net](https://openreview.net)
- MoGe-2 on OpenReview: [MoGe-2: Accurate Monocular Geometry with Metric Scale and Sharp Details](https://openreview.net)
- MoGe GitHub (CVPR'25 Oral): [microsoft/MoGe](https://github.com/microsoft/MoGe)
- SMPL body model: [smpl.is.tue.mpg.de](https://smpl.is.tue.mpg.de)
- SMPL-X body model: [vchoutas/smplx](https://github.com/vchoutas/smplx)
- GVHMR installation docs: [Zju3dv/GVHMR](https://github.com/zju3dv/GVHMR)
- Viser SMPL visualization: [viser.studio](https://viser.studio)
- PyTorch installation: [pytorch.org](https://pytorch.org)
