# Classical Visual-Inertial Odometry (S-MSCKF)

This phase implements the Multi-State Constraint Kalman Filter (MSCKF), a classical filter-based approach for Visual-Inertial Odometry, as described in the S-MSCKF paper. The algorithm fuses 6-DoF IMU measurements with sparse visual features to estimate the camera trajectory and the environment’s 3D structure.

## 📦 Dependencies

The following packages are required:

- Python 3.8+
- NumPy
- SciPy
- OpenCV (`cv2`)
- Matplotlib
- PyQuaternion

Install them with:

```bash
pip install numpy scipy opencv-python matplotlib pyquaternion
```
🚀 Running the Code

The main entry point is vio.py, which can be run without any arguments. Make sure you have the EuRoC dataset (MH_01_easy) downloaded and the correct path set in config.py.

python vio.py
Copy
If you want to use the working version (recommended), run:

python msckf_works.py
Copy
The script will process the dataset, estimate the trajectory, and optionally display the visualization.

📊 Expected Output

The output will include trajectory visualization (saved as imgs/euroc_mh_01_easy.png) and the estimated trajectory compared against the Vicon ground truth.

RMSE ATE: 5.138 meters on EuRoC MH_01_easy sequence.
Visualization GIF: Available in the main repository under assets/videos/Output_Classical_VIO.gif.

---
📁 Key Files

File	Description
vio.py	Main wrapper that orchestrates the VIO pipeline.
msckf.py	Original starter code (implementation of MSCKF).
msckf_works.py	Working implementation with all required functions.
config.py	Configuration parameters for dataset path and filter settings.
dataset.py	Data loading and synchronization for EuRoC dataset.
feature.py	Feature detection and matching utilities.
plot.py	Trajectory plotting and error computation.

--- 
🔗 References

S-MSCKF: Stereo Multi-State Constraint Kalman Filter
MSCKF: A Multi-State Constraint Kalman Filter for Vision-aided Inertial Navigation
