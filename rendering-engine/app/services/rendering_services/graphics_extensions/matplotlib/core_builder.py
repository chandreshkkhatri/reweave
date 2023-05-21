import matplotlib.pyplot as plt

class CoreBuilder:
    def __init__(self) -> None:
        self.plt = plt
        
    def __plot(self, x, y):
        self._strip_plot_ticks()
        self.plt.show()

    def _strip_grid_elements(self):
        self.ax.axis('off')

    def _strip_plot_frame(self):
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['bottom'].set_visible(False)
        self.ax.spines['left'].set_visible(False)
    
    def _strip_plot_ticks(self):
        self.ax.get_xaxis().set_visible(False)
        self.ax.get_yaxis().set_visible(False)

    