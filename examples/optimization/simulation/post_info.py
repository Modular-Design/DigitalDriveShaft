import optuna
from pathlib import Path
import json
from post_db import optimizers, storage


for opti in optimizers:
    study = optuna.create_study(
        study_name=f"simulation_{opti}",  # simulation_metal or simulation_composite
        storage=storage,
        load_if_exists=True,
    )

    df = study.trials_dataframe(
        attrs=("number", "value", "params", "user_attrs", "duration", "state")
    )

    print(opti)
    # print(df)
    print(f"Simulation time: {df['duration'].sum()}")
    usefull_df = df[(df["values_1"] <= 1)]
    print(f"Usefull Trials: {usefull_df.shape[0]}")
    print("================================================")

exit()


def max_util(x):
    return
    # return max(x["values_1"], x["values_2"])


tlayers = [x for x in df.columns if x.startswith("params_t")]
nlayers = len(tlayers)

if "user_attrs_total_thickness" not in df.columns:

    def total_thickness(x):
        return sum([x[i] for i in tlayers])

    df["user_attrs_total_thickness"] = df.apply(total_thickness, axis=1)


print(usefull_df, end="\n###################\n")
rest_df = df[(df["values_1"] > 1)].sort_values(by=["values_1"])[
    ["user_attrs_total_thickness", "values_1", "user_attrs_utilization"]
]
print("Unusefull Variants:")
print(rest_df, end="\n###################\n")

if usefull_df.shape[0] == 0:
    exit()


if True:
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
