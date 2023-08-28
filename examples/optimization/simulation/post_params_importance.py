import optuna
import json
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import cycler
import matplotlib.patches as mpatches  # noqa
import numpy as np

if True:
    matplotlib.use("pgf")
    matplotlib.rcParams.update(
        {
            "pgf.texsystem": "pdflatex",
            "text.usetex": True,
            "pgf.rcfonts": False,
        }
    )


optimizers = ["nsga2", "nsga3", "tpe"]
result_path = (Path(__file__).parent / "data").absolute()

if False:
    importance = {"mass": dict(), "util.": dict(), "rpm": dict(), "deform.": dict()}
    for opti in optimizers:
        study = optuna.create_study(
            study_name=f"simulation_{opti}",  # simulation_metal or simulation_composite
            storage="sqlite:////home/willi/Nextcloud/share/sim13/db.sqlite3",
            load_if_exists=True,
        )

        df = study.trials_dataframe(
            attrs=("number", "value", "params", "user_attrs", "duration", "state")
        )

        importance["mass"][opti] = optuna.importance.get_param_importances(
            study, target=lambda t: t.values[0]
        )
        importance["util."][opti] = optuna.importance.get_param_importances(
            study, target=lambda t: t.values[1]
        )
        importance["rpm"][opti] = optuna.importance.get_param_importances(
            study, target=lambda t: t.values[2]
        )
        importance["deform."][opti] = optuna.importance.get_param_importances(
            study, target=lambda t: t.values[3]
        )

    with (result_path / "importance.json").open("w+") as fp:
        json.dump(importance, fp)

importance = dict()
with (result_path / "importance.json").open("r") as fp:
    importance = json.load(fp)


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

plt.rcParams.update(light_plots)


def plot_importance(
    importance: dict[str, dict[str, dict]], colors: list[str], markers: dict
) -> None:
    goals = list(importance.keys())
    optimizers = sorted(list(list(importance.values())[0].keys()))
    params = sorted(list(list(importance.values())[0][optimizers[0]].keys()))

    width = 1.0 / (len(goals) + 1)
    y_min = -width * (len(goals)) / 2
    y_max = len(params) - 1 + width * (len(goals)) / 2
    y = np.linspace(0, len(params) - 1, len(params))  # the label locations

    fig, ax = plt.subplots(layout="constrained", figsize=(3.0, 8.0))

    multiplier = 0
    for goal, studies in importance.items():
        offset = width * multiplier - width * (len(goals) - 1) / 2
        for opti, attrs in studies.items():
            xs, ys = list(), list()
            for i in range(len(params)):
                key = params[i]
                ys.append(i + offset)
                xs.append(attrs.get(key))
            ax.scatter(
                xs,
                ys,
                color=colors[multiplier],
                marker=markers[opti],
                zorder=10,
                label=str(opti.upper()) + r"$\mathrm{_{" + str(goal) + r"}}",
            )
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
        # elif para.startswith("t"):
        #     key_len = len("t")
        #     para = r"t_" + str(int(para[key_len:]) + 1)
        params[i] = r"$\mathrm{" + para + r"}$"
    ax.set_yticks(y, params)
    ax.legend(loc="center right", ncols=1)  # len(goals)
    ax.set_xlim([0, 1])
    ax.set_ylim([y_min, y_max])
    fig.tight_layout(pad=0)

    plt.savefig(result_path / ("params_importance" + ".pgf"))
    # plt.show()


plot_importance(
    importance,
    ["#fcbf49", "#f77f00", "#d62828", "#003049", "#0a9396"],
    {"nsga2": "d", "nsga3": "o", "tpe": "x"},
)
