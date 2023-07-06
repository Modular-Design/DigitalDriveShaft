import numpy as np
import os
from ansys.mapdl.core import launch_mapdl


def mkdir(path):
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)
        print("---  new folder...  ---")
        print("---  OK  ---")
    else:
        print("---  There is this folder!  ---")


# constants
thickness = 12  # meters
rad = 85
rad_out = rad + thickness
rad_in = rad - thickness / 2


def material():
    # Define element types
    mapdl.et(1, "solid185")
    mapdl.keyopt(1, 2, 2)
    mapdl.keyopt(1, 3, 1)
    mapdl.sectype(1, "shell")
    mapdl.secoffset("bot")
    mapdl.secdata(1, 1, 0)
    mapdl.et(2, "solid185")
    mapdl.keyopt(2, 2, 2)
    mapdl.et(3, 154)
    mapdl.et(4, "solid185")
    mapdl.keyopt(4, 2, 2)
    mapdl.keyopt(4, 3, 1)
    mapdl.sectype(4, "shell")
    mapdl.secoffset("bot")
    mapdl.secdata(1, 4, 45)
    mapdl.et(5, "solid185")
    mapdl.keyopt(5, 2, 2)
    mapdl.keyopt(5, 3, 1)
    mapdl.sectype(5, "shell")
    mapdl.secoffset("bot")
    mapdl.secdata(1, 5, -45)
    mapdl.et(6, "solid185")
    mapdl.keyopt(6, 2, 2)
    mapdl.keyopt(6, 3, 1)
    mapdl.sectype(6, "shell")
    mapdl.secoffset("bot")
    mapdl.secdata(1, 6, 90)
    # Define metal material and composite material
    mapdl.mp("EX", 1, 1.334e5)  # Elastic moduli in MPa
    mapdl.mp("EY", 1, 5.750e3)
    mapdl.mp("EZ", 1, 5.750e3)
    mapdl.mp("GXY", 1, 2.358e3)
    mapdl.mp("GXZ", 1, 2.358e3)
    mapdl.mp("GYZ", 1, 1.095e3)
    mapdl.mp("PRXY", 1, 0.2875)  # Poisson's Ratio
    mapdl.mp("PRXZ", 1, 0.2875)
    mapdl.mp("PRYZ", 1, 0.37)
    mapdl.mp("MU", 1, 0.3)  # Coefficient of friction
    # Define failure criteria
    mapdl.fc(1, "s", "XTEN", 852)
    mapdl.fc(1, "s", "XCMP", -631)
    mapdl.fc(1, "s", "YTEN", 57)
    mapdl.fc(1, "s", "YCMP", -200)
    mapdl.fc(1, "s", "ZTEN", 57)
    mapdl.fc(1, "s", "ZCMP", -200)
    mapdl.fc(1, "s", "XY", 132)
    mapdl.fc(1, "s", "XZ", 132)
    mapdl.fc(1, "s", "YZ", 58)
    mapdl.fc(1, "s", "YZIT", 0.3)
    mapdl.fc(1, "s", "YZIC", 0.3)
    mapdl.mp("EX", 2, 190e3)  # Elastic moduli in MPa (kg/(m*s**2))
    mapdl.mp("NUXY", 2, 0.29)  # Poisson's Ratio
    mapdl.mp("MU", 2, 0.3)  # Coefficient of friction
    mapdl.fc(2, "s", "XTEN", 1950)
    mapdl.fc(2, "s", "YTEN", 1950)
    mapdl.fc(2, "s", "ZTEN", 1950)
    mapdl.fc(2, "s", "XY", 1131)
    mapdl.fc(2, "s", "XZ", 1131)
    mapdl.fc(2, "s", "YZ", 1131)
    mapdl.mp("EX", 4, 1.334e5)  # Elastic moduli in MPa
    mapdl.mp("EY", 4, 5.750e3)
    mapdl.mp("EZ", 4, 5.750e3)
    mapdl.mp("GXY", 4, 2.358e3)
    mapdl.mp("GXZ", 4, 2.358e3)
    mapdl.mp("GYZ", 4, 1.095e3)
    mapdl.mp("PRXY", 4, 0.2875)  # Poisson's Ratio
    mapdl.mp("PRXZ", 4, 0.2875)
    mapdl.mp("PRYZ", 4, 0.37)
    mapdl.mp("MU", 4, 0.3)  # Coefficient of friction
    # Define failure criteria
    mapdl.fc(4, "s", "XTEN", 852)
    mapdl.fc(4, "s", "XCMP", -631)
    mapdl.fc(4, "s", "YTEN", 57)
    mapdl.fc(4, "s", "YCMP", -200)
    mapdl.fc(4, "s", "ZTEN", 57)
    mapdl.fc(4, "s", "ZCMP", -200)
    mapdl.fc(4, "s", "XY", 132)
    mapdl.fc(4, "s", "XZ", 132)
    mapdl.fc(4, "s", "YZ", 58)
    mapdl.fc(4, "s", "YZIT", 0.3)
    mapdl.fc(4, "s", "YZIC", 0.3)
    mapdl.mp("EX", 5, 1.334e5)  # Elastic moduli in MPa
    mapdl.mp("EY", 5, 5.750e3)
    mapdl.mp("EZ", 5, 5.750e3)
    mapdl.mp("GXY", 5, 2.358e3)
    mapdl.mp("GXZ", 5, 2.358e3)
    mapdl.mp("GYZ", 5, 1.095e3)
    mapdl.mp("PRXY", 5, 0.2875)  # Poisson's Ratio
    mapdl.mp("PRXZ", 5, 0.2875)
    mapdl.mp("PRYZ", 5, 0.37)
    mapdl.mp("MU", 5, 0.3)  # Coefficient of friction
    # Define failure criteria
    mapdl.fc(5, "s", "XTEN", 852)
    mapdl.fc(5, "s", "XCMP", -631)
    mapdl.fc(5, "s", "YTEN", 57)
    mapdl.fc(5, "s", "YCMP", -200)
    mapdl.fc(5, "s", "ZTEN", 57)
    mapdl.fc(5, "s", "ZCMP", -200)
    mapdl.fc(5, "s", "XY", 132)
    mapdl.fc(5, "s", "XZ", 132)
    mapdl.fc(5, "s", "YZ", 58)
    mapdl.fc(5, "s", "YZIT", 0.3)
    mapdl.fc(5, "s", "YZIC", 0.3)
    mapdl.mp("EX", 6, 1.334e5)  # Elastic moduli in MPa
    mapdl.mp("EY", 6, 5.750e3)
    mapdl.mp("EZ", 6, 5.750e3)
    mapdl.mp("GXY", 6, 2.358e3)
    mapdl.mp("GXZ", 6, 2.358e3)
    mapdl.mp("GYZ", 6, 1.095e3)
    mapdl.mp("PRXY", 6, 0.2875)  # Poisson's Ratio
    mapdl.mp("PRXZ", 6, 0.2875)
    mapdl.mp("PRYZ", 6, 0.37)
    mapdl.mp("MU", 6, 0.3)  # Coefficient of friction
    # Define failure criteria
    mapdl.fc(6, "s", "XTEN", 852)
    mapdl.fc(6, "s", "XCMP", -631)
    mapdl.fc(6, "s", "YTEN", 57)
    mapdl.fc(6, "s", "YCMP", -200)
    mapdl.fc(6, "s", "ZTEN", 57)
    mapdl.fc(6, "s", "ZCMP", -200)
    mapdl.fc(6, "s", "XY", 132)
    mapdl.fc(6, "s", "XZ", 132)
    mapdl.fc(6, "s", "YZ", 58)
    mapdl.fc(6, "s", "YZIT", 0.3)
    mapdl.fc(6, "s", "YZIC", 0.3)


def model(row, sectors, bolt_diameter, distance_between_rows, edge_distance):
    # generate plates
    mapdl.cylind(rad, rad_out, "", length + 8, "", arc_end)
    mapdl.cylind(rad - 0.001, rad_in, -8, length, "", arc_end)
    # generate holes and mesh
    for i in range(0, row):
        k0 = mapdl.k("", 0, 0, 0)
        kline = mapdl.k(
            "",
            rad * np.cos(arc_cent * (i % 2 + 0.5)),
            rad * np.sin(arc_cent * (i % 2 + 0.5)),
            0,
        )
        line1 = mapdl.l(k0, kline)
        mapdl.lwplan("", line1, 0)
        h = distance_between_rows * i + edge_distance
        bolt = mapdl.cyl4(0, -h, "", "", bolt_diameter / 2, "", 100)
        mapdl.vsbv("all", bolt)
        arc_mesh = min(edge_distance / rad, arc_cent / 2)
        length_mesh = min(edge_distance, arc_cent * rad / 2)
        # arc_mesh = bolt_diameter / rad
        k1 = mapdl.k(
            "",
            (rad_out + 10) * np.cos(arc_cent * (i % 2 + 0.5) - arc_mesh),
            (rad_out + 10) * np.sin(arc_cent * (i % 2 + 0.5) - arc_mesh),
            h - length_mesh,
        )
        k2 = mapdl.k(
            "",
            rad_in * np.cos(arc_cent * (i % 2 + 0.5) - arc_mesh),
            rad_in * np.sin(arc_cent * (i % 2 + 0.5) - arc_mesh),
            h - length_mesh,
        )
        k3 = mapdl.k(
            "",
            (rad_out + 10) * np.cos(arc_cent * (i % 2 + 0.5) + arc_mesh),
            (rad_out + 10) * np.sin(arc_cent * (i % 2 + 0.5) + arc_mesh),
            h - length_mesh,
        )
        k4 = mapdl.k(
            "",
            rad_in * np.cos(arc_cent * (i % 2 + 0.5) + arc_mesh),
            rad_in * np.sin(arc_cent * (i % 2 + 0.5) + arc_mesh),
            h - length_mesh,
        )
        k5 = mapdl.k(
            "",
            (rad_out + 10) * np.cos(arc_cent * (i % 2 + 0.5) - arc_mesh),
            (rad_out + 10) * np.sin(arc_cent * (i % 2 + 0.5) - arc_mesh),
            h + length_mesh,
        )
        k6 = mapdl.k(
            "",
            rad_in * np.cos(arc_cent * (i % 2 + 0.5) - arc_mesh),
            rad_in * np.sin(arc_cent * (i % 2 + 0.5) - arc_mesh),
            h + length_mesh,
        )
        k7 = mapdl.k(
            "",
            (rad_out + 10) * np.cos(arc_cent * (i % 2 + 0.5) + arc_mesh),
            (rad_out + 10) * np.sin(arc_cent * (i % 2 + 0.5) + arc_mesh),
            h + length_mesh,
        )
        k8 = mapdl.k(
            "",
            rad_in * np.cos(arc_cent * (i % 2 + 0.5) + arc_mesh),
            rad_in * np.sin(arc_cent * (i % 2 + 0.5) + arc_mesh),
            h + length_mesh,
        )
        mapdl.a(k1, k2, k4, k3)  # area1
        mapdl.a(k3, k4, k8, k7)  # area2
        mapdl.a(k7, k8, k6, k5)  # area3
        mapdl.a(k5, k6, k2, k1)  # area4
        mapdl.a(k1, k2, k8, k7)  # area5
        mapdl.a(k3, k4, k6, k5)  # area6
        if distance_between_rows > 2 * length_mesh:
            mapdl.kwplan("", k1, k2, k3)
            mapdl.vsbw("all")
            mapdl.kwplan("", k5, k6, k7)
            mapdl.vsbw("all")
        # mapdl.aplot()
        mapdl.vsba("all", "all")
        k30 = mapdl.k("", 0, 0, h)
        k31 = mapdl.k("", 0, 1, h)
        k32 = mapdl.k("", 1, 0, h)
        mapdl.kwplan("", k31, k32, k30)
        mapdl.vsbw("all")
    k10 = mapdl.k(
        "", (rad_out + 100) * np.cos(arc_cent), (rad_out + 100) * np.sin(arc_cent), -10
    )
    k11 = mapdl.k("", 0, 0, -10)
    k12 = mapdl.k(
        "",
        (rad_out + 100) * np.cos(arc_cent),
        (rad_out + 100) * np.sin(arc_cent),
        length + 100,
    )
    k13 = mapdl.k("", 0, 0, length + 100)
    mapdl.a(k10, k11, k13, k12)  # area_cent
    k14 = mapdl.k(
        "",
        (rad_out + 100) * np.cos(arc_cent / 2),
        (rad_out + 100) * np.sin(arc_cent / 2),
        -10,
    )
    k15 = mapdl.k("", 0, 0, -10)
    k16 = mapdl.k(
        "",
        (rad_out + 100) * np.cos(arc_cent / 2),
        (rad_out + 100) * np.sin(arc_cent / 2),
        length + 100,
    )
    k17 = mapdl.k("", 0, 0, length + 100)
    mapdl.a(k14, k15, k17, k16)  # area_cent0
    k18 = mapdl.k(
        "",
        (rad_out + 100) * np.cos(arc_cent * 1.5),
        (rad_out + 100) * np.sin(arc_cent * 1.5),
        -10,
    )
    k19 = mapdl.k("", 0, 0, -10)
    k20 = mapdl.k(
        "",
        (rad_out + 100) * np.cos(arc_cent * 1.5),
        (rad_out + 100) * np.sin(arc_cent * 1.5),
        length + 100,
    )
    k21 = mapdl.k("", 0, 0, length + 100)
    mapdl.a(k18, k19, k21, k20)  # area_cent1
    # mapdl.aplot()
    mapdl.vsba("all", "all")
    mapdl.csys(1)
    for i in range(6, 15):
        k1 = mapdl.k("", rad_in + (thickness / 10) * i, 0, -8)
        k2 = mapdl.k("", rad_in + (thickness / 10) * i, arc_end, -8)
        k3 = mapdl.k("", rad_in + (thickness / 10) * i, arc_end, length + 8)
        k4 = mapdl.k("", rad_in + (thickness / 10) * i, 0, length + 8)
        mapdl.a(k1, k2, k3, k4)
    mapdl.vsba("all", "all")


def bolt(row, sectors, bolt_diameter, distance_between_rows, edge_distance):
    # generate bolts
    for i in range(0, row):
        mapdl.csys(0)
        k0 = mapdl.k("", 0, 0, 0)
        kline = mapdl.k(
            "",
            rad * np.cos(arc_cent * (i % 2 + 0.5)),
            rad * np.sin(arc_cent * (i % 2 + 0.5)),
            0,
        )
        line1 = mapdl.l(k0, kline)
        mapdl.lwplan("", line1, 0.97 - (thickness / 2) / rad)
        h = distance_between_rows * i + edge_distance
        mapdl.wpoffs(yoff=-h)
        # for j in range(4):
        #    bolt = mapdl.cylind(
        #       bolt_diameter / 2, '', '',
        #       1.5 * thickness + 3, 90*(j-1),
        #       90*j
        #    )
        mapdl.cylind(bolt_diameter / 2, "", "", 1.5 * thickness + 5)  # bolt
        mapdl.cswpla(30 + i, 0)
        k1 = mapdl.k("", -bolt_diameter / 2, 0, 0)
        k2 = mapdl.k("", bolt_diameter / 2, 0, 0)
        k3 = mapdl.k("", bolt_diameter / 2, 0, 1.5 * thickness + 5)
        k4 = mapdl.k("", -bolt_diameter / 2, 0, 1.5 * thickness + 5)
        mapdl.a(k1, k2, k3, k4)  # area1
        k5 = mapdl.k("", 0, -bolt_diameter / 2, 0)
        k6 = mapdl.k("", 0, bolt_diameter / 2, 0)
        k7 = mapdl.k("", 0, bolt_diameter / 2, 1.5 * thickness + 5)
        k8 = mapdl.k("", 0, -bolt_diameter / 2, 1.5 * thickness + 5)
        mapdl.a(k5, k6, k7, k8)  # area2
        mapdl.asel("s", "loc", "x", 0)
        mapdl.asel("r", "loc", "y", 0)
        mapdl.vsel("s", "loc", "x", 0)
        mapdl.vsel("r", "loc", "y", 0)
        mapdl.vsba("all", "all")


def mesh_shaft():
    # mesh density in thickness direction
    mapdl.lsel("s", "length", "", thickness / 10)
    mapdl.lsel("u", "radius", "", bolt_diameter / 3, bolt_diameter / 1)
    mapdl.lesize("all", ndiv=2)
    mapdl.lsel("s", "length", "", thickness / 2 - 0.001)
    mapdl.lsel("u", "radius", "", bolt_diameter / 3, bolt_diameter / 1)
    mapdl.lesize("all", ndiv=5)
    # mesh density of holes
    mapdl.csys("1")
    mapdl.lsel("s", "loc", "x", rad - 0.2, rad + 0.2)
    mapdl.lsel("r", "radius", "", bolt_diameter / 3, bolt_diameter / 1)
    mapdl.lesize("all", ndiv=em_hole / 8)
    # mesh density of radial lines
    arc_mesh = min(edge_distance / rad, arc_cent / 2)
    length_mesh = min(edge_distance, arc_cent * rad / 2)
    for i in range(0, row):
        h = distance_between_rows * i + edge_distance
        mapdl.csys(1)
        mapdl.asel("s", "loc", "x", rad - 0.2, rad + 0.2)
        mapdl.lsla()
        mapdl.lsel(
            "r",
            "loc",
            "y",
            (arc_cent * (i % 2 + 0.5) - arc_mesh + 0.01) * 180 / np.pi,
            (arc_cent * (i % 2 + 0.5) + arc_mesh - 0.01) * 180 / np.pi,
        )
        mapdl.lsel("r", "loc", "z", h - length_mesh + 0.1, h + length_mesh - 0.1)
        mapdl.lsel("u", "radius", "", bolt_diameter / 3, bolt_diameter / 1)
        # mapdl.lesize(
        #   'all',
        #   ndiv=round((length_mesh - bolt_diameter / 2) / plate_size) * 3
        # )
        mapdl.lesize("all", ndiv=5)
    # mesh density of other lines
    mapdl.csys(1)
    mapdl.lsel("s", "loc", "x", rad - 0.2, rad + 0.2)
    mapdl.lesize("all", plate_size, kforc=0)
    # excute the mesh of composite schaft
    mapdl.csys(1)
    # mapdl.vsel('s', 'loc', 'x', rad, rad_out + 1)
    mapdl.lsel("s", "length", "", thickness / 10)
    mapdl.lsel("s", "loc", "x", rad, rad + 0.2)
    mapdl.asll()
    mapdl.vsla()
    mapdl.mat("1")
    mapdl.type("1")
    mapdl.vsweep("all")
    # mapdl.eplot()
    for i in range(0, 10):
        mapdl.lsel("s", "loc", "x", rad + i + 0.5)
        mapdl.asll()
        mapdl.vsla()
        mapdl.mat("1")
        mapdl.type("1")
        mapdl.vsweep("all")
    mapdl.lsel("s", "length", "", thickness / 2 - 0.001)
    mapdl.asll()
    mapdl.vsla()
    mapdl.mat("2")
    mapdl.type("2")
    mapdl.vsweep("all")
    # mapdl.eplot()
    t = [4, 5, 4, 5, 4, 5, 4, 5, 1, 6]
    mapdl.local(11, 1)
    mapdl.esys(11)
    for i in range(0, 10):
        mapdl.csys(1)
        mapdl.esel(
            "s",
            "cent",
            "x",
            rad + i * (thickness / 10),
            rad + (i + 1) * (thickness / 10),
        )
        # mapdl.eplot()
        mapdl.emodif("all", "esys", 11)
        mapdl.emodif("all", "SECNUM", t[i])
        mapdl.eorient("all", "negx")


def mesh_bolt():
    # define the mesh desity
    mapdl.csys("1")
    mapdl.lsel("s", "length", "", 1.5 * thickness + 5)
    mapdl.lesize("all", thickness_size)
    mapdl.asel("S", "LOC", "X", rad_in - 3, rad_in - 0.1)
    mapdl.lsla()
    mapdl.lsel("r", "radius", "", bolt_diameter / 3, bolt_diameter / 1)
    mapdl.lesize("all", ndiv=em_hole / 4)
    mapdl.asel("S", "LOC", "X", rad_in - 3, rad_in - 0.1)
    mapdl.lsla()
    mapdl.lsel("u", "radius", "", bolt_diameter / 3, bolt_diameter / 1)
    mapdl.lesize("all", ndiv=em_hole / 4 * 0.6)
    # mapdl.mshape(1, '3d')
    mapdl.allsel()
    mapdl.vsweep("all")
    mapdl.allsel()
    # mapdl.eplot()


def boundary_conditons():
    # Fix the left-hand side.
    mapdl.csys("1")
    mapdl.nsel("S", "LOC", "Z", length + 8)
    # mapdl.nsel("S", "LOC", "Z", length)
    mapdl.nrotat("all")
    mapdl.d("ALL", "UZ")
    mapdl.d("ALL", "UY")
    # fix the bolts
    for i in range(0, row):
        mapdl.csys(0)
        k0 = mapdl.k("", 0, 0, 0)
        kline = mapdl.k(
            "",
            rad * np.cos(arc_cent * (i % 2 + 0.5)),
            rad * np.sin(arc_cent * (i % 2 + 0.5)),
            0,
        )
        line1 = mapdl.l(k0, kline)
        mapdl.lwplan("", line1, 0.97 - (thickness / 2) / rad)
        h = distance_between_rows * i + edge_distance
        mapdl.wpoffs(yoff=-h)
        mapdl.cswpla(30 + i, 1)
        mapdl.nsel("s", "loc", "x", 0)
        mapdl.nsel("r", "loc", "y", 0)
        mapdl.nsel("r", "loc", "z", 0)
        mapdl.csys(1)
        mapdl.nrotat("all")
        mapdl.d("all", "UX")
    # moment force
    mapdl.mp("dens", 3, 0)
    mapdl.r(2)
    mapdl.csys("1")
    mapdl.asel("S", "LOC", "Z", -8)
    mapdl.local(20, 1)
    mapdl.csys(0)
    mapdl.aatt(3, 2, 3, 20)
    mapdl.amesh("all")
    mapdl.esel("s", "type", "", 3)
    mapdl.sfe("all", 3, "pres", "", 50)
    _ = mapdl.allsel()
    # mapdl.eplot(plot_bc=True)


def post_processing():
    mapdl.result
    mapdl.post1()
    mapdl.set(1, 1)
    mapdl.rsys("solu")
    mapdl.rsys("lsys")
    mapdl.view(1, -1, -1, 1)
    mapdl.angle(1, 60)
    # get contact pressure
    mapdl.get("GR_STATUS", "GRAPH", "0", "DISPLAY")
    mapdl.show("png", "", "GR_STATUS")
    mapdl.graphics("power")
    mapdl.shade("", 1)
    mapdl.gfile(1200)
    mapdl.rgb("index", 100, 100, 100, 0)
    mapdl.rgb("index", 80, 80, 80, 13)
    mapdl.rgb("index", 60, 60, 60, 14)
    mapdl.rgb("index", 0, 0, 0, 15)
    mapdl.plnsol("cont", "press")
    mapdl.show("close", "", "GR_STATUS")
    mapdl.rename("file000", "png", "cont_press", "png")
    # get displacement
    mapdl.csys("1")
    mapdl.asel("S", "LOC", "X", rad_in - 3, rad_in - 1)
    mapdl.vsla()
    mapdl.vsel("INVE")
    mapdl.eslv()
    mapdl.nsle()
    mapdl.get("GR_STATUS", "GRAPH", "0", "DISPLAY")
    mapdl.show("png", "", "GR_STATUS")
    mapdl.graphics("power")
    mapdl.shade("", 1)
    mapdl.gfile(1200)
    mapdl.rgb("index", 100, 100, 100, 0)
    mapdl.rgb("index", 80, 80, 80, 13)
    mapdl.rgb("index", 60, 60, 60, 14)
    mapdl.rgb("index", 0, 0, 0, 15)
    mapdl.plnsol("u", "sum")
    mapdl.show("close", "", "GR_STATUS")
    mapdl.rename("file000", "png", "u_sum", "png")
    maxDisp = mapdl.get("maxDisp", "plnsol", 0, "max")
    # get metal failure index
    mapdl.csys("1")
    mapdl.asel("S", "LOC", "X", rad_in - 3, rad_in)
    mapdl.vsla()
    mapdl.eslv()
    mapdl.nsle()
    mapdl.esel("r", "cent", "x", rad_in, rad_out + 5)
    mapdl.get("GR_STATUS", "GRAPH", "0", "DISPLAY")
    mapdl.show("png", "", "GR_STATUS")
    mapdl.graphics("power")
    mapdl.shade("", 1)
    mapdl.gfile(1200)
    mapdl.rgb("index", 100, 100, 100, 0)
    mapdl.rgb("index", 80, 80, 80, 13)
    mapdl.rgb("index", 60, 60, 60, 14)
    mapdl.rgb("index", 0, 0, 0, 15)
    mapdl.plesol("s", "EQV")
    mapdl.show("close", "", "GR_STATUS")
    mapdl.rename("file000", "png", "eqv", "png")
    maxStress = mapdl.get("maxStress", "plnsol", 0, "max")
    mapdl.get("GR_STATUS", "GRAPH", "0", "DISPLAY")
    mapdl.show("png", "", "GR_STATUS")
    mapdl.graphics("power")
    mapdl.shade("", 1)
    mapdl.gfile(1200)
    mapdl.rgb("index", 100, 100, 100, 0)
    mapdl.rgb("index", 80, 80, 80, 13)
    mapdl.rgb("index", 60, 60, 60, 14)
    mapdl.rgb("index", 0, 0, 0, 15)
    mapdl.plesol("fail", "smax")
    mapdl.show("close", "", "GR_STATUS")
    mapdl.rename("file000", "png", "StressFactor", "png")
    maxStressFactor = mapdl.get("maxStressFactor", "plnsol", 0, "max")
    # get fiber failure
    mapdl.csys("1")
    mapdl.asel("S", "LOC", "X", rad_in - 3, rad_in)
    mapdl.vsla()
    mapdl.vsel("INVE")
    mapdl.eslv()
    mapdl.nsle()
    mapdl.get("GR_STATUS", "GRAPH", "0", "DISPLAY")
    mapdl.show("png", "", "GR_STATUS")
    mapdl.graphics("power")
    mapdl.shade("", 1)
    mapdl.gfile(1200)
    mapdl.rgb("index", 100, 100, 100, 0)
    mapdl.rgb("index", 80, 80, 80, 13)
    mapdl.rgb("index", 60, 60, 60, 14)
    mapdl.rgb("index", 0, 0, 0, 15)
    mapdl.fctyp("", "PFIB")
    mapdl.plesol("fail", "PFIB")
    mapdl.show("close", "", "GR_STATUS")
    mapdl.rename("file000", "png", "PFIB", "png")
    maxPFIB = mapdl.get("maxPFIB", "plnsol", 0, "max")
    # get matrix failure
    mapdl.get("GR_STATUS", "GRAPH", "0", "DISPLAY")
    mapdl.show("png", "", "GR_STATUS")
    mapdl.graphics("power")
    mapdl.shade("", 1)
    mapdl.gfile(1200)
    mapdl.rgb("index", 100, 100, 100, 0)
    mapdl.rgb("index", 80, 80, 80, 13)
    mapdl.rgb("index", 60, 60, 60, 14)
    mapdl.rgb("index", 0, 0, 0, 15)
    mapdl.fctyp("", "PMAT")
    mapdl.plesol("fail", "PMAT")
    mapdl.show("close", "", "GR_STATUS")
    mapdl.rename("file000", "png", "PMAX", "png")
    maxPMAX = mapdl.get("maxPMAX", "plnsol", 0, "max")
    mapdl.csys("1")
    mapdl.lsel("S", "LOC", "X", rad, rad_out)
    mapdl.lsel("r", "radius", "", bolt_diameter / 3, bolt_diameter / 1)
    mapdl.nsll("s", 1)
    mapdl.cm("n_cycle", "node")
    mapdl.esln()
    mapdl.cm("e_cycle", "elem")
    mapdl.csys("1")
    mapdl.asel("S", "LOC", "X", rad_in - 3, rad_in)
    mapdl.vsla()
    mapdl.vsel("INVE")
    mapdl.eslv()
    mapdl.nsle()
    mapdl.esel("u", vmin="e_cycle")
    mapdl.nsel("u", vmin="n_cycle")
    # mapdl.esel('r', 'cent', 'x', 41, 50)
    mapdl.get("GR_STATUS", "GRAPH", "0", "DISPLAY")
    mapdl.show("png", "", "GR_STATUS")
    mapdl.graphics("power")
    mapdl.shade("", 1)
    mapdl.gfile(1200)
    mapdl.rgb("index", 100, 100, 100, 0)
    mapdl.rgb("index", 80, 80, 80, 13)
    mapdl.rgb("index", 60, 60, 60, 14)
    mapdl.rgb("index", 0, 0, 0, 15)
    mapdl.fctyp("", "PFIB")
    mapdl.plesol("fail", "PFIB")
    mapdl.show("close", "", "GR_STATUS")
    mapdl.rename("file000", "png", "PFIB_", "png")
    maxPFIB_ = mapdl.get("maxPFIB_", "plnsol", 0, "max")
    mapdl.get("GR_STATUS", "GRAPH", "0", "DISPLAY")
    mapdl.show("png", "", "GR_STATUS")
    mapdl.graphics("power")
    mapdl.shade("", 1)
    mapdl.gfile(1200)
    mapdl.rgb("index", 100, 100, 100, 0)
    mapdl.rgb("index", 80, 80, 80, 13)
    mapdl.rgb("index", 60, 60, 60, 14)
    mapdl.rgb("index", 0, 0, 0, 15)
    mapdl.fctyp("", "PMAT")
    mapdl.plesol("fail", "PMAT")
    mapdl.show("close", "", "GR_STATUS")
    mapdl.rename("file000", "png", "PMAX_", "png")
    maxPMAX_ = mapdl.get("maxPMAX_", "plnsol", 0, "max")
    mass = (
        row
        * sectors
        * (np.pi * bolt_diameter**2 / 4)
        * (1.5 * thickness + 5)
        * 0.0078
        + (
            np.pi * (rad**2 - rad_in**2) * length
            - row * sectors * (np.pi * bolt_diameter**2 / 4) * (thickness / 2)
        )
        * 0.0078
        - row * sectors * (np.pi * bolt_diameter**2 / 4 * thickness) * 0.001558
    ) / 1000
    f = open("result.txt", "a")
    f.write("maxDisp=")
    f.write(str(maxDisp))
    f.write("\n")
    f.write("maxStress=")
    f.write(str(maxStress))
    f.write("\n")
    f.write("maxStressFactor=")
    f.write(str(maxStressFactor))
    f.write("\n")
    f.write("maxPFIB=")
    f.write(str(maxPFIB))
    f.write("\n")
    f.write("maxPMAX=")
    f.write(str(maxPMAX))
    f.write("\n")
    f.write("mass=")
    f.write(str(mass))
    f.write("\n")
    f.write("maxPFIB_=")
    f.write(str(maxPFIB_))
    f.write("\n")
    f.write("maxPMAX=_")
    f.write(str(maxPMAX_))
    f.close()


for row in [2]:
    for sectors in [7]:
        for bolt_diameter in [14, 16]:  # 8,10,12,
            for dbr in [0.7]:
                for ed in [2.5]:
                    try:
                        str_row = str(row)
                        str_sectors = str(sectors)
                        str_bolt_diameter = str(bolt_diameter)
                        str_dbr = str(dbr)
                        str_ed = str(ed)
                        file0 = "C:\\result\\"  # directory of computing
                        file = (
                            file0
                            + "_"
                            + str_row
                            + "_"
                            + str_sectors
                            + "_"
                            + str_bolt_diameter
                            + "_"
                            + str_dbr
                            + "_"
                            + str_ed
                        )
                        mkdir(file)
                        os.chdir(file)
                        mapdl = launch_mapdl(run_location=file, override=True)
                        mapdl.clear()
                        mapdl.prep7()
                        mapdl.units(
                            "MPA"
                        )  # MPA - International system (mm, Mg, s, °C).
                        material()
                        # parameters
                        distance_between_rows = dbr * np.pi * (2 * rad) / sectors
                        edge_distance = ed * bolt_diameter
                        # dependent parameter
                        arc_end = 360 / sectors
                        arc_cent = np.pi / (sectors)
                        length = (row - 1) * distance_between_rows + 2 * edge_distance
                        # generate a parametric shaft model
                        model(
                            row,
                            sectors,
                            bolt_diameter,
                            distance_between_rows,
                            edge_distance,
                        )
                        # make the model cyclic
                        mapdl.allsel()
                        output = mapdl.cyclic()
                        print(f"Expected Sectors: {sectors}")
                        print(output)
                        # define the mesh density
                        em_thickness = 10
                        thickness_size = thickness / em_thickness
                        em_hole = 40
                        hole_size = np.pi * bolt_diameter / em_hole
                        arc_cent = np.pi / (sectors)
                        length_mesh = min(edge_distance, arc_cent * rad / 2)
                        plate_size = length_mesh / (em_hole / 8)
                        # mesh the shafts
                        mesh_shaft()
                        # generate a parametric bolts model
                        mapdl.csys("0")
                        bolt(
                            row,
                            sectors,
                            bolt_diameter,
                            distance_between_rows,
                            edge_distance,
                        )
                        mesh_bolt()
                        # generate general contact
                        mapdl.gcgen()
                        mapdl.gcdef("", "all", "all", 10)
                        # mapdl.mp('MU', 10, 0.3)
                        boundary_conditons()
                        mapdl.run("/SOLU")
                        mapdl.antype("STATIC")
                        output = mapdl.solve()
                        print(output)
                        post_processing()
                        mapdl.exit()
                    except Exception as ex:
                        print(ex)
                        continue


# A program by Yuejie Gu and Ruihua Dong
