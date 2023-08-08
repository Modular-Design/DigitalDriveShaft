import optuna
from pathlib import Path
import json

study = optuna.create_study(
    study_name="simulation_metal",  # simulation_metal or simulation_composite
    storage="sqlite:////home/willi/Nextcloud/share/sim3/db.sqlite3",
    load_if_exists=True,
)

df = study.trials_dataframe(attrs=("number", "value", "params", "duration", "state"))
print("All trials:")
print(df, end="\n\n")

print(f"Simulation time: {df['duration'].sum()}", end="\n\n")


def max_util(x):
    return max(x["values_1"], x["values_2"])


df["utilization"] = df.apply(max_util, axis=1)

print("Sorted by utilization:")
sorted_df = df.sort_values(by="utilization")
print(sorted_df, end="\n\n")

print("Best Candiadate")
best_candidate = sorted_df.head(1)
print(best_candidate, end="\n\n")

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

result_path = (Path(__file__).parent / "data").absolute()
with (result_path / "importance_metal.json").open("w+") as fp:
    json.dump(importance, fp)


# print(importance)

print()
