Physical-Kinematic Synthesis for Embodied AI: Integrating SeedAnce 2.0 with Robot Mechanical Constraints for High-Fidelity POV Video Conversion
The synthesis of robotic point-of-view (POV) video from human demonstrations represents a critical frontier in the development of general-purpose embodied artificial intelligence. For robotic agents to learn effectively from human data, the "embodiment gap"—the morphological and kinematic divergence between a human demonstrator and a robotic platform—must be bridged. This research explores the technical feasibility of utilizing ByteDance’s SeedAnce 2.0, a multimodal video generation model, as a "neural simulator" to re-render first-person human videos into physically accurate robot POV videos. This process necessitates the strict integration of mechanical constraints, such as joint degrees of freedom (DOF), rotational limits, and actuator torque profiles, all of which are formally defined in Unified Robot Description Format (URDF) files. By conditioning generative models on validated kinematic scaffolds, it becomes possible to produce high-fidelity synthetic data that respects the laws of physics and the specific mechanical realities of modern industrial and humanoid robots.   

Comparative Kinematics and Mechanical Constraints of Modern Robotic Embodiments
A fundamental requirement for generating physically accurate robot POV video is a comprehensive understanding of the target robot’s mechanical architecture. Industrial arms and humanoid platforms exhibit diverse joint configurations, ranging from the repetitive, high-range joints of collaborative robots to the anthropomorphic but rotationally constrained joints of humanoid bipedal systems.   

Collaborative Industrial Arms: Universal Robots UR5 and UR10
Universal Robots' UR series represents the standard for 6-axis collaborative manipulators (cobots). These systems are designed for high repeatability and safety in shared human-robot workspaces. The UR5 and UR10 utilize a series of rotational joints that offer a range of motion significantly different from the human arm. While the human shoulder is a complex ball-and-socket joint with limited rotational freedom in certain planes, the UR joints are essentially revolute actuators with wide angular ranges.   

Feature	UR5 Specification	UR10e Specification
Reach (Radius)	
850 mm / 33.5 in 

1300 mm / 51.2 in 

Degrees of Freedom	
6 rotating joints 

6 rotating joints 

Payload Capacity	
5 kg / 11 lbs 

10 kg or 12.5 kg 

Joint Ranges	
±360 
∘
  (All joints) 

±360 
∘
  (Excl. Elbow ±160 
∘
 ) 

Maximum Speed	
180 
∘
 /s (All joints) 

120 
∘
 /s (Base/Shoulder), 180 
∘
 /s (Others) 

Tool Speed	
Typical 1 m/s 

Typical 1 m/s 

Repeatability	
±0.1 mm 

±0.05 mm 

  
The UR5 architecture is characterized by its simplicity and the ability for joints to rotate beyond the mechanical limits of biological counterparts. This allows the robot to perform tasks such as continuous unscrewing or reaching behind its base without the need for complex re-grasping. However, this flexibility introduces the risk of kinematic singularities, particularly when the wrist joints align, which must be handled by the inverse kinematics (IK) solver before the motion is passed to a video generation model.   

Humanoid Robotics: Agile Mobility and Dexterous Manipulation
Humanoid robots like the Unitree H1, Figure 01, and Boston Dynamics' electric Atlas are designed to operate in human-centric environments, requiring a joint distribution that approximates human proportions but often exceeds human performance in specific dimensions.   

The Unitree H1 is a bipedal humanoid focusing on agility and affordability. Its upper body features a modular design where each arm typically possesses 4 degrees of freedom (DOF), including the body-shoulder joint, shoulder pitch, shoulder roll, and elbow joint. This is often expanded to 7 DOF in research configurations to allow for more complex manipulation.   

Unitree H1 Arm Joint	Movement Limit (Radians) 	Peak Torque (N.m) 
Shoulder Pitch	-2.87 to +2.87	~120
Shoulder Roll	-3.11 to +0.34 (R) / -0.34 to +3.11 (L)	~120
Shoulder Yaw	-4.45 to +1.3 (R) / -1.3 to +4.45 (L)	~120
Elbow Joint	-1.25 to +2.61	~120
  
In contrast, the Figure 01 robot prioritizes industrial-scale manipulation. It stands 5'6" tall and possesses 41 total degrees of freedom, with 7 DOF in each arm and 6 DOF in each hand. The Figure 01 uses custom electric actuators designed for high torque and efficiency, allowing it to handle a 20 kg payload. The hand design features four fingers and an opposable thumb with force control, enabling it to grasp objects ranging from small fasteners to large parts bins.   

Boston Dynamics' electric Atlas (unveiled in April 2024) represents the peak of humanoid mobility, with 56 degrees of freedom. Unlike the earlier hydraulic version, the electric Atlas uses fully rotational joints that can rotate 360 degrees at the hips, waist, and neck. This allows the robot to perform movements that are biologically impossible for humans, providing a unique challenge for retargeting: the robot can maintain its camera view while rotating its entire torso or limbs in ways a human demonstrator cannot.   

The Fourier GR-1, another prominent humanoid, utilizes 44 total joints, with 7 DOF per arm and an 11-DOF dexterous hand. It is powered by the Fourier Smart Actuator (FSA), which integrates the motor, driver, and reducer into a compact module capable of 230 N.m peak torque. The GR-1 is specifically designed for real-world assistance, requiring high-resolution displays and built-in emotional systems to interact naturally with humans.   

Reference Video Datasets for Embodied Perception and Training
To condition video generation models for robot POV, it is necessary to utilize datasets that provide a first-person perspective (often called "wrist-cam" or "eye-in-hand" views). These datasets provide the visual grounding for how end-effectors interact with objects and how the environment deforms or shifts from a robotic perspective.   

Large-Scale Embodiment and Wrist-Mounted Perspectives
The Open X-Embodiment dataset is a significant repository, aggregating over 1 million real-world robot trajectories across 22 different robot types. It includes diverse manipulation tasks such as pick and place, sorting, and assembly, providing a broad foundation for cross-embodiment learning.   

The DROID dataset (2024) is specifically tailored for diverse robotic manipulation with wrist-mounted cameras. It captures high-resolution visual data that aligns with the robot's action space, making it highly relevant for training generative simulators. By providing synchronous video and joint state data, DROID allows models to learn the causal relationship between a command (e.g., "close gripper") and the resulting visual change in the POV video.   

Universal Manipulation Interface (UMI) and Data Collection Innovation
The Universal Manipulation Interface (UMI) project offers a novel approach to data collection by using a handheld gripper mounted with a GoPro camera. This setup allows human demonstrators to record "in-the-wild" demonstrations that can be transferred directly to robot policies. The UMI framework captures precise robot actions even under fast human motion and includes a mechanism to automatically check if each demonstration is valid under the target robot's specific kinematic constraints.   

Dataset/Tool	Primary Perspective	Key Benefit for POV Generation
Open X-Embodiment	Multi-view / Third-person	
Diverse robot types and task variety 

DROID (2024)	Wrist-mounted	
High-quality first-person action data 

UMI	Handheld POV	
Low-cost, "in-the-wild" human demonstrations 

FastUMI	Handheld (RealSense)	
Robust tracking in occluded environments 

  
FastUMI improves upon the original UMI design by replacing SLAM-based tracking with a RealSense T265 module, which provides more stable 6-DOF pose tracking even when the camera is partially occluded—a common occurrence during complex manipulation tasks like assembly or hinged door operations. These datasets and interfaces provide the "source" video and "target" kinematic data necessary to train models like SeedAnce 2.0 to understand the transformation from human to robot POV.   

Technical Foundations of Motion Retargeting
Motion retargeting is the process of mapping a human demonstrator's hand and arm movements onto the robot’s kinematic chain while respecting mechanical limits. This is an essential preprocessing step; the video generation model cannot simply "hallucinate" movement but must be guided by a kinematically valid sequence of robot states.   

Inverse Kinematics and Skeleton Tree Reorientation
Standard techniques for retargeting rely on Inverse Kinematics (IK), which solves for joint angles q that place the robot's end-effector at a target pose P derived from the human demonstration. However, industrial arms and humanoid limbs have different link lengths and joint centers than humans, necessitating an optimization-based approach.   

AnyTeleop is a unified system that supports diverse robot arms and dexterous hands within a single framework. It uses a learning-free motion retargeting library that translates human motion to robot motion in real time, leveraging CUDA-based geometry queries to avoid self-collisions and environmental obstacles. The system is highly modular and can adapt to any robot arm-hand system given only its URDF file.   

Another sophisticated method involves "skeleton tree reorientation". This algorithm captures the operator’s complete upper limb posture (often in SMPL format) and maps it to the robot joint space. By matching the rotation centers of the human skeleton with the mechanical rotation centers of the robot, the algorithm ensures that the robot's motion reflects the actual intent of the human demonstrator while staying within its own rotational limits.   

Contact-Centric and Force-Aware Retargeting
For manipulation tasks, matching the pose of the end-effector is often insufficient. SoftAct is a contact force-guided framework that transfers human manipulation skills to robotic hands. In the first stage, it attributes contact forces observed in human fingers to robot fingers proportionally. In the second stage, it performs online retargeting by combining end-effector pose tracking with geodesic-weighted refinements based on contact geometry. This ensures that the robot's interaction with objects is functional and stable, even when there is a significant morphological mismatch between the human and robot hands.   

Traj2Action further simplifies this by using the 3D trajectory of the operational endpoint as a unified intermediate representation. A "Trajectory Expert" predicts a coarse future trajectory from human and robot data, which then conditions an "Action Expert" to output precise, robot-specific commands like gripper width and orientation. This coarse-to-fine decomposition allows the system to scale effectively across different embodiments.   

Video Generation with Physical and Kinematic Conditioning
The field of generative video modeling has recently transitioned from purely statistical pixel synthesis to "physics-aware" world modeling. Between 2023 and 2025, several researchers have proposed frameworks to condition video generation on robotic actions, URDF files, and joint sequences.   

Trajectory-Conditioned Synthesis: RoboMaster and TC-IDM
RoboMaster is a notable framework that synthesizes realistic robotic manipulation video from an initial frame, a text prompt, and a "collaborative trajectory". Unlike earlier models that treated the robot and the object as separate entities, RoboMaster models the interactive dynamics within a unified trajectory, decomposing the interaction into pre-, during, and post-interaction phases. This ensures that the generated video reflects the physical response of the object to the robot's manipulation.   

The Tool-Centric Inverse Dynamics Model (TC-IDM) establishes an intermediate representation based on the "tool's imagined trajectory". It extracts point cloud trajectories from generated videos via segmentation and 3D motion estimation. By focusing on the tool rather than the entire robot, TC-IDM achieves high viewpoint invariance and generalizes effectively across different end-effectors.   

Multi-Stage Pipelines: PhyRPR and PhysCtrl
A significant challenge in video generation is the entanglement of high-level physical reasoning with low-level visual synthesis. PhyRPR (PhyReason–PhyPlan–PhyRefine) is a three-stage pipeline designed to address this.   

PhyReason: Employs a large multimodal model to infer the underlying physical implications of a prompt and extract a sequence of physically grounded key states.   

PhyPlan: Deterministically synthesizes a controllable "coarse motion scaffold" that respects kinematic and mechanical constraints.   

PhyRefine: Injects this scaffold into the diffusion sampling process to refine appearance and ensure visual realism.   

Similarly, PhysCtrl is a framework for physics-grounded image-to-video generation that represents physical dynamics as 3D point trajectories over time. It allows for explicit control over physical parameters (like material stiffness or Young's Modulus) and external forces. Experiments demonstrate that PhysCtrl can generate realistic motion trajectories that drive video models to produce high-fidelity, controllable outputs that outperform traditional single-stage methods.   

Physics-Infused Latent Dynamics: Phantom
Phantom represents a "Physics-Infused Video Generation" model that jointly models visual content and latent physical dynamics. Built on a dual-branch flow-matching architecture, Phantom augments a visual generation pathway with a dedicated "physics branch". This branch enables the model to explicitly reason over latent physical processes—such as gravity and momentum—inferred from observed video. The two branches exchange information via cross-attention layers, ensuring that the generated future frames are both visually realistic and physically consistent with the laws of motion.   

SeedAnce 2.0: A Multimodal Architecture for Robot POV Conversion
ByteDance’s SeedAnce 2.0 (launched officially in February 2026) is a revolutionary multimodal video generation model that integrates text, images, video, and audio into a unified architecture. Its capabilities make it an ideal candidate for the task of robot POV conversion, particularly due to its "Director Mode" and "multimodal reference system".   

Technical Architecture and Capabilities
SeedAnce 2.0 is built on a Dual-Branch Diffusion Transformer architecture, which allows it to process up to 12 multimodal reference files simultaneously: 9 images, 3 videos, and 3 audio clips. This allows for a level of control previously unavailable in video generation models.   

Feature	SeedAnce 2.0 Specification
Resolution	
Up to 2K (1080p-2048p) 

Max Duration	
15 seconds per shot (extendable to 60s) 

Input Capacity	
9 Images, 3 Videos, 3 Audio Clips, Text 

Generation Speed	
2K video 30% faster than version 1.5 

Audio Generation	
Native, synchronized audio-video joint generation 

Control Mechanism	
@ Asset tagging for precision directing 

  
Unlike earlier models that added audio in post-production, SeedAnce 2.0 generates audio natively alongside video. For robot POV videos, this means the mechanical whirring of the motors, the "click" of the gripper closing, and the sound of objects hitting a surface are all generated in perfect synchronization with the visual action.   

Physics-Aware Training and Consistency
One of the core breakthroughs of SeedAnce 2.0 is its "physics-aware training," which prevents the glitchy or "hallucinated" movements common in earlier models. The model understands how objects interact under force, how fabrics drape, and how fluids flow. This is critical for robot POV, where the arm's movement must appear to have weight and momentum consistent with its mechanical specifications.   

SeedAnce 2.0 also excels at maintaining character and scene consistency. Using reference images (e.g., from a URDF rendering of a robot arm), the model ensures that the mechanical details—wires, joint housings, and surface textures—remain "locked" across frames even during intense motion sequences.   

Practical Recommendation: Pipeline for Robot POV Synthesis
Based on the research findings, a robust and feasible pipeline for converting first-person human demonstrations into physically accurate robot POV videos using SeedAnce 2.0 involves a multi-stage integration of kinematic modeling and multimodal synthesis.   

Step 1: Data Acquisition and State Estimation
The process begins with a first-person human demonstration, ideally captured using a system like UMI or FastUMI. This provides not only the video feed but also the 6-DOF trajectory of the human hand and the timing of grasping actions.   

If the source is a legacy human POV video without tracking data, computer vision algorithms such as WHAM (Whole-Body Human Action Model) are used to extract a human skeleton sequence in SMPL format. This sequence provides the ground truth for what the human intended to do in the scene.   

Step 2: Kinematic Mapping and URDF Conditioning
The extracted human motion must be retargeted to the specific robot's embodiment.

URDF Loading: The target robot's URDF file is loaded to define joint limits (θ 
min
​
 ,θ 
max
​
 ) and link lengths.   

Retargeting: A tool like AnyTeleop or a skeleton reorientation algorithm is used to solve the inverse kinematics. This transforms human hand coordinates into a sequence of robot joint angles that are mechanically feasible for the robot (e.g., a UR5 or Figure 01).   

Scaffold Rendering: A coarse "motion scaffold" video is rendered using a simulator like NVIDIA Isaac Sim. This video shows a low-fidelity version of the robot arm performing the task in the same workspace. This scaffold provides the "motion and camera work" reference for the generative model.   

Step 3: Multimodal Synthesis in SeedAnce 2.0
The final stage leverages SeedAnce 2.0's multimodal inputs to produce the high-fidelity robot POV video.   

@Image1-4: High-resolution renderings of the specific robot arm and end-effector (gripper) from different angles to ensure identity consistency.   

@Video1: The "motion scaffold" from Step 2. This guides the model's execution of the robot arm's trajectory and camera movement.   

@Video2: The original human POV video. This provides the environmental context—the objects on the table, the lighting of the room, and the textures of the background.   

Text Prompt: A detailed "Director" style prompt.

Example: "Cinematic first-person robot POV. The robot arm tagged @Image1 follows the trajectory in @Video1 to pick up the red block seen in @Video2. The camera is mounted on the robot's wrist, providing a wide-angle view. Focus on the metallic texture of the gripper and the realistic physics of the block as it is lifted. Ambient factory hum and mechanical servo sounds."    

Step 4: Iterative Refinement and Validation
The generated 15-second clip is evaluated for both visual fidelity and physical accuracy. Models like TC-IDM can be used as a "verifiable reward" mechanism: they extract the robot's movement from the generated video and compare it back to the original URDF plan. If the video depicts a movement that exceeds joint limits or appears physically impossible (e.g., the arm passing through itself), the prompt is refined or the retargeting scaffold is adjusted for a second pass.   

Implications for the Future of Neural Simulation
The shift from rigid, computationally expensive simulators to flexible, multimodal "neural simulators" like SeedAnce 2.0 represents a paradigm shift in robotics. While traditional physics engines like PhysX or MuJoCo provide high numerical accuracy, they often struggle with visual realism and the simulation of deformable objects like cloth or fluids. SeedAnce 2.0 and related research papers from 2023-2025 demonstrate that generative models can effectively "interpolate" the complex physics of the real world while adhering to the hard constraints of robotic kinematics.   

By converting human POV videos into robot POV videos, researchers can unlock the vast ocean of human activity data currently hosted on platforms like YouTube or TikTok for robot training. This creates a scalable pathway for "imitation learning at scale," where a robot can watch a human perform a task and immediately visualize itself performing the same task within its own mechanical limitations—a process essential for achieving human-level dexterity in robotic systems.   

The primary hurdle remains the "long-horizon" consistency and the accurate modeling of complex contact forces. However, the emergence of dual-branch architectures that separate visual and physical latents suggests that by 2026, generative video models will be as much a tool for engineers as they are for filmmakers, providing a "digital twin" that is both visually indistinguishable from reality and physically grounded in engineering truth.   


wavespeed.ai
Seedance 2.0 Image-to-Video | Cinematic AI Video from Images | WaveSpeedAI
Opens in a new window

unifuncs.com
Comprehensive Analysis of AI Video Generation Technologies: Seedance 2.0, NSFW Video Generators, and the Strategic Advantages of HackAIGC - UniFuncs
Opens in a new window

hacks022.vercel.app
Introduction to the NVIDIA Isaac Robotics Platform
Opens in a new window

arxiv.org
TOCALib: Optimal control library with interpolation for bimanual manipulation and obstacles avoidance - arXiv
Opens in a new window

sirayatech.com
Seedance 2.0 is Here: ByteDance Redefines AI Video Generation with Director-Level Control - Siraya Technologies
Opens in a new window

arxiv.org
PhyRPR: Training-Free Physics-Constrained Video Generation - arXiv
Opens in a new window

neurips.cc
NeurIPS Poster PhysCtrl: Generative Physics for Controllable and Physics-Grounded Video Generation
Opens in a new window

universal-robots.com
UR5 Technical specifications Item no. 110105 - Universal Robots
Opens in a new window

blog.robozaps.com
Figure 01 Review: Specs & Analysis - Robozaps Blog
Opens in a new window

briandcolwell.com
A Complete Review Of Boston Dynamics' Atlas Robot - Brian D. Colwell
Opens in a new window

universal-robots.com
Technical Specifications UR10e - Universal Robots
Opens in a new window

universal-robots.com
Technical specifications UR10 Item no. 110110 - Universal Robots
Opens in a new window

universal-robots.com
Joint Limits - Universal Robots
Opens in a new window

reddit.com
Is there an ideal number for DOF? (robot arm) - Reddit
Opens in a new window

bostondynamics.com
Boston Dynamics Unveils New Atlas Robot to Revolutionize Industry
Opens in a new window

support.unitree.com
H1 SDK Development Guide - 宇树文档中心
Opens in a new window

docs.quadruped.de
H1 Overview | Unitree H1 - QUADRUPED Robotics
Opens in a new window

unitree.com
Universal humanoid robot H1_Bipedal Robot_Humanoid Intelligent Robot Company | Unitree Robotics
Opens in a new window

therobotreport.com
Figure 01 humanoid takes first public steps - The Robot Report
Opens in a new window

qviro.com
Figure FIGURE 01 Specifications - QVIRO
Opens in a new window

bostondynamics.com
Atlas Humanoid Robot - Boston Dynamics
Opens in a new window

bostondynamics.com
EMBODIED MANUFACTURING INTELLIGENCE - Boston Dynamics
Opens in a new window

scribd.com
Fourier GR1 | PDF | Robotics | Mechanical Engineering - Scribd
Opens in a new window

humanoid.guide
GR-1 - Humanoid robot guide
Opens in a new window

fftai.com
Fourier_General Purpose_Humanoid Robot_Assistant
Opens in a new window

ca.rbtx.shop
Fourier GR1 | Humanoid Robot | 44 DOF - RBTX
Opens in a new window

humanoidrobothub.net
Fourier GR-1 - Humanoid Robot Hub
Opens in a new window

arxiv.org
Learning Video Generation for Robotic Manipulation with Collaborative Trajectory Control
Opens in a new window

umi-gripper.github.io
Universal Manipulation Interface: In-The-Wild Robot Teaching ...
Opens in a new window

openreview.net
From Human Hands to Robot Arms: Manipulation Skills Transfer via Trajectory Alignment | OpenReview
Opens in a new window

arxiv.org
AnyTeleop: A General Vision-Based Dexterous Robot Arm-Hand Teleoperation System - arXiv
Opens in a new window

ieeexplore.ieee.org
Vision-Language-Action Models for Robotics: A Review Towards Real-World Applications - IEEE Xplore
Opens in a new window

raw.githubusercontent.com
FastUMI: A Scalable and Hardware-Independent Universal Manipulation Interface with Dataset - GitHub
Opens in a new window

arxiv.org
FastUMI: A Scalable and Hardware-Independent Universal Manipulation Interface with Dataset - arXiv
Opens in a new window

semanticscholar.org
Human-Robot Motion Retargeting via Neural Latent Optimization | Semantic Scholar
Opens in a new window

drpress.org
A Method for Redirecting Humanoid Robots Based on Segmented Geometric Inverse Kinematics
Opens in a new window

arxiv.org
AnyTeleop: A General Vision-Based Dexterous Robot Arm-Hand Teleoperation System
Opens in a new window

arxiv.org
Functional Force-Aware Retargeting from Virtual Human Demos to Soft Robot Policies
Opens in a new window

raw.githubusercontent.com
Empowering World Models with Reflection for Embodied Video Prediction - GitHub
Opens in a new window

arxiv.org
Phantom: Physics-Infused Video Generation via Joint Modeling of Visual and Latent Physical Dynamics - arXiv
Opens in a new window

researchgate.net
(PDF) TC-IDM: Grounding Video Generation for Executable Zero-shot Robot Motion
Opens in a new window

arxiv.org
TC-IDM: Grounding Video Generation for Executable Zero-shot Robot Motion - arXiv
Opens in a new window

huggingface.co
Paper page - PhyRPR: Training-Free Physics-Constrained Video Generation
Opens in a new window

reddit.com
ByteDance releases Seedance 2.0 video model with Director mode and multimodal upgrades : r/singularity - Reddit
Opens in a new window

github.com
The Seedance 2.0 Prompt Library. Find the best prompts for cinematic AI videos. See real video examples and use text recipes that work. Create stable and professional movies every time. Do not guess. Just use our guides to master smooth motion and keep your characters consistent. · GitHub
Opens in a new window

dzine.ai
Seedance 2.0 Guide: Features, Usages & Alternatives | Dzine Blog
Opens in a new window

seaweed.video
seaweed.video
Opens in a new window

fal.ai
Seedance 2.0 API Live on fal (April 2026) | Video Generation API - Fal.ai
Opens in a new window

medium.com
How Seedance 2.0 works - Medium
Opens in a new window

replicate.com
Seedance 2.0 | Video Generation API - Replicate
Opens in a new window

higgsfield.ai
Seedance 2.0 — Multimodal AI Video Generation - Higgsfield
Opens in a new window

openreview.net
VideoPhy: Evaluating Physical Commonsense for Video Generation - OpenReview
Opens in a new window

openreview.net
SCALABLE REAL-WORLD ROBOT DATA GENERATION - OpenReview
Opens in a new window

vidnoz.com
Seaweed AI Video Generator: Features, Limitations & Best Alternative
Opens in a new window

studio.aifilms.ai
Hollywood Strikes Back: MPA Condemns ByteDance's Seedance... - AI FILMS Studio
Opens in a new window

lf3-static.bytednsdoc.com
Seed2.0 Model Card: Towards Intelligence Frontier for Real-World Complexity
Opens in a new window
Opens in a new window
Opens in a new window
Opens in a new window
Opens in a new window
Opens in a new window
Opens in a new window
Opens in a new window
Opens in a new window
Opens in a new window
Opens in a new window
Opens in a new window
Opens in a new window
Opens in a new window
Opens in a new window
Opens in a new window
Opens in a new window
Opens in a new window
Opens in a new window
Opens in a new window
Opens in a new window
Opens in a new window
Opens in a new window
Opens in a new window
Opens in a new window
