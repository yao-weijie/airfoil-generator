import math
import os
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import scipy.io as scio
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from PyQt5.QtCore import QCoreApplication, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QFileDialog, QGraphicsScene, QMainWindow

from cst import CST_shape
from mainWindow import Ui_MainWindow
from process.postprocess import coord2img
from process.preprocess import (
    gen_mesh,
    set_decomposefile,
    set_runfile,
    set_transfile,
    set_ufile,
)

matplotlib.use("Qt5Agg")

here = Path(".").absolute()


class QtFigure(FigureCanvasQTAgg):
    def __init__(self, graphics, parent=None):
        width = graphics.width()
        height = graphics.height()
        self.fig = plt.figure(figsize=(width / 100, height / 100), dpi=100)
        FigureCanvasQTAgg.__init__(self, self.fig)
        self.setParent(parent)

        self.graphics = graphics
        self.graphyScene = QGraphicsScene()
        self.graphicsProxy = self.graphyScene.addWidget(self)
        self.graphics.setScene(self.graphyScene)

        self.init_flag = True
        self.axes = self.fig.add_subplot(111)
        self.axes.spines["top"].set_visible(False)
        self.axes.spines["right"].set_visible(False)
        self.axes.spines["bottom"].set_visible(False)
        self.axes.spines["left"].set_visible(False)
        self.axes.set_xticks([])
        self.axes.set_yticks([])
        self.axes.set_aspect("equal")

    def update_plot(self, coord):
        x, y = coord[:, 0], coord[:, 1]
        if self.init_flag:
            self.axes.grid(True)
            self.axes.set_xlim(xmin=-0.05, xmax=1.05)
            self.axes.set_ylim(ymin=-0.55, ymax=0.55)
            (self.ax,) = self.axes.plot([], [], "b")
            self.fig.tight_layout()
            self.init_flag = False

        self.ax.set_data(x, y)
        self.fig.canvas.draw()

    def update_img(self, img, channel="magnitude"):
        cmap = "jet"
        #  if channel == 'vortex':
        #  cmap = 'coolwarm'

        nozero = img.nonzero()
        m = img[nozero].min()
        M = img[nozero].max()
        print(f"min: {m:.4f}, Max: {M:.4f} in channel: {channel}")

        self.axes.contourf(img, cmap=cmap, levels=30, vmin=m, vmax=M)
        #  self.axes.imshow(img)
        self.fig.tight_layout()
        self.init_flag = False
        self.fig.canvas.draw()


class Args(object):
    res = 128
    case_dir = Path("./caseSteadyState").absolute()


class SimThread(QThread):
    trigger = pyqtSignal(dict)

    def __init__(self, params):
        super(SimThread, self).__init__()
        self.signal_over = pyqtSignal(dict)
        self._params = params
        self.simulation_results = {}
        self.case_dir = Args.case_dir

    def set_params(self, params):
        self._params = params

    def run(self):
        params = self._params
        case_dir = Args.case_dir
        fsX = params["velocity"] * math.cos(params["angle"] / 180 * math.pi)
        fsY = params["velocity"] * math.sin(params["angle"] / 180 * math.pi)
        nu = params["nu"]
        rho = params["rho"]
        set_transfile(case_dir, rho, nu)
        set_decomposefile(case_dir, subdomains=10)
        set_ufile(case_dir, fsX, fsY)
        set_runfile(case_dir, subdomains=10, parallel_enable=True)
        # set_runfile(case_dir, args.subdomains, args.parallel_enable)

        # generate mesh
        os.chdir(case_dir)
        try:
            gen_mesh(params["coord"])
        except:
            print("\tmesh generation failed!")
            os.chdir(str(here))

        # 运行仿真
        os.chdir(case_dir)
        os.system("sh ./Allclean > foam.log")
        os.system("sh ./Allrun >> foam.log")
        os.chdir(str(here))

        data_img = coord2img(fsX, fsY, Args)

        data_img = {k: np.rot90(v) for k, v in data_img.items()}
        simulation_results = {
            "magnitude": np.sqrt(data_img["Ux_img"] ** 2 + data_img["Uy_img"] ** 2),
            "vortex": np.zeros((128, 128)),
            "Ux": data_img["Ux_img"],
            "Uy": data_img["Uy_img"],
        }

        self.trigger.emit(simulation_results)


class MainApp(Ui_MainWindow, QMainWindow):
    def __init__(self, mainWindow):
        super(MainApp, self).__init__()
        self.setupUi(mainWindow)
        self.simulation_results = {}
        self.channel = "magnitude"
        self.cst = CST_shape(wu=[0.5, 0.5, 0.5], wl=[-0.5, -0.5, -0.5], N1=0.5, N2=1)
        self.sim_thread = SimThread(self.get_sim_params())
        self.sim_signal = pyqtSignal(dict)
        self.bind_actions()
        self.init_params()
        self.init_figs()

    def init_params(self):
        self.slider_wu0.setValue(50)
        self.slider_wu1.setValue(50)
        self.slider_wu2.setValue(50)
        self.slider_wl0.setValue(-50)
        self.slider_wl1.setValue(-50)
        self.slider_wl2.setValue(-50)
        self.slider_N1.setValue(50)
        self.slider_N2.setValue(100)

    def init_figs(self):
        self.shape_fig = QtFigure(self.airfoilShapeGraphics)
        self.flow_fig = QtFigure(self.flowFieldGraphics)

        self.shape_fig.update_plot(self.cst.coord)
        self.flow_fig.update_img(np.random.rand(128, 128), self.channel)
        # self.flow_fig.update_img(np.zeros((128, 128)), self.channel)

    def get_cst_params(self):
        wu0 = self.slider_wu0.value() / 100
        wu1 = self.slider_wu1.value() / 100
        wu2 = self.slider_wu2.value() / 100
        wl0 = self.slider_wl0.value() / 100
        wl1 = self.slider_wl1.value() / 100
        wl2 = self.slider_wl2.value() / 100
        N1 = self.slider_N1.value() / 100
        N2 = self.slider_N2.value() / 100
        cst_params = {"wu": [wu0, wu1, wu2], "wl": [wl0, wl1, wl2], "N1": N1, "N2": N2}
        return cst_params

    def bind_actions(self):
        self.slider_wu0.valueChanged.connect(self._update_shape)
        self.slider_wu1.valueChanged.connect(self._update_shape)
        self.slider_wu2.valueChanged.connect(self._update_shape)
        self.slider_wl0.valueChanged.connect(self._update_shape)
        self.slider_wl1.valueChanged.connect(self._update_shape)
        self.slider_wl2.valueChanged.connect(self._update_shape)
        self.slider_N1.valueChanged.connect(self._update_shape)
        self.slider_N2.valueChanged.connect(self._update_shape)

        self.doubleSpinBox_velocity.valueChanged.connect(self._update_Re)
        self.doubleSpinBox_nu.valueChanged.connect(self._update_Re)
        self.doubleSpinBox_rho.valueChanged.connect(self._update_Re)

        self.flowFieldChannels.currentTextChanged.connect(self._update_flowfield)
        self.pushButton_sim.clicked.connect(self._simulate)
        self.sim_thread.trigger.connect(self._simulate_over)

        self.actionsave.triggered.connect(self.save)

    def _update_shape(self):
        _translate = QCoreApplication.translate
        sender = self.sender()
        sender_name = sender.objectName()
        val = int(sender.value())
        v = val / 100
        if sender_name == "slider_wu0":
            self.cst.wu[0] = v
            self.label_wu0_val.setText(_translate("MainWindow", str(v)))
        elif sender_name == "slider_wu1":
            self.cst.wu[1] = v
            self.label_wu1_val.setText(_translate("MainWindow", str(v)))
        elif sender_name == "slider_wu2":
            self.cst.wu[2] = v
            self.label_wu2_val.setText(_translate("MainWindow", str(v)))
        elif sender_name == "slider_wl0":
            self.cst.wl[0] = v
            self.label_wl0_val.setText(_translate("MainWindow", str(v)))
        elif sender_name == "slider_wl1":
            self.cst.wl[1] = v
            self.label_wl1_val.setText(_translate("MainWindow", str(v)))
        elif sender_name == "slider_wl2":
            self.cst.wl[2] = v
            self.label_wl2_val.setText(_translate("MainWindow", str(v)))
        elif sender_name == "slider_N1":
            self.cst.N1 = v
            self.label_N1_val.setText(_translate("MainWindow", str(v)))
        elif sender_name == "slider_N2":
            self.cst.N2 = v
            self.label_N2_val.setText(_translate("MainWindow", str(v)))
        else:
            pass

        self.cst.cal_coord()
        self.shape_fig.update_plot(self.cst.coord)

    def _update_Re(self):
        _translate = QCoreApplication.translate

        L = 1
        velocity = self.doubleSpinBox_velocity.value()
        # rho = self.doubleSpinBox_rho.value()
        nu = self.doubleSpinBox_nu.value() * 1e-5
        Re = velocity * L / nu

        string_Re = f"Reynolds number:  {Re:.0f}"
        self.label_Re.setText(_translate("MainWindow", string_Re))

    def _update_flowfield(self):
        if len(self.simulation_results) == 0:
            return
        sender_name = self.sender().objectName()
        if sender_name == "flowFieldChannels":
            self.channel = self.flowFieldChannels.currentText()
            self.flow_fig.update_img(
                self.simulation_results[self.channel], self.channel
            )

    def get_sim_params(self):
        params = {
            "coord": self.cst.coord,
            "angle": self.doubleSpinBox_angle.value(),
            "velocity": self.doubleSpinBox_velocity.value(),
            "rho": self.doubleSpinBox_rho.value(),
            "nu": self.doubleSpinBox_nu.value() * 1e-5,
        }
        return params

    def _simulate(self):
        if self.sim_thread.isRunning():
            return
        else:
            self.label_sim_status.setText("Status: simulating!")
            self.sim_thread.set_params(self.get_sim_params())
            self.sim_thread.start()

    def _simulate_over(self, simulation_results):
        self.simulation_results = simulation_results
        self.label_sim_status.setText("Status done!")
        self.flow_fig.update_img(simulation_results[self.channel], self.channel)

    def save(self):
        # [0] is outputfile path, [1] is filetype filter
        fpath = QFileDialog.getSaveFileName(self, "save", ".", "mat files(*.mat)")[0]
        if not fpath.endswith(".mat"):
            fpath += ".mat"
        dict = {}
        dict.update(self.simulation_results)
        scio.savemat(fpath, dict)


def main():
    import sys

    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    widget = MainApp(mainWindow)
    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
