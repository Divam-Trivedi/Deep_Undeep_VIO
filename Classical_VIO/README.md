# Classical Visual-Inertial Odometry

A Python implementation of a **Stereo Multi-State Constraint Kalman Filter (S-MSCKF)** for Visual-Inertial Odometry (VIO).

This implementation combines synchronized **stereo camera measurements** with **IMU measurements** to estimate the motion of a camera/IMU system. The filter maintains a sliding window of camera states and uses geometric constraints from tracked visual features to correct the inertial state estimate.

The system is evaluated on the **EuRoC MAV MH_01_easy** sequence.

---

## 🔬 Overview

Visual-Inertial Odometry combines the complementary properties of cameras and inertial sensors:

* 📷 **Stereo cameras** provide geometric constraints through tracked image features.
* 📡 **IMU** provides high-frequency measurements of angular velocity and linear acceleration.
* 🔄 **MSCKF** fuses both modalities in an error-state Kalman filtering framework.

The overall estimation pipeline can be summarized as:

```text
                    EuRoC Dataset
                         │
             ┌───────────┴───────────┐
             │                       │
        Stereo Images               IMU
             │                       │
      Feature Detection          IMU Propagation
             │                       │
      Feature Tracking           State Prediction
             │                       │
             └───────────┬───────────┘
                         │
                  MSCKF Measurement
                       Update
                         │
                         ▼
                  Camera / IMU State
                         │
                         ▼
                    Trajectory
```

The MSCKF formulation uses multi-view feature observations to construct geometric constraints without requiring every feature to remain explicitly in the filter state. This is one of the key ideas behind the original MSCKF formulation.

---

# 📦 Dependencies

The implementation requires **Python 3.8+** and the following Python packages:

* NumPy
* SciPy
* OpenCV
* Matplotlib
* PyQuaternion

Install the dependencies with:

```bash
pip install numpy scipy opencv-python matplotlib pyquaternion
```

---

# 📁 Dataset

The implementation is designed for the **EuRoC MAV dataset**, specifically:

```text
MH_01_easy
```

EuRoC provides synchronized stereo images, IMU measurements, calibration parameters, and ground-truth trajectories.

Download the dataset from the official EuRoC MAV dataset source and make sure the `MH_01_easy` sequence is available locally.

A typical dataset layout is:

```text
MH_01_easy/
├── mav0/
│   ├── cam0/
│   │   ├── data/
│   │   └── data.csv
│   ├── cam1/
│   │   ├── data/
│   │   └── data.csv
│   ├── imu0/
│   │   └── data.csv
│   └── state_groundtruth_estimate0/
│       └── data.csv
```

The camera and IMU calibration parameters used by the filter are defined in:

```text
config.py
```

The current configuration includes stereo camera intrinsics/extrinsics and IMU-to-camera transformations corresponding to the EuRoC setup.

---

# ⚙️ Configuration

Before running the estimator, configure the dataset location in the appropriate configuration/loader code.

The main filter parameters are defined in:

```text
config.py
```

These include:

### Camera / Feature Tracking

* Feature grid configuration
* FAST feature detection threshold
* RANSAC threshold
* Stereo matching threshold
* Lucas-Kanade tracking parameters
* Image pyramid levels
* Feature tracking precision
* Keyframe thresholds

### IMU / Filter Parameters

* Gravity
* IMU frame rate
* Gyroscope noise
* Accelerometer noise
* Gyroscope bias noise
* Accelerometer bias noise
* Observation noise
* Initial state covariance

### MSCKF State Management

* Maximum number of camera states
* Camera state augmentation
* Keyframe selection
* Position uncertainty threshold
* Online filter reset conditions

Several of these parameters are explicitly exposed in `config.py`, including the 20-state camera window, stereo threshold, IMU noise parameters, and keyframe thresholds.

---

# 🚀 Running the VIO Pipeline

From the `Classical_VIO` directory:

```bash
cd Classical_VIO
```

The main entry point is:

```bash
python vio.py
```

The pipeline loads the EuRoC sequence, processes the stereo images and IMU measurements, performs feature tracking and filtering, and estimates the trajectory.

---

# 🧠 Algorithm Pipeline

The implementation follows the main stages of a filter-based visual-inertial estimator.

### 1. IMU Propagation

IMU measurements are used to propagate the current state forward in time.

The state includes quantities such as:

* Orientation
* Position
* Velocity
* IMU biases
* Camera/IMU calibration states

---

### 2. Feature Detection

Visual features are detected in the camera images and distributed across an image grid to encourage spatial coverage.

The configuration uses FAST-based feature detection together with configurable tracking and RANSAC thresholds.

---

### 3. Feature Tracking

Features are tracked between consecutive frames using pyramidal Lucas-Kanade optical flow.

Stereo observations provide additional geometric constraints between the left and right camera views.

---

### 4. State Augmentation

When a new camera frame is incorporated, the corresponding camera pose is added to the MSCKF state.

A sliding window limits the number of camera states retained by the filter.

---

### 5. Multi-View Geometric Constraints

Features observed across multiple camera poses provide constraints on the camera states.

The MSCKF formulation exploits these constraints without requiring the 3D feature positions to remain permanently in the filter state. This is a central characteristic of the original MSCKF approach.

---

### 6. Kalman Filter Update

The visual constraints are used to correct the inertial prediction.

The resulting estimate combines:

```text
IMU prediction
      +
Visual geometric constraints
      ↓
MSCKF correction
      ↓
Updated 6-DoF state
```

---

### 7. Trajectory Estimation

The estimated camera trajectory is compared against the EuRoC ground-truth trajectory for evaluation.

---

# 📊 Results

The implementation was evaluated on:

**EuRoC MAV — MH_01_easy**

### Quantitative Result

| Metric                         |               Result |
| ------------------------------ | -------------------: |
| RMSE Absolute Trajectory Error |          **5.138 m** |
| Dataset                        | **EuRoC MH_01_easy** |

### Trajectory Visualization

![EuRoC MH\_01\_easy trajectory](imgs/euroc_mh_01_easy.png)

The generated visualization compares the estimated trajectory with the available ground-truth trajectory.

A rendered visualization of the system is also available in the main repository:

➡️ [Classical VIO Output](../assets/videos/Output_Classical_VIO.gif)

---

# 📂 Project Structure

```text
Classical_VIO/
│
├── config.py
│   └── Dataset, camera, IMU, feature-tracking,
│       and filter configuration
│
├── dataset.py
│   └── EuRoC dataset loading and synchronization
│
├── feature.py
│   └── Feature detection and tracking
│
├── image.py
│   └── Image processing utilities
│
├── msckf.py
│   └── MSCKF implementation
│
├── msckf_works.py
│   └── Working/recommended MSCKF implementation
│
├── plot.py
│   └── Trajectory visualization and error evaluation
│
├── utils.py
│   └── Mathematical and utility functions
│
├── viewer.py
│   └── Visualization utilities
│
├── vio.py
│   └── Main VIO pipeline
│
└── imgs/
    └── EuRoC result visualization
```

---

# 📚 References

### MSCKF

A. I. Mourikis and S. I. Roumeliotis,
**"A Multi-State Constraint Kalman Filter for Vision-aided Inertial Navigation,"**
IEEE International Conference on Robotics and Automation (ICRA), 2007.

[Publication details and DOI](https://doi.org/10.1109/ROBOT.2007.364024)

### Stereo MSCKF

The stereo formulation builds upon the MSCKF framework for visual-inertial estimation. For additional background on S-MSCKF and its application to autonomous flight, see:

K. Sun et al.,
**"Robust Stereo Visual Inertial Odometry for Fast Autonomous Flight,"**
2017.

[Paper](https://arxiv.org/abs/1712.00036)

---

# 📄 Further Documentation

For a broader comparison between the classical and deep-learning approaches in this project, see the main repository:

➡️ **[Deep and Un-Deep VIO](../README.md)**

The complete technical discussion of the classical implementation is also available in:

➡️ **[Classical VIO Report](../reports/Classical_VIO.pdf)**

---

## License

This project is distributed under the **MIT License**.

See the repository [LICENSE](../LICENSE) for details.
