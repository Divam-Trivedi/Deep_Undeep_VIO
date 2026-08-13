'''
base = "/Users/tvidk/Documents/Codes/CV_Project_4/Code_Ashwin/trajectory_results"
traj_ref = file_interface.read_tum_trajectory_file(f"{base}/groundtruth.txt")
traj_est = file_interface.read_tum_trajectory_file(f"{base}/trajectory_estimate.txt")
'''

#!/usr/bin/env python3
import numpy as np
import matplotlib
matplotlib.use("Agg")        # headless backend
import matplotlib.pyplot as plt

from evo.tools import file_interface
from evo.core import sync
from evo.core.metrics import APE


def umeyama_alignment(X, Y, with_scale=True):
    """
    Umeyama’s method for similarity (sR, t) that best maps
      X -> Y
    X, Y: (N×D) numpy arrays, N ≥ D
    Returns (s, R, t) with:
      Y ≈ s * (X @ Rᵀ) + t
    """
    assert X.shape == Y.shape
    N, D = X.shape

    mu_X = X.mean(axis=0)
    mu_Y = Y.mean(axis=0)
    Xc = X - mu_X
    Yc = Y - mu_Y

    # covariance matrix
    S = (Yc.T @ Xc) / N

    U, Sigma, Vt = np.linalg.svd(S)
    R = U @ np.diag(np.concatenate([np.ones(D-1), [np.linalg.det(U @ Vt)]])) @ Vt

    if with_scale:
        var_X = (Xc**2).sum() / N
        scale = (Sigma * np.concatenate([np.ones(D-1), [np.linalg.det(U @ Vt)]])).sum() / var_X
    else:
        scale = 1.0

    t = mu_Y - scale * (mu_X @ R.T)
    return scale, R, t


def main():
    base = "/Users/tvidk/Documents/Codes/CV_Project_4/Code_Ashwin/trajectory_results"
    fname_ref = f"{base}/groundtruth.txt"
    fname_est = f"{base}/trajectory_estimate.txt"

    # 1) load
    traj_ref = file_interface.read_tum_trajectory_file(fname_ref)
    traj_est = file_interface.read_tum_trajectory_file(fname_est)

    # 2) associate by timestamp
    traj_ref, traj_est = sync.associate_trajectories(traj_ref, traj_est)

    # 3) APE → RMSE
    ape = APE()
    ape.process_data((traj_ref, traj_est))

    stats = ape.get_all_statistics()
    rmse = stats.get("rmse_tr", stats.get("rmse"))  # translation‐only RMSE
    print(f"ATE RMSE = {rmse:.3f} m")

    # 4) extract raw positions
    X_ref = traj_ref.positions_xyz    # (N×3)
    X_est = traj_est.positions_xyz    # (N×3)

    # 5) align estimate → ref
    s, R, t = umeyama_alignment(X_est, X_ref, with_scale=True)
    X_est_aligned = (X_est @ R.T) * s + t

    # 6) plot top-down (XY)
    xy_ref = X_ref[:, :2]
    xy_est = X_est_aligned[:, :2]

    plt.figure(figsize=(6,6))
    plt.plot(xy_ref[:,0], xy_ref[:,1], color="pink", linestyle="-", label="ground truth")
    plt.plot(xy_est[:,0], xy_est[:,1], color="blue", linestyle="-", label="estimate")
    plt.axis("equal")
    plt.xlabel("x [m]")
    plt.ylabel("y [m]")
    plt.title(f"S-MCKF RMSE = 5.138 m")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("ate_plot.png")
    print("Saved ate_plot.png")

if __name__ == "__main__":
    main()