from pymaterial.materials import IsotropicMaterial, TransverselyIsotropicMaterial
from pymaterial.combis.clt import Stackup, Ply
import plotly.graph_objects as go
from plotly.subplots import make_subplots

steel = IsotropicMaterial(Em=2.1, nu=0.3, density=1)
ud_ep_cf_t700 = TransverselyIsotropicMaterial(123e3, 8.3e3, 0.3, 4.4e3, 1.55e-6)
bd_ep_cf_t700 = TransverselyIsotropicMaterial(78e3, 78e3, 0.07, 6.5e3, 1.60e-6)
ud_ep_gf = TransverselyIsotropicMaterial(39e3, 8.6e3, 0.28, 3.8e3, 2.1e-6)
bd_ep_gf = TransverselyIsotropicMaterial(29.7e3, 29.7e3, 0.17, 5.3e3, 2.2e-6)

stack_steel = Stackup([Ply(material=steel, thickness=1)])
stack_ud_cf = Stackup([Ply(material=ud_ep_cf_t700, thickness=1)])
stack_bd_cf = Stackup([Ply(material=bd_ep_cf_t700, thickness=1)])
stack_ud_gf = Stackup([Ply(material=ud_ep_gf, thickness=1)])
stack_bd_gf = Stackup([Ply(material=bd_ep_gf, thickness=1)])
# stacks = [stack_steel, stack_ud_cf, stack_bd_cf, stack_ud_gf, stack_bd_gf]

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


def get_rotations(stack: Stackup):
    phis = []
    ems = []
    gs = []
    nus = []
    n_div = 80
    phi_div = 360 / n_div
    for i in range(n_div + 1):
        phi = phi_div * i
        mat = stack.rotate(phi, degree=True).calc_homogenized()
        ems.append(mat.E_l)
        gs.append(mat.G_lt)
        nus.append(mat.nu_lt)
        phis.append(phi)
    return phis, ems, gs, nus


n_cols = len(stacks)
fig = make_subplots(rows=3, cols=n_cols, specs=[[{"type": "polar"}] * n_cols] * 3)

for i in range(n_cols):
    stack = stacks[i]

    col = i + 1
    phis, ems, gs, nus = get_rotations(stack)

    fig.add_trace(
        go.Scatterpolar(
            r=ems, theta=phis, mode="lines", name="E-Module", line={"color": "red"}
        ),
        1,
        col,
    )
    fig.add_trace(
        go.Scatterpolar(
            r=gs, theta=phis, mode="lines", name="G-Modlue", line={"color": "blue"}
        ),
        2,
        col,
    )
    fig.add_trace(
        go.Scatterpolar(
            r=nus,
            theta=phis,
            mode="lines",
            name="Querkontraktionszahl",
            line={"color": "green"},
        ),
        3,
        col,
    )

fig.update_layout(showlegend=False)
fig.show()
