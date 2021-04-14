import numpy as np
from numpy.random import normal
from matplotlib import pyplot as plt
from scipy.spatial.transform import Rotation as R
x = np.stack([normal(0, 1, 200), normal(0, 0.1, 200)])
x2 = np.array([[-10, 10], [0, 0]])
rot = R.from_euler('z', [0.6]).as_matrix().squeeze()[:2, :2]
x = rot@x + np.array([[1], [2]])
x2 = rot@x2 + np.array([[1], [2]])
plt.plot([-100, 100], [0, 0], c='k', linewidth=0.5)
plt.plot([0, 0], [-100, 100], c='k', linewidth=0.5)
plt.scatter(*x, s=10)
plt.plot(*x2, c='orange', linewidth=2)
plt.xlim([-1, 3])
plt.ylim([-1, 4])
