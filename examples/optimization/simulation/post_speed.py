import matplotlib.pyplot as plt
from matplotlib import cycler
import numpy as np
from post_db import optimizers, storage

from pathlib import Path
import optuna

import matplotlib
import matplotlib.patches as mpatches  # noqa

if True:
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
    "axes.prop_cycle": cycler(
        "color", ["#fcbf49", "#f77f00", "#d62828", "#003049", "#0a9396"]
    ),
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
    "legend.framealpha": 1.0,
    "savefig.facecolor": "black",
    "savefig.edgecolor": "black",
    "savefig.transparent": True,
}

result_path = (Path(__file__).parent / "data").absolute()


def _format_values(vals, labels, i):
    if str(labels[i][0]).startswith("mass"):
        vals = vals * 1e3

    return vals, np.min(vals), np.max(vals)


def _calc_ticks(val_min, val_max) -> tuple[int, float, float]:
    step = 0.001
    ticks = 10
    counter = 0
    multiplier = [2, 5.0 / 2, 10 / 5]

    while True:
        tick_min = np.floor(val_min / step) * step
        tick_max = np.ceil(val_max / step) * step
        ticks = int((tick_max - tick_min) / step) + 1
        if ticks < 7:
            break
        step = step * multiplier[counter % 3]
        counter = counter + 1

    return ticks, tick_min, tick_max


def _speedplot(axs, i, datasets: dict[str, object], labels):
    ax = axs[i]

    plot_obj = []
    x_mins, x_maxs = [], []
    y_mins, y_maxs = [], []
    for optimizer, df in datasets.items():
        xs, ys = df["number"].to_numpy(), df[f"values_{i}"].to_numpy()
        ref_value = ys[0]
        assending = labels[i][1]
        for j in range(1, len(xs)):
            if assending:
                if ys[j] < ref_value:
                    ref_value = ys[j]
                else:
                    ys[j] = ref_value
            else:
                if ys[j] > ref_value:
                    ref_value = ys[j]
                else:
                    ys[j] = ref_value

        xs, x_min, x_max = _format_values(xs, labels, -1)
        x_mins.append(x_min)
        x_maxs.append(x_max)
        ys, y_min, y_max = _format_values(ys, labels, i)
        y_mins.append(y_min)
        y_maxs.append(y_max)
        special = ax.plot(xs, ys, zorder=20, label=optimizer)
        plot_obj.append(special)

    ax.ticklabel_format(useOffset=False, style="plain")
    ax.tick_params(axis="both", labelsize="small")

    x_ticks, x_min, x_max = _calc_ticks(np.min(x_mins), np.max(x_maxs))
    y_ticks, y_min, y_max = _calc_ticks(np.min(y_mins), np.max(y_maxs))

    ax.set_xlim([x_min, x_max])
    ax.set_xticks(np.linspace(x_min, x_max, x_ticks))
    if i == 0:  # len(labels) - 1:
        ax.set_xlabel("iterations", weight="bold")
        ax.legend(loc="upper right", fontsize="xx-small", handlelength=1)

    ax.set_ylim([y_min, y_max])
    ax.set_yticks(np.linspace(y_min, y_max, y_ticks))
    ax.set_ylabel(labels[i][0], weight="bold")

    return plot_obj


def plot_study_speed(datasets: dict[str, object], objectives):
    plt.rcParams.update(light_plots)
    fig, axs = plt.subplots(
        len(objectives), 1, figsize=(3, 5), layout="constrained", sharex=True
    )

    for i in range(len(objectives)):
        _speedplot(axs, i, datasets, objectives)

    handles, labels = axs[0].get_legend_handles_labels()
    fig.subplots_adjust(
        # left  = 0.1,  # the left side of the subplots of the figure
        # right = 0.01,    # the right side of the subplots of the figure
        # bottom = 0.1,   # the bottom of the subplots of the figure
        # top = 0.01,      # the top of the subplots of the figure
        wspace=0.2,  # the amount of width reserved for blank space between subplots
        hspace=0.2,  # the amount of height reserved for white space between subplots
    )
    # plt.subplots_adjust(top=0.7)
    plt.tight_layout()
    # plt.tight_layout(rect=[0.0, 0.0, 0.0, 0.0])

    plt.savefig(
        result_path / ("speed" + ".pgf"),
    )

    plt.clf()
    legend = plt.legend(handles, labels, ncols=5)

    def export_legend(legend, filename="legend.pgf", expand=[-5, -5, 5, 5]):
        fig = legend.figure
        fig.canvas.draw()
        bbox = legend.get_window_extent()
        bbox = bbox.from_extents(*(bbox.extents + np.array(expand)))
        bbox = bbox.transformed(fig.dpi_scale_trans.inverted())
        fig.savefig(result_path / filename, dpi="figure", bbox_inches=bbox)

    export_legend(legend)
    # plt.show()


dfs = dict()

for optimizer in optimizers:
    study = optuna.create_study(
        study_name=f"simulation_{optimizer}",
        storage=storage,
        load_if_exists=True,
    )

    df = study.trials_dataframe(
        attrs=("number", "value", "params", "user_attrs", "duration", "state")
    )

    dfs[optimizer.upper()] = df

plot_study_speed(
    dfs,
    [
        (r"mass $\mathrm{[kg]}$", True),
        (r"utilization $\mathrm{[\;]}$", True),
        (r"rpm $\mathrm{[rpm]}$", False),
        (r"deformation $\mathrm{[\mu m]}$", False),
    ],
)
