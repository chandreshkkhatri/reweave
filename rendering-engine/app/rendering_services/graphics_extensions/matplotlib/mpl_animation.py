import numpy as np
from matplotlib.animation import FuncAnimation
from app.rendering_services.graphics_extensions.matplotlib.core_builder import CoreBuilder


class MPLAnimation(CoreBuilder):
    def __init__(self) -> None:
        super().__init__()

    def __animate_growing_coil(self):
        self.fig = self.plt.figure()
        self.axis = self.plt.axes(xlim=(-50, 50),
                                  ylim=(-50, 50))

        self.line, = self.axis.plot([], [], lw=2)
        self.xdata, self.ydata = [], []

        def init():
            self.line.set_data([], [])
            return self.line,

        def animate(i):
            t = 0.1 * i

            # x, y values to be plotted
            x = t * np.sin(t)
            y = t * np.cos(t)

            # appending values to the previously
            # empty x and y data holders
            self.xdata.append(x)
            self.ydata.append(y)
            self.line.set_data(self.xdata, self.ydata)

            return self.line,

        anim = FuncAnimation(self.fig, animate, init_func=init,
                             frames=500, interval=20, blit=True)
        anim.save('./builds/growingCoil.mp4', writer='ffmpeg', fps=30)


    def test(self):
        self.__animate_growing_coil()