import matplotlib.pyplot as plt
from matplotlib import cycler
import numpy as np
from post_db import optimizers, storage

from pathlib import Path
import optuna
from itertools import combinations_with_replacement

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


def _get_subplot(axs, i, j):
    return axs[len(axs) - 1 - j, i]


def _format_values(df, labels, i, filter_ids=None):
    vals = df[f"values_{i}"]
    if filter_ids is not None:
        vals = vals[filter_ids]

    if labels[i] == "mass":
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
        if ticks < 6:
            break
        step = step * multiplier[counter % 3]
        counter = counter + 1

    return ticks, tick_min, tick_max


def _pointplot(axs, i, j, datasets: dict[str, object], labels):
    ax = _get_subplot(axs, i, j)
    # ax.set_title(f"{i}|{j}")
    # xs, x_min, x_max = _format_values(df, labels, i)
    # ys, y_min, y_max = _format_values(df, labels, j)
    # normal = ax.scatter(
    #     xs,
    #     ys,
    #     s=5,
    #     zorder=10,
    #     label="trials"
    # )
    plot_obj = []
    x_mins, x_maxs = [], []
    y_mins, y_maxs = [], []
    for category, values in datasets.items():
        color = values["color"]
        for study in values["dfs"]:
            df = study["df"]
            marker = study["marker"]
            label = r"$\mathrm{" + study["label"] + r"_{" + category + r"}}$"
            xs, x_min, x_max = _format_values(df, labels, i)
            x_mins.append(x_min)
            x_maxs.append(x_max)
            ys, y_min, y_max = _format_values(df, labels, j)
            y_mins.append(y_min)
            y_maxs.append(y_max)
            special = ax.scatter(
                xs, ys, s=8, zorder=20, label=label, color=color, marker=marker
            )
            plot_obj.append(special)

    ax.ticklabel_format(useOffset=False, style="plain")
    ax.tick_params(axis="both", labelsize="small")

    x_ticks, x_min, x_max = _calc_ticks(np.min(x_mins), np.max(x_maxs))
    y_ticks, y_min, y_max = _calc_ticks(np.min(y_mins), np.max(y_maxs))

    if j == 0:
        ax.set_xlim([x_min, x_max])
        ax.set_xticks(np.linspace(x_min, x_max, x_ticks))
        ax.set_xlabel(labels[i], weight="bold")
    else:
        ax.sharex(_get_subplot(axs, i, 0))
        plt.setp(ax.get_xticklabels(), visible=False)

    if i == 0:
        ax.set_ylim([y_min, y_max])
        ax.set_yticks(np.linspace(y_min, y_max, y_ticks))
        ax.set_ylabel(labels[j], weight="bold")
    else:
        ax.sharey(_get_subplot(axs, 0, j))
        plt.setp(ax.get_yticklabels(), visible=False)
        # ax.get_yaxis().set_visible(False)

    if i == (len(labels) - 1) and j == (len(labels) - 1):
        handles, labels = ax.get_legend_handles_labels()
        if False:
            ax.legend(
                handles,
                labels,
                loc="lower right",
                ncols=len(labels),
                bbox_to_anchor=(0, 1),
            )

    return plot_obj


def plot_study_results(datasets: dict[str, object], objectives):
    plt.rcParams.update(light_plots)
    num_axs = len(objectives)
    fig, axs = plt.subplots(
        nrows=num_axs, ncols=num_axs, figsize=(8, 8), layout="constrained"
    )

    for i, j in combinations_with_replacement(list(range(num_axs)), 2):
        _pointplot(axs, i, j, datasets, objectives)
        if i != j:
            _pointplot(axs, j, i, datasets, objectives)

    handles, labels = axs[0, 0].get_legend_handles_labels()
    fig.subplots_adjust(
        # left  = 0.1,  # the left side of the subplots of the figure
        # right = 0.01,    # the right side of the subplots of the figure
        # bottom = 0.1,   # the bottom of the subplots of the figure
        # top = 0.01,      # the top of the subplots of the figure
        wspace=0.2,  # the amount of width reserved for blank space between subplots
        hspace=0.2,  # the amount of height reserved for white space between subplots
    )
    # plt.subplots_adjust(top=0.7)
    # plt.tight_layout()
    plt.tight_layout(rect=[0.0, 0.0, 0.85, 0.85])

    plt.savefig(
        result_path / ("study" + ".pgf"),
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


legend = {
    "values_0": "mass",
    "values_1": "util.",
    "values_2": "rpm",
    "values_3": "deform.",
}

ascendences = {
    "values_0": True,
    "values_1": False,
    "values_2": False,
    "values_3": False,
}

runs = {
    "NSGA2": {"df": None, "marker": "d", "label": "NSGA2"},
    "NSGA3": {"df": None, "marker": "o", "label": "NSGA3"},
    "TPE": {"df": None, "marker": "x", "label": "TPE"},
}

criterias = {
    "trails": {"dfs": [], "color": "#fcbf49"},
    "mass": {"dfs": [], "color": "#f77f00"},
    "util.": {"dfs": [], "color": "#d62828"},
    "rpm": {"dfs": [], "color": "#003049"},
    "deform.": {"dfs": [], "color": "#0a9396"},
}

for optimizer in optimizers:
    study = optuna.create_study(
        study_name=f"simulation_{optimizer}",
        storage=storage,
        load_if_exists=True,
    )

    df = study.trials_dataframe(
        attrs=("number", "value", "params", "user_attrs", "duration", "state")
    )

    usefull_df = df[(df["values_1"] <= 1)]
    run = runs[optimizer.upper()].copy()
    run["df"] = usefull_df
    criterias["trails"]["dfs"].append(run)

    for key in legend.keys():
        criteria = legend[key]
        ascending = ascendences[key]

        run = runs[optimizer.upper()].copy()
        run["df"] = usefull_df.sort_values(by=key, ascending=ascending).head(1)
        criterias[criteria]["dfs"].append(run)

plot_study_results(
    criterias,
    ["mass", "utilization", "rpm", "deformation"],
)
