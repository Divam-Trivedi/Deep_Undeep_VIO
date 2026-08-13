# Deep and Un-Deep Visual-Inertial Odometry (VIO)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-Deep Learning-orange.svg)](https://pytorch.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This repository implements a comprehensive study of Visual-Inertial Odometry (VIO), exploring both the **Classical** approach (filter-based fusion) and the **Deep Learning** approach (neural-network-based pose estimation). The project demonstrates how complementary sensors—Cameras and Inertial Measurement Units (IMUs)—can be fused to achieve robust state estimation for aerial robots.

## 🚀 Project Overview

The project is divided into two distinct phases:

### Phase 1: Classical VIO (S-MSCKF)
Implementation of the Multi-State Constraint Kalman Filter (MSCKF). This phase focuses on the geometric relationship between image features and IMU pre-integration to estimate the trajectory of a quadrotor.
- **Dataset:** EuRoC MH_01_easy.
- **Core Approach:** Error-state Kalman Filtering with feature-based measurement updates.

### Phase 2: Deep VIO (LSTM Fusion)
An end-to-end deep learning approach to estimate relative poses. This phase explores the impact of modality (Vision only vs. IMU only vs. Fusion) on odometry accuracy.
- **Dataset:** Custom synthetic data generated via Blender.
- **Core Approach:** LSTM-based networks processing RGB frames and 6-DoF IMU sequences.

---

## 📊 Results Summary

### Phase 1: Classical VIO
| Metric | Value | Dataset |
| :--- | :--- | :--- |
| **RMSE ATE** | **5.138 m** | EuRoC MH_01_easy |

**Trajectory Visualization:**
![Classical VIO Output](Classical_VIO/imgs/euroc_mh_01_easy.png)

**Real-time Processing:**
![Classical VIO GIF](assets/videos/Output_Classical_VIO.gif)

---

### Phase 2: Deep VIO (Synthetic Evaluation)
Results for relative pose estimation on testing trajectories:

| Trajectory | Method | RMSE ATE | Median ATE | Scale Drift |
| :--- | :--- | :--- | :--- | :--- |
| **Infinity** | Vision-Only | 17.92 m | 10.23 m | 0.125 |
| | IMU-Only | 8.91 m | 8.61 m | 0.113 |
| | **Visual-Inertial** | **12.17 m** | **7.86 m** | **0.150** |
| **Random** | Vision-Only | 31.50 m | 21.51 m | 0.231 |
| | IMU-Only | 9.50 m | 7.22 m | 0.240 |
| | **Visual-Inertial** | **20.81 m** | **12.60 m** | **0.235** |
| **Spiral** | Vision-Only | 15.98 m | 10.67 m | 0.154 |
| | IMU-Only | 7.91 m | 7.73 m | 0.217 |
| | **Visual-Inertial** | **10.98 m** | **8.41 m** | **0.193** |

**Training Performance:**
![Training Curve](assets/images/training_curves/training_curve.png)

---

## 📁 Repository Structure

```text
.
├── Classical_VIO/      # Phase 1: MSCKF Implementation
├── Deep_VIO/           # Phase 2: LSTM-based VIO & Data Gen
├── assets/             # All visual results (Images, GIFs, Videos)
├── reports/            # Final Technical Reports (PDFs)
└── LICENSE             # MIT License
```

🛠️ Getting Started

Classical VIO

For detailed setup and execution of the MSCKF implementation, please refer to the Classical VIO README.

Deep VIO

For information on the LSTM architectures and Blender data generation, please refer to the Deep VIO README.

--- 

📄 Documentation & Presentation

Technical Reports:
Phase 1 Report (PDF)
Phase 2 Report (PDF)
Presentation Video: Watch Video Presentation
Model Architectures:
Vision Network
IMU Network

---
⚖️ License

Distributed under the MIT License. See LICENSE for more information.
