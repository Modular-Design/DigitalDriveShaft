from pymaterial.materials import TransverselyIsotropicMaterial
from pymaterial.combis.clt import Stackup, Ply
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ud_ep_cf_t700 = TransverselyIsotropicMaterial(45000, 15000, 0.3, 5600, 1.55e-6)
force = 1000
b = 20
p_0 = Ply(material=ud_ep_cf_t700, thickness=0.5)
p_15 = p_0.rotate(15, degree=True)
p_n15 = p_0.rotate(-15, degree=True)
p_30 = p_0.rotate(30, degree=True)
p_n30 = p_0.rotate(-30, degree=True)
p_45 = p_0.rotate(45, degree=True)
p_n45 = p_0.rotate(-45, degree=True)
p_60 = p_0.rotate(60, degree=True)
p_n60 = p_0.rotate(-60, degree=True)
p_90 = p_0.rotate(90, degree=True)

stacks_tens = [
    Stackup([p_0, p_90, p_90, p_0]),
    Stackup([p_45, p_n45, p_n45, p_45]),
    Stackup([p_30, p_n30, p_60, p_n60, p_n60, p_60, p_n30, p_30]),
    Stackup([p_0, p_90, p_45, p_n45, p_n45, p_45, p_90, p_0]),
    Stackup([p_0, p_0, p_90, p_90], False),
]


stacks_bend = [
    Stackup([p_0, p_90, p_90, p_0]),
    Stackup([p_90, p_0, p_0, p_90]),
    Stackup([p_45, p_n45, p_n45, p_45]),
    Stackup([p_30, p_n30, p_60, p_n60, p_n60, p_60, p_n30, p_30]),
    Stackup([p_0, p_90, p_45, p_n45, p_n45, p_45, p_90, p_0]),
    Stackup([p_90, p_0, p_45, p_n45, p_n45, p_45, p_0, p_90]),
]


def create_stackups_stress_strain_per_ply(stacks, loading):
    n_cols = len(stacks)
    fig = make_subplots(
        rows=2, cols=n_cols, specs=[[{}] * n_cols] * 2
    )  # 'type': 'scatter'

    for i in range(n_cols):
        stack = stacks[i]
        deformations = stack.apply_load(np.array(loading))
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
            go.Scatter(
                x=exs, y=zs, mode="lines", name="Strain", line={"color": "blue"}
            ),
            2,
            col,
        )

    fig.update_layout(showlegend=False)
    fig.show()


def create_stackups_stress_strain(stacks):
    n_cols = len(stacks)
    fig = make_subplots(rows=1, cols=n_cols, specs=[[{}] * n_cols])  # 'type': 'scatter'
    strains = np.arange(0.0, 0.05 + 0.01, 0.01)
    for i in range(n_cols):
        stack = stacks[i]
        mat = stack.calc_homogenized()
        stresses = mat.get_E1() * strains

        col = i + 1

        fig.add_trace(
            go.Scatter(
                x=strains,
                y=stresses,
                mode="lines",
                name="Stress",
                line={"color": "red"},
            ),
            1,
            col,
        )

    fig.update_layout(showlegend=False)
    fig.show()


# create_stackups_stress_strain(stacks_tens)
create_stackups_stress_strain_per_ply(stacks_tens, [force / 10, 0, 0, 0, 0, 0])

# create_stackups_stress_strain(stacks_bend)
create_stackups_stress_strain_per_ply(stacks_bend, [0, 0, 0, force * 80 / 10, 0, 0])
