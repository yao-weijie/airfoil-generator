import numpy as np

x = np.array([0.0, 0.0, 1, 5, -7, 0])
nozero = x.nonzero()
mm = x[nozero].min()
print(mm)
