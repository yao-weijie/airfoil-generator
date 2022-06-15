import matplotlib.pyplot as plt
import time
import numpy as np

fig, ax = plt.subplots()
fig.show()
for i in range(10):
    x = np.random.rand(10)
    ax.plot(x)

    time.sleep(1)
