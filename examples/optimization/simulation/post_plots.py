import matplotlib.pyplot as plt
from matplotlib import cycler
import numpy as np

from pathlib import Path
import json

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
        rects = ax.barh(y + offset, measurements, width, label=goal, zorder=10)

        ax.bar_label(rects, measurements_labels, padding=3, fontsize=8)
        multiplier += 1

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel("Parameter", weight="bold")
    ax.set_xlabel("Parameter Importance", weight="bold")
    # ax.set_title('Normalized Parameter Importance')
    for i in range(len(params)):
        para = str(params[i])
        if para.startswith("a"):
            key_len = len("a")
            para = r"\alpha_" + str(int(para[key_len:]) + 1)
        elif para.startswith("material"):
            key_len = len("material")
            para = r"m_" + str(int(para[key_len:]) + 1)
        elif para.startswith("shape"):
            key_len = len("shape")
            para = r"s"
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


if __name__ == "__main__":
    with (result_path / "importance_metal.json").open("r") as fp:
        importance = json.load(fp)
    plot_importance(importance)


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
    for label, dataset in datasets.items():
        xs, x_min, x_max = _format_values(dataset, labels, i)
        x_mins.append(x_min)
        x_maxs.append(x_max)
        ys, y_min, y_max = _format_values(dataset, labels, j)
        y_mins.append(y_min)
        y_maxs.append(y_max)
        special = ax.scatter(xs, ys, s=8, zorder=20, label=label)
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
    plt.legend(
        handles,
        labels,
        loc="lower left",
        # mode="expand",
        bbox_to_anchor=(0.2, 0),
        bbox_transform=fig.transFigure,
        # borderaxespad=0,
        ncols=len(labels),
    )

    # fig.get_layout_engine().set(
    #     w_pad=0.01, h_pad=0.01,
    #     hspace=2,wspace=2
    # )
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
    plt.tight_layout(rect=[0, 0, 0.0, 0.0])

    plt.savefig(
        result_path / ("study" + ".pgf"),
    )
    # plt.show()


def table_best(datasets: dict[str, object]):
    with (result_path / "tab_overview.tex").open("+w") as fp:
        fp.writelines(
            [
                r"\begin{table*}[ht]",
                "\n",
                r"\renewcommand{\arraystretch}{1.3}",
                "\n",
                r"\caption{Best Candidates in different Categories}",
                "\n",
                r"\label{tab:trails}",
                "\n",
                r"\centering",
                "\n",
            ]
        )
        fp.writelines(
            [
                r"\begin{tabular}{|c|c|c|c|c|c|c|c|c|}",
                "\n",
                r"\hline",
                "\n",
                r"\textbf{Category}",
                "&",
                r"\textbf{Trail}",
                "&",
                r"$\mathrm{\mathbf{\alpha \; \left[ ^\circ \right]}}$",
                "&",
                r"$\mathrm{\mathbf{m \; \left[ \; \right]}}$",
                "&",
                r"$\mathrm{\mathbf{t \; \left[ mm \right]}}$",
                "&",
                r"$\mathrm{\mathbf{mass \; \left[ kg \right]}}$",
                "&",
                r"$\mathrm{\mathbf{utili \; \left[ \; \right]}}$",
                "&",
                r"$\mathrm{\mathbf{rpm \; \left[ rpm \right]}}$",
                "&",
                r"$\mathrm{\mathbf{bending \; \left[ \mu m \right]}}$\\",
                "\n",
                r"\hline",
                "\n",
                # r"\small", "\n"
            ]
        )
        n_layers = 4
        for descr, dataset in datasets.items():
            row = dataset.head(1)  # .loc[[0]]
            fp.writelines([descr, "&", str(row["number"].values[0]), "&"])
            fp.writelines(
                [
                    r"["
                    + ", ".join(
                        str(np.round(row[f"params_a{i}"].values[0], 1))
                        for i in range(n_layers)
                    )
                    + r"]",
                    "&",
                ]
            )
            fp.writelines(
                [
                    r"["
                    + ", ".join(
                        r"$\mathrm{"
                        + row[f"params_material{i}"]
                        .values[0]
                        .replace("Titanium", "Ti")
                        .replace(r"\;GPa", "")
                        + r"}$"
                        for i in range(n_layers)
                    )
                    + r"]",
                    "&",
                ]
            )
            fp.writelines(
                [
                    r"["
                    + ", ".join(
                        str(np.round(row[f"params_t{i}"].values[0], 1))
                        for i in range(n_layers)
                    )
                    + r"]",
                    "&",
                ]
            )
            fp.writelines(
                [
                    str(np.round(row[f"values_{0}"].values[0] * 1e3, 1)),  # mass
                    "&",
                    str(np.round(row[f"values_{1}"].values[0], 2)),  # util
                    "&",
                    str(int(np.round(row[f"values_{2}"].values[0], 0))),  # rpm
                    "&",
                    str(np.round(row[f"values_{3}"].values[0] * 1e3, 2)),  # bending
                    r"\\",
                    "\n",
                ]
            )

        fp.writelines(
            [
                r"\hline",
                "\n",
                r"\end{tabular}",
                "\n",
                r"\end{table*}",
                "\n",
            ]
        )
