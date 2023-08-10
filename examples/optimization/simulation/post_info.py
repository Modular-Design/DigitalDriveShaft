import optuna
from pathlib import Path
import json
from post_plots import plot_study_results, table_best

study = optuna.create_study(
    study_name="simulation",  # simulation_metal or simulation_composite
    storage="sqlite:////home/willi/Nextcloud/share/sim5/db.sqlite3",
    load_if_exists=True,
)

df = study.trials_dataframe(
    attrs=("number", "value", "params", "user_attrs", "duration", "state")
)
print("All trials:")
print(df, end="\n\n")

print(f"Simulation time: {df['duration'].sum()}", end="\n\n")


def max_util(x):
    return
    # return max(x["values_1"], x["values_2"])


# df["utilization"] = df.apply(max_util, axis=1)


print("Usefull Variants:")
usefull_df = df[(df["values_1"] <= 1)]
print(usefull_df, end="\n###################\n")
rest_df = df[(df["values_1"] > 1)]
print("Unusefull Variants:")
print(rest_df, end="\n###################\n")

print("Best Candiadates")

bc_mass = usefull_df.sort_values(by="values_0").head(1)
bc_util = usefull_df.sort_values(by="values_1", ascending=False).head(1)
bc_rpm = usefull_df.sort_values(by="values_2", ascending=False).head(1)
bc_bending = usefull_df.sort_values(by="values_3", ascending=False).head(1)


cfk_df = df[
    (
        (df["params_material0"] == "CFK")
        & (df["params_material1"] == "CFK")
        & (df["params_material2"] == "CFK")
        & (df["params_material3"] == "CFK")
    )
]

print(cfk_df.shape[0])

CFK_mass = cfk_df.sort_values(by="values_0").head(1)
CFK_util = cfk_df.sort_values(by="values_1", ascending=True).head(1)
CFK_rpm = cfk_df.sort_values(by="values_2", ascending=False).head(1)
CFK_bending = cfk_df.sort_values(by="values_3", ascending=False).head(1)


if False:
    importance = dict()
    importance["mass"] = optuna.importance.get_param_importances(
        study, target=lambda t: t.values[0]
    )
    importance["utilization"] = optuna.importance.get_param_importances(
        study, target=lambda t: t.values[1]
    )
    importance["rpm"] = optuna.importance.get_param_importances(
        study, target=lambda t: t.values[2]
    )

    importance["bending"] = optuna.importance.get_param_importances(
        study, target=lambda t: t.values[3]
    )

    result_path = (Path(__file__).parent / "data").absolute()
    with (result_path / "importance_metal.json").open("w+") as fp:
        json.dump(importance, fp)


print(f"usefull: {len(usefull_df.index[:])}")
print(f"rest: {len(rest_df.index[:])}")

if False:
    plot_study_results(
        df,
        ["mass", "utilization", "rpm", "bending"],
        {
            # "trails": rest_df.index[:],
            "trails": usefull_df.index[:],
            "mass": bc_mass.index[0],
            "utilization": bc_util.index[0],
            "rpm": bc_rpm.index[0],
            "bending": bc_bending.index[0],
        },
    )


if True:
    table_best(
        df,
        {
            "mass": bc_mass.index[0],
            "utilization": bc_util.index[0],
            "rpm": bc_rpm.index[0],
            "bending": bc_bending.index[0],
            # r"$\mathrm{CFK_{mass}}$": CFK_mass.index[0],
            # r"$\mathrm{CFK_{util.}}$":CFK_util.index[0],
            # r"$\mathrm{CFK_{rpm}}$":CFK_rpm.index[0],
            # r"$\mathrm{CFK_{bend.}}$":CFK_bending.index[0],
        },
    )
