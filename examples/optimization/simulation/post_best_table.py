import optuna
from pathlib import Path
import numpy as np

result_path = (Path(__file__).parent / "data").absolute()

materials = {
    r"CFK_{230}": r"CF_{395}",
    r"CFK_{395}": r"CF_{395}",
    "HTS40": r"CF_{40}",
    "Titanium": "Ti",
}


def table_best(datasets: dict[str, object]):
    with (result_path / "tab_overview.tex").open("+w") as fp:
        fp.writelines(
            [
                r"\begin{table*}[ht]",
                "\n",
                r"\renewcommand{\arraystretch}{1.3}",
                "\n",
                r"\setlength{\tabcolsep}{3pt}",
                "\n",
                r"\caption{",
                "Best Candidates from different Optimizers in different Categories",
                r"}",
                "\n",
                r"\label{tab:trails}",
                "\n",
                r"\centering",
                "\n",
            ]
        )
        fp.writelines(
            [
                r"\begin{tabular}{",
                str("c" * 9) + "c}",
                "\n",
                r"\hline",
                "\n",
                r"\textbf{Category}",
                "&",
                r"\textbf{Trail}",
                "&",
                r"$\mathrm{\mathbf{\alpha} \; \left[ ^\circ \right]}$",
                "&",
                r"\textbf{m} $\mathrm{\left[ \; \right]}$",
                "&",
                r"\textbf{s} $\mathrm{\left[ \; \right]}$",
                "&",
                r"\textbf{t} $\mathrm{\left[ mm \right]}$",
                "&",
                r"\textbf{mass} $\mathrm{\left[ kg \right]}$",
                "&",
                r"\textbf{util.} $\mathrm{\left[ \; \right]}$",
                "&",
                r"\textbf{rpm} $\mathrm{\left[ rpm \right]}$",
                "&",
                r"\textbf{deform.} $\mathrm{\left[ \mu m \right]}$\\",
                "\n",
                r"\hline",
                "\n",
                # r"\small", "\n"
            ]
        )
        n_layers = 4
        for descr, dataset in datasets.items():
            row = dataset.head(1)  # .loc[[0]]
            try:
                fp.writelines([descr, "&", str(row["number"].values[0]), "&"])
            except IndexError:
                print(f"ERROR: no entry found for: {descr}")
            fp.writelines(
                [
                    r"["
                    + ", ".join(
                        str(int(np.round(row[f"params_a{i}"].values[0], 0)))
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
                        + materials[row[f"params_material{i}"].values[0]]
                        + r"}$"
                        for i in range(n_layers)
                    )
                    + r"]",
                    "&",
                ]
            )
            fp.writelines(
                [
                    str(np.round(row["params_shape"].values[0], 1)),
                    "&",
                    str(np.round(row["params_t"].values[0], 1)),
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

optimizers = ["nsga2", "nsga3", "tpe"]


def generate_key(opti, value):
    return r"$\mathrm{{" + opti.upper() + r"}_{" + value + r"}}$"


candiadates = dict()
for value in legend.values():
    for opti in optimizers:
        key = generate_key(opti, value)
        candiadates[key] = None

optimizers = ["nsga3", "nsga2", "tpe"]

for optimizer in optimizers:
    study = optuna.create_study(
        study_name=f"simulation_{optimizer}",
        storage="sqlite:////home/willi/Nextcloud/share/sim13/db.sqlite3",
        load_if_exists=True,
    )

    df = study.trials_dataframe(
        attrs=("number", "value", "params", "user_attrs", "duration", "state")
    )

    print("#####################")
    print(optimizer)
    print("#####################")
    for col in df.columns:
        print(col)

    usefull_df = df[(df["values_1"] <= 1)]

    for key in legend.keys():
        criteria = legend[key]
        ascending = ascendences[key]
        candidate = generate_key(optimizer, criteria)
        candiadates[candidate] = usefull_df.sort_values(
            by=key, ascending=ascending
        ).head(1)

table_best(candiadates)
