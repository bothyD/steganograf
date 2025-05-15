import matplotlib
import matplotlib.patheffects
import matplotlib.pyplot as plt
import numpy


class PlotBuilder:
    __COLORS = ("tab:blue", "tab:red", "tab:green")

    @staticmethod
    def build_plot(title: str, data, save_path: str = "report/plot.png"):
        matplotlib.rcParams.update({"font.size": 14})

        xt = data.keys()
        data = list(data.values())
        data = {k: [x[k] for x in data] for k in data[0].keys()}

        x = numpy.arange(len(xt))
        width = 0.25
        multiplier = 0

        fig, ax = plt.subplots(constrained_layout=True)

        for index, (attribute, measurement) in enumerate(data.items()):
            offset = width * multiplier
            rects = ax.bar(
                x + offset,
                measurement,
                width,
                label=attribute,
                color=PlotBuilder.__COLORS[index],
            )
            ax.bar_label(rects, padding=3)
            multiplier += 1

        for text in ax.texts:
            text.set_path_effects(
                [matplotlib.patheffects.withStroke(linewidth=4, foreground="w")]
            )

        ax.set_xticks(x + width, [str(x) for x in xt])
        ax.grid(axis="y")
        ax.legend()

        if fig.canvas.manager is not None:
            fig.canvas.manager.set_window_title(title)

        
        fig.savefig(save_path, dpi=300, bbox_inches="tight")

        plt.show()