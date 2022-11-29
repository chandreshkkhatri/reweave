import numpy as np
import seaborn as sns
import seaborn.objects as so
import matplotlib.image as mpimg

from moviepy.video.io.bindings import mplfig_to_npimage
from src.services.graphics_extensions.matplotlib.mpl_make_frame_helpers import MPLMakeFrameHelpers


class MPLMakeFrame(MPLMakeFrameHelpers):
    def __init__(self) -> None:
        super().__init__()

    def _get_sin_wave_frame(self, t):
        self.fig, self.ax = self.plt.subplots()
        x = np.linspace(-2, 2, 200)
        self.ax.plot(x, np.sin(x*2 + 8*np.pi/2 * t))
        self._strip_grid_elements()
        return mplfig_to_npimage(self.fig)

    def _get_line_frame(self, t):
        self.fig, self.ax = self.plt.subplots()
        x = np.linspace(-2, 2, 200)
        y = []
        for i in x:
            if (int((i+2)*1000+t*50)) % 2 == 0:
                y.append(1)
            else:
                y.append(None)

        self.ax.plot(x, y)
        self._strip_grid_elements()
        return mplfig_to_npimage(self.fig)

    def _get_image_frame(self, t):
        self.fig, self.ax = self.plt.subplots()
        img = mpimg.imread('./res/images.png')
        img = self._move_img(img, -int(t*100), 0)
        imgplot = self.plt.imshow(img)
        self._strip_grid_elements()
        return mplfig_to_npimage(self.fig)

    def _move_img(self, img, x, y):
        img = np.roll(img, x, axis=1)
        img = np.roll(img, y, axis=0)
        return img

    def __seaborn_plot(self):
        df = sns.load_dataset("penguins")
        sns.pairplot(df, hue="species")
        self.plt.show()

    def test(self):
        self.__seaborn_plot()
