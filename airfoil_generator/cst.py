import numpy as np
from math import pi, cos, factorial
import matplotlib.pyplot as plt


class CST_shape(object):
    def __init__(self, wu=[1, 1, 1], wl=[-1, -1, -1], N1=0.5, N2=1.0, dz=0, N=200):
        self.set_params(wl, wu, N1, N2, dz, N)
        self.cal_coord()

    def set_params(self, wu=[1, 1, 1], wl=[-1, -1, -1], N1=0.5, N2=1.0, dz=0, N=200):
        self.wl = wl
        self.wu = wu
        self.N1 = N1
        self.N2 = N2
        self.dz = dz
        self.N = N

    def get_params(self):
        return self.wl, self.wu, self.N1, self.N2, self.dz, self.N

    def cal_coord(self):
        """function to calculate airfoil coordinate [x, y]"""
        wl, wu, N1, N2, dz, N = self.get_params()

        # Create x coordinate
        x = np.ones((N, 1))
        y = np.zeros((N, 1))
        zeta = np.zeros((N, 1))

        for i in range(0, N):
            zeta[i] = 2 * pi / N * i
            x[i] = 0.5 * (cos(zeta[i]) + 1)

        center_loc = np.where(
            x == np.min(x)
        )  # Used to separate upper and lower surfaces
        center_loc = center_loc[0][0]

        xl = np.zeros(center_loc)
        xu = np.zeros(N - center_loc)

        for i in range(len(xl)):
            xl[i] = x[i]  # Lower surface x-coordinates
        for i in range(len(xu)):
            xu[i] = x[i + center_loc]  # Upper surface x-coordinates

        yl = self.__ClassShape(
            wl, xl, N1, N2, -dz
        )  # Call ClassShape function to determine lower surface y-coordinates
        yu = self.__ClassShape(
            wu, xu, N1, N2, dz
        )  # Call ClassShape function to determine upper surface y-coordinates

        y = np.concatenate([yl, yu])  # Combine upper and lower y coordinates
        y = y.reshape(-1, 1)

        # 改成逆时针排列
        x = x[::-1]
        y = y[::-1]
        coord = np.concatenate([x, y], axis=1)
        self.coord = np.concatenate([coord, coord[0:1]], axis=0)

        return self.coord

    def __ClassShape(self, w, x, N1, N2, dz):
        """Function to calculate class and shape function"""

        # Class function; taking input of N1 and N2
        C = np.zeros(len(x))
        for i in range(len(x)):
            C[i] = x[i] ** N1 * ((1 - x[i]) ** N2)

        # Shape function; using Bernstein Polynomials
        n = len(w) - 1  # Order of Bernstein polynomials

        K = np.zeros(n + 1)
        for i in range(0, n + 1):
            K[i] = factorial(n) / (factorial(i) * (factorial((n) - (i))))

        S = np.zeros(len(x))
        for i in range(len(x)):
            S[i] = 0
            for j in range(0, n + 1):
                S[i] += w[j] * K[j] * x[i] ** (j) * ((1 - x[i]) ** (n - (j)))

        # Calculate y output
        y = np.zeros(len(x))
        for i in range(len(y)):
            y[i] = C[i] * S[i] + x[i] * dz

        return y

    def writeToFile(self, fname):
        """write [x, y] to file"""
        with open(fname, "w") as f:
            f.write(
                f"wu={self.wu}, wl={self.wl}, N1={self.N1}, N2={self.N2}, dz={self.dz}, N={self.N}\n"
            )
            np.savetxt(f, self.coord, fmt="%.4f", delimiter="\t")

    def plotting(self):
        x, y = self.coord[:, 0], self.coord[:, 1]
        fig, ax = plt.subplots()
        ax.plot(x, y, "r-", label="coords")
        ax.set_title("airfoil shape")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.grid(True)
        ax.set_xlim(xmin=-0.1, xmax=1.1)
        ax.set_ylim(ymin=-0.5, ymax=0.5)
        ax.set_aspect("equal")
        fig.tight_layout()
        plt.show()
        fig.savefig("Coord_predictN.png")


if __name__ == "__main__":
    wu = [0.5, 0.5, 0.5]  # Upper surface
    wl = [-0.2, 0.3, 0.2]  # Lower surface
    N1 = 0.5
    N2 = 0.5
    dz = 0
    N = 50
    #  s = input('input something:  ')
    #  print(s)

    airfoil_CST = CST_shape(wu, wl, N1, N2, dz, N)
    airfoil_CST.cal_coord()
    airfoil_CST.plotting()
    airfoil_CST.writeToFile("airfoil_coord.dat")
