from pymaterial.materials import TransverselyIsotropicMaterial
from pymaterial.combis.clt import Stackup, Ply
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ud_ep_cf_t700 = TransverselyIsotropicMaterial(123e3, 8.3e3, 0.3, 4.4e3, 1.55e-6)

p_0 = Ply(material=ud_ep_cf_t700, thickness=1)
p_15 = p_0.rotate(15, degree=True)
p_n15 = p_0.rotate(-15, degree=True)
p_45 = p_0.rotate(45, degree=True)
p_n45 = p_0.rotate(-45, degree=True)
p_60 = p_0.rotate(60, degree=True)
p_n60 = p_0.rotate(-60, degree=True)
p_90 = p_0.rotate(90, degree=True)

stacks = [
    Stackup([p_0, p_90, p_90, p_0]),
    Stackup([p_45, p_n45, p_n45, p_45]),
    Stackup([p_0, p_90, p_45, p_n45, p_n45, p_45, p_90, p_0]),
    Stackup([p_0, p_60, p_n60, p_n60, p_60, p_0]),
    Stackup([p_n15, p_45, p_0, p_45, p_n15]),
]

n_cols = len(stacks)

fig = make_subplots(rows=2, cols=n_cols, specs=[[{}] * n_cols] * 2)  # 'type': 'scatter'

for i in range(n_cols):
    stack = stacks[i]
    deformations = stack.apply_load(np.array([1, 0, 0, 0, 0, 0]))
    strains = stack.get_strains(deformations)
    stresses = stack.get_stresses(strains)

    col = i + 1

    sxs = []
    for stress in stresses:
        bot, top = stress
        sxs.append(bot[0])
        sxs.append(top[0])

    exs = []
    for strain in strains:
        bot, top = strain
        exs.append(bot[0])
        exs.append(top[0])

    zs = []
    height = stack.get_thickness()
    plies = stack.get_plies()
    z = -height / 2.0
    for ply in plies:
        zs.append(z)
        z += ply.get_thickness()
        zs.append(z)

    fig.add_trace(
        go.Scatter(x=sxs, y=zs, mode="lines", name="Stress", line={"color": "red"}),
        1,
        col,
    )
    fig.add_trace(
        go.Scatter(x=exs, y=zs, mode="lines", name="Strain", line={"color": "blue"}),
        2,
        col,
    )

fig.update_layout(showlegend=False)
fig.show()
