import matplotlib.pyplot as plt
from matplotlib import cycler
import numpy as np

from pathlib import Path
import json

import matplotlib

matplotlib.use("pgf")
matplotlib.rcParams.update(
    {
        "pgf.texsystem": "pdflatex",
        "text.usetex": True,
        "pgf.rcfonts": False,
    }
)


light_plots = {
    "lines.color": "black",
    "patch.edgecolor": "black",
    "text.color": "black",
    "axes.prop_cycle": cycler("color", ["#FFE15D", "#F49D1A", "#DC3535", "#B01E68"]),
    "axes.linewidth": 1.5,
    "axes.facecolor": "white",
    "axes.edgecolor": "black",
    "axes.labelcolor": "black",
    "xtick.color": "black",
    "ytick.color": "black",
    "figure.facecolor": "white",
    "figure.edgecolor": "white",
    # grid
    "axes.grid": True,
    "grid.color": "lightgray",
    "grid.linestyle": "dashed",
    # legend
    "legend.fancybox": False,
    "legend.edgecolor": "black",
    "legend.labelcolor": "black",
    "legend.framealpha": 0.8,
    "savefig.facecolor": "black",
    "savefig.edgecolor": "black",
    "savefig.transparent": True,
}

result_path = (Path(__file__).parent / "data").absolute()


def plot_importance(importance: dict[str, dict]) -> None:
    plt.rcParams.update(light_plots)
    goals = list(importance.keys())
    params = sorted(list(list(importance.values())[0].keys()))

    width = 0.5  # the width of the bars
    space = width / 2  # the space with between groups
    y_min = 0
    y_max = width * len(goals) * len(params) + space * (len(params) - 1)
    y = np.linspace(y_min, y_max, len(params))  # the label locations

    fig, ax = plt.subplots(layout="constrained", figsize=(3.0, 8.0))

    multiplier = 0
    for goal, attrs in importance.items():
        measurements = list()
        measurements_labels = list()
        for key in params:
            value = attrs.get(key)
            measurements.append(value)
            measurements_labels.append(round(value, 2))
        offset = width * multiplier
        rects = ax.barh(y + offset, measurements, width, label=goal)

        ax.bar_label(rects, measurements_labels, padding=3, fontsize="small")
        multiplier += 1

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel("Parameter", weight="bold")
    ax.set_xlabel("Normalized Parameter Importance", weight="bold")
    # ax.set_title('Normalized Parameter Importance')
    for i in range(len(params)):
        para = str(params[i])
        if para.startswith("a"):
            key_len = len("a")
            para = r"\alpha_" + str(int(para[key_len:]) + 1)
        elif para.startswith("material"):
            key_len = len("material")
            para = r"m_" + str(int(para[key_len:]) + 1)
        elif para.startswith("t"):
            key_len = len("t")
            para = r"t_" + str(int(para[key_len:]) + 1)
        params[i] = r"$\mathrm{" + para + r"}$"
    ax.set_yticks(y + width, params)
    ax.legend(loc="lower right", ncols=1)  # len(goals)
    ax.set_xlim([0, 1])
    ax.set_ylim([y_min - space, y_max + width * len(goals)])
    fig.tight_layout(pad=0)

    plt.savefig(result_path / ("params_importance" + ".pgf"))
    # plt.show()


with (result_path / "importance_metal.json").open("r") as fp:
    importance = json.load(fp)
plot_importance(importance)
