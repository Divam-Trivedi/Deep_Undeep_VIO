# Deep Visual-Inertial Odometry (LSTM Fusion)

This phase implements a deep learning-based Visual-Inertial Odometry (VIO) system using PyTorch. Three model variants are trained and evaluated:

1. **Vision-Only**: LSTM processes visual features extracted from two consecutive RGB frames.
2. **Inertial-Only**: LSTM processes a sequence of 6-DoF IMU measurements.
3. **Visual-Inertial Fusion**: Both modalities are processed by separate LSTMs and concatenated to predict relative pose.

All models estimate relative pose between two camera frames, which is then used for dead‑reckoning to obtain full 3D trajectories.

## 📁 Project Structure
Copy
Deep_VIO/
├── data_gen.blend # Blender scene for synthetic data generation
├── data_gen.py # Python script to export images, IMU, and ground truth poses
├── vio.py # Model definitions, training, and evaluation code
├── evaluation_results.csv # Metrics for all testing trajectories
└── README.md


## 🧠 Model Architectures

- [Vision Network (PNG)](../assets/images/model_architectures/VisionNet.png)
- [IMU Network (PNG)](../assets/images/model_architectures/IMUNet.png)

## 📦 Dependencies

Install the required Python packages:

```bash
pip install torch torchvision numpy pandas matplotlib scipy opencv-python
```
Additionally, you need Blender (version 3.0 or later) if you want to generate new synthetic data.

🗂️ Data Generation

The synthetic dataset is created using Blender. The camera follows trajectories over a textured plane while IMU measurements are simulated.

To generate new data:

Open data_gen.blend in Blender.
Adjust trajectory parameters if needed (see the Blender text editor).
Run the script via the Blender Python console or by executing the external script:
blender data_gen.blend --background --python data_gen.py
Copy
This will output:

RGB images (10% sample rate relative to IMU)
IMU measurements (accelerometer and gyroscope) at 1000 Hz
Ground truth 6‑DoF poses
The generated data is stored in a folder named synthetic_data/ (or as defined in the script).

🏋️ Training

The vio.py script supports training for all three variants. You can set the model type via command‑line arguments.

Example:

python vio.py --model fusion --epochs 100 --batch_size 32 --data_path ./synthetic_data/
Copy
Supported model types: vision, imu, fusion.

Training will output:

Model checkpoints in checkpoints/
Training curves in training_curves/
📈 Evaluation

After training, evaluate on unseen test trajectories:

python vio.py --model fusion --evaluate --checkpoint checkpoints/fusion_best.pth --test_data ./test_data/
Copy
The script will compute metrics (RMSE ATE, Median ATE, RMSE RPE, Scale Drift) and generate trajectory plots saved to results/.

📊 Results Summary

Trajectory	Method	RMSE ATE (m)	Median ATE (m)	Scale Drift
Infinity	Vision-Only	17.926	10.229	0.125
IMU-Only	8.910	8.606	0.114
Fusion	12.170	7.857	0.150
Random	Vision-Only	31.499	21.509	0.232
IMU-Only	9.504	7.222	0.240
Fusion	20.807	12.600	0.235
Spiral	Vision-Only	15.983	10.675	0.155
IMU-Only	7.909	7.730	0.217
Fusion	10.980	8.414	0.193
Training curve:



🔗 References

Deep Drone Acrobatics
PRGFlow
OysterSim

---

Both README files are ready to be placed in the respective directories. Let me know if you want any adjustments or if you'd like me to also generate the `.gitignore` and `LICENSE` files.
Copy
