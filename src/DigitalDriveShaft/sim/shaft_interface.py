from ansys.mapdl.core import launch_mapdl
from materials import OrthotropicMaterial, IsotropicMaterial
from failure import OrthotropicStressFailure
import math




rotation_speed = 0  # Drehzahl in [1/min]
angle_vel = rotation_speed/60. * 2 * math.pi  # Winkelgeschwindigkeit in [rad/s]
nz = 4              # Zaehneanzahl
sw = 360/nz/2       # Halber Sektionswinkel in [deg]
ra = 97.5           # Aussenradius in [mm]
la = 12             # Dicke der Aussenlage in [mm]
li = 2              # Dicke der Innenlage in [mm]
zw = 0.12*sw        # Anteil des Zahnkopfs am Sektor in [deg]
zh = 6              # Zahnhoehe in [mm]
zf = 0.63*sw        # Anteil Zahnfuss in [deg]
rk = 0.5            # Radius am Zahnkopf in [mm]
rf = 0.5            # Radius am Zahnfuss in [mm]
bw = 0.8*sw         # Zahnfussbreite in [deg]

deep = 40           # Laenge des Wellenstuecks in [mm]
deep_in = 20
deep_out = 20

moment = 168000000  # Drehmoment in [Nmm]
alpha = 45          # Zahnflankenwinkel in [deg]

d_nabe = 7
ri_nabe = ra - la - li - zh - d_nabe  # Radius der Nabe in [mm]

sb = ra - la - li
sa = ra - la - li - zh / 2

wb = (180 - alpha) * math.pi / 180
x = sa / sb * math.sin(wb)
wa = math.asin(x) * 180/ math.pi
wb = wb * 180 / math.pi
fw = 180 - wa - wb
fw = bw-fw
es = 0.265*3

mapdl = launch_mapdl(loglevel="WARNING")
mapdl.finish()
mapdl.run("/clear")
mapdl.run("/facet,fine")  # feinere Aufteilung der Facetten

mapdl.prep7()
CFK_UD_HTS40 = OrthotropicMaterial(E_l=138e3, E_t=8.5e3,
                                   nu_lt=0.29, nu_tt=0.31,
                                   G_lt=4.5e3, G_tt=3.24e3,
                                   density=1.5e-9)
cfk_failure = OrthotropicStressFailure(tens_l=1602, tens_t=25, shear_lt=40, shear_tt=40, compr_l=-800, compr_t=-115)

mat1_id = 201
mat2_id = 202
CFK_UD_HTS40.add_to_mapdl(mapdl, mat1_id)
cfk_failure.add_to_mapdl(mapdl, mat1_id)

CFK_UD_HTS40.add_to_mapdl(mapdl, mat2_id)
cfk_failure.add_to_mapdl(mapdl, mat2_id)

# Materialdefinition Nabe
nabe_mat_id = 204
steel = IsotropicMaterial(Em=210e3, nu=0.3, density=7.8e-9)
steel.add_to_mapdl(mapdl, nabe_mat_id)

mapdl.k(100, 0, 0)  # Wellenmittelpunkt
mapdl.k(101, 0, ra)  # Punkt auf Aussenradius
mapdl.circle(100, "", "", 101, sw, 1)  # Bogen um K100, ra von K101 um Winkel sw aus
mapdl.k(102, 0, (ra-la))
mapdl.circle(100, "", "", 102, sw, 1)
mapdl.k(103, 0, (ra-la-li))  # Kreisbogen des Zahnfusses
mapdl.circle(100, "", "", 103, sw)
mapdl.k(104, 0, (ra-la-li-zh/2))  # Kreisbogen des Zahnfusses
mapdl.circle(100, "", "", 104, sw)
mapdl.k(105, 0, (ra-la-li-zh))  # Kreisbogen des Zahnfusses
mapdl.circle(100, "", "", 105, sw)
mapdl.k(106, 0, (ra-la-li))  # Kreisbogen des Zahnfusses
mapdl.circle(100, "", "", 106, bw)
mapdl.k(107, 0, (ra-la-li-zh/2))  # Kreisbogen des Zahnfusses
mapdl.circle(100, "", "", 107, fw)
mapdl.l(1, 3)
mapdl.l(2, 4)
mapdl.l(4, 6)
mapdl.l(12, 14)
mapdl.lextnd(11, 14, ra)
mapdl.lsbl(5, 12)
mapdl.ldele(11)
mapdl.ldele(14)
mapdl.ldele(7)
mapdl.ldele(4)
mapdl.l(12, 16)
mapdl.kdele(14)
mapdl.ldele(8)
mapdl.cskp(11, 0, 12, 16, 1)
mapdl.lgen(2, 4, "", "", "", li, "", "", 0)
mapdl.csys(0)
mapdl.k(108, 0, (ra-zh-la))
mapdl.circle(100, "", "", 108, bw)
mapdl.lextnd(5, 14, li, 0)
mapdl.ldele(6)
mapdl.boptn("keep", "yes")
mapdl.lsbl(5, 2)
mapdl.ldele(6)
mapdl.ldele(5)
mapdl.lsbl(8, 7)
mapdl.lsbl(7, 8)
mapdl.ldele(5)
mapdl.ldele(8)
mapdl.ldele(12)
mapdl.ldele(7)
mapdl.lsbl(3, 4)
mapdl.ldele(5)
mapdl.ldele(3)
mapdl.l(19, 16)
mapdl.l(12, 20)
mapdl.lsbl(3, 5)
mapdl.csys(11)
mapdl.lgen(2, 4, "", "", "", li/2, "", "", 0)
mapdl.csys(0)
mapdl.cskp(12, 0, 22, 24, 1)
mapdl.k(109, 0, li)
mapdl.k(110, 0, -li)
mapdl.csys(0)
mapdl.l(109, 110)
mapdl.ldele(8)
mapdl.ldele(14)
mapdl.ldele(12)
mapdl.ldele(5)
mapdl.ldele(3)
mapdl.lsbl(6, 15)
mapdl.lsbl(4, 15)
mapdl.lsbl(15, 6)
mapdl.ldele(14)
mapdl.ldele(15)
mapdl.ldele(6)
mapdl.nummrg("kp")
mapdl.lsbl(16, 4)
mapdl.ldele(4)
mapdl.ldele(14)
mapdl.ldele(16)
mapdl.lsbl(2, 3)
mapdl.nummrg("kp")
mapdl.ldele(2)
mapdl.ldele(4)
mapdl.lfillt(12, 13, rk+0.5)
mapdl.lfillt(11, 5, rk)
mapdl.lfillt(7, 8, rf)
mapdl.lfillt(14, 3, rf*1.0)
mapdl.lcomb(14, 16, 0)
mapdl.lcomb(7, 15, 0)
mapdl.lcomb(13, 2, 0)
mapdl.lcomb(11, 4, 0)
mapdl.lcomb(7, 8, 0)
mapdl.lcomb(14, 3, 0)
mapdl.lcomb(2, 12, 0)
mapdl.lcomb(4, 5, 0)
mapdl.k(111, 0, ra-(1.001*la))
mapdl.circle(100, "", "", 111, bw)
mapdl.lsbl(3, 5)
mapdl.lsbl(5, 3)
mapdl.ldele(13)
mapdl.ldele(5)
mapdl.nummrg("kp")
mapdl.lcomb(8, 12, 1)
mapdl.ldele(8)
mapdl.lcomb(11, 4)
mapdl.ldele(11)
mapdl.nummrg("kp")
mapdl.run("lsym, x, all")
mapdl.nummrg("kp")
mapdl.lcomb(1, 11, 0)
mapdl.l(13, 17)
mapdl.lcomb(5, 16, 1)
mapdl.ldele(5)
mapdl.ldele(16)
mapdl.lcomb(4, 15, 1)
mapdl.ldele(4)
mapdl.ldele(15)
mapdl.lcomb(2, 13, 1)
mapdl.ldele(2)
mapdl.ldele(13)
mapdl.al(1, 20, 23, 9)
mapdl.al(10, 3, 6, 7)
mapdl.al(5, 17, 4, 6)
mapdl.al(14, 21, 18, 17)
mapdl.al(12, 11, 8)
mapdl.al(11, 22, 19)
mapdl.agen(2, 1, "", "", "", "", "", "", 0)
mapdl.agen(2, 2, "", "", "", "", "", "", 0)
mapdl.agen(2, 3, "", "", "", "", "", "", 0)
mapdl.agen(2, 4, "", "", "", "", "", "", 0)
mapdl.agen(2, 5, "", "", "", "", "", "", 0)
mapdl.agen(2, 6, "", "", "", "", "", "", 0)
mapdl.vext(7, "", "", 0, 0, deep)
mapdl.vext(8, "", "", 0, 0, deep)
mapdl.vext(9, "", "", 0, 0, deep)
mapdl.vext(10, "", "", 0, 0, deep)
mapdl.vext(11, "", "", 0, 0, deep)
mapdl.vext(12, "", "", 0, 0, deep)
mapdl.vsel("s", "volu", "", 1)
mapdl.cm("outer", "volu")
mapdl.et(101, 186)
mapdl.keyopt(101, 2, 0)  # red int
mapdl.keyopt(101, 3, 1)  # layered
mapdl.keyopt(101, 8, 1)  # all layers
mapdl.esize(6 * es)
mapdl.lesize(45, "", "", 3)
# vsweep,1,5,3,0
mapdl.veorient(1, "kp", 56, 55)
mapdl.vmesh(1)

# === Aussenlage ===
mapdl.sectype(101, "shell", "", "aussen")
mapdl.secdata(la/4, 202, 45, 5)  # 5 Integrationspunkte
mapdl.secdata(la/4, 202, 45, 5)
mapdl.esel("s", "ename", "", "outer")
mapdl.emodif("all", "sec", 101)
mapdl.vsel("s", "volu", "", 2)
mapdl.cm("inner", "volu")
mapdl.et(102, 186)
mapdl.keyopt(102, 2, 0)  # red int
mapdl.keyopt(102, 3, 1)  # layered
mapdl.keyopt(102, 8, 1)  # all layers
mapdl.type(102)
mapdl.esize(es)
mapdl.lesize(50, "", "", 2)
# vsweep,2,11,11,0
mapdl.veorient(2, "kp", 60, 61)
mapdl.vmesh(2)

# === Innenlage ===
mapdl.sectype(102, "shell", "", "aussen")
mapdl.secdata(li/2, 202, 45, 5)  # 5 Integrationspunkte
mapdl.esel("s", "ename", "", "inner")
mapdl.emodif("all", "sec", 102)
mapdl.allsel()
mapdl.vsel("s", "volu", "", 3)
mapdl.cm("inner", "volu")
mapdl.et(102, 186)
mapdl.keyopt(102, 2, 0)  # red int
mapdl.keyopt(102, 3, 1)  # layered
mapdl.keyopt(102, 8, 1)  # all layers
mapdl.type(102)
mapdl.esize(es)
mapdl.lesize(59, "", "", 2)
# vsweep,2,11,11,0
mapdl.veorient(3, "kp", 64, 63)
mapdl.vmesh(3)

# === Innenlage ===
mapdl.sectype(102, "shell", "", "aussen")
mapdl.secdata(li/2, 202, 45, 5)  # 5 Integrationspunkte
mapdl.esel("s", "ename", "", "inner")
mapdl.emodif("all", "sec", 102)
mapdl.allsel()
mapdl.vsel("s", "volu", "", 4)
mapdl.cm("inner", "volu")
mapdl.et(102, 186)
mapdl.keyopt(102, 2, 0)  # red int
mapdl.keyopt(102, 3, 1)  # layered
mapdl.keyopt(102, 8, 1)  # all layers
mapdl.type(102)
mapdl.esize(es)
mapdl.lesize(69, "", "", 2)
# vsweep,2,11,11,0
mapdl.veorient(4, "kp", 69, 66)
mapdl.vmesh(4)

# === Innenlage ===
mapdl.sectype(102, "shell", "", "aussen")
mapdl.secdata(li/2, 202, 45, 5)  # 5 Integrationspunkte
mapdl.esel("s", "ename", "", "inner")
mapdl.emodif("all", "sec", 102)
mapdl.allsel()
mapdl.vsel("s", "volu", "", 5, 6, 1)
mapdl.cm("core", "volu")
mapdl.et(103, 186)
mapdl.keyopt(103, 3, 1)
mapdl.type(103)
mapdl.esize(1.5*es)
mapdl.veorient(5, "area", 34)
mapdl.vmesh(5)
mapdl.veorient(6, "area", 38)
mapdl.vmesh(6)

# === Kern ===
mapdl.esel("s", "ename", "", "core")
mapdl.emodif("all", "mat", mat1_id)
mapdl.emodif("all", "sec", 203)
mapdl.allsel()
mapdl.esel("s", "type", "", 102)
mapdl.nsle("s", "all")
mapdl.nummrg("node")
mapdl.allsel()
mapdl.esel("s", "type", "", 103)
mapdl.nsle("s", "all")
mapdl.nummrg("node")
mapdl.allsel()
mapdl.k(111, 0, 0, -deep_out)
mapdl.lsel("s", "line", "", 18)
mapdl.lsel("a", "line", "", 7)
mapdl.lsel("a", "line", "", 4)
mapdl.lgen(2, "all", "", "", "", "", -deep_out, "", 1, 0)
mapdl.run("alls")
# rins=ra-2*(la+li+zh)
# k,112,0,rins,-deep/4
# k,112,0,ra-la-li-zh*3,-deepout
mapdl.k(112, 0, ri_nabe, -deep_out)
mapdl.circle(111, "", "", 112, sw)
mapdl.run("lsym, x, 89")
mapdl.lglue(89, 90)
mapdl.ldele(90)
mapdl.l(83, 79)
mapdl.l(81, 78)
mapdl.al(90, 88, 86, 87, 92, 89, 91)
mapdl.vext(41, "", "", 0, 0, deep_in + deep_out)
mapdl.allsel()
mapdl.vsel("s", "volu", "", 7)
mapdl.cm("insert", "volu")
mapdl.et(104, 187)
# keyopt,102,3,1
mapdl.type(104)
mapdl.aesize(45, es)
mapdl.aesize(44, es)
mapdl.aesize(46, es)
mapdl.aesize(41, es*3)
mapdl.esize(es*6)
mapdl.mshkey("mapped")
mapdl.vmesh(7)
mapdl.esel("s", "ename", "", "insert")
mapdl.emodif("all", "mat", 204)

# ==============================================================================
# Kontakte
mapdl.mp("MU", 201, "")
mapdl.mat(201)
mapdl.mp("EMIS", 201, 7.88860905221e-031)
mapdl.r(3)
mapdl.real(3)
mapdl.et(105, 170)
mapdl.et(106, 174)
mapdl.r(3, "", "", 1.0, 0.1, 0, "")
mapdl.rmore("", "", 1.0E20, 0.0, 1.0, "")
mapdl.rmore(0.0, 0, 1.0, "", 1.0, 0.5)
mapdl.rmore(0, 1.0, 1.0, 0.0, "", 1.0)
mapdl.keyopt(106, 4, 0)
mapdl.keyopt(106, 5, 0)
mapdl.keyopt(106, 7, 0)
mapdl.keyopt(106, 8, 0)
mapdl.keyopt(106, 9, 0)
mapdl.keyopt(106, 10, 2)
mapdl.keyopt(106, 11, 0)
mapdl.keyopt(106, 12, 6)
mapdl.keyopt(106, 2, 0)
mapdl.keyopt(105, 5, 0)

# Generate the target surface
mapdl.asel("S", "", "", 16)
mapdl.type(105)
mapdl.nsla("S", 1)
mapdl.esln("S", 0)
mapdl.esll("U")
mapdl.esel("U", "ENAME", "", 188, 189)
mapdl.nsle("A", "CT2")
mapdl.esurf()

# Generate the contact surface
mapdl.asel("S", "", "", 34)
mapdl.asel("a", "", "", 40)
mapdl.asel("a", "", "", 22)
mapdl.asel("a", "", "", 29)
mapdl.type(106)
mapdl.nsla("S", 1)
mapdl.esln("S", 0)
mapdl.nsle("A", "CT2")  # CZMESH patch (fsk qt-40109 8/2008)
mapdl.esurf()
mapdl.allsel()
mapdl.mp("MU", 201, 0)
mapdl.mat(201)
mapdl.mp("EMIS", 201, 7.88860905221e-031)
mapdl.r(4)
mapdl.real(4)
mapdl.et(107, 170)
mapdl.et(108, 174)
mapdl.r(4, "", "", 1.0, 0.1, 0, "")
mapdl.rmore("", "", 1.0E20, 0.0, 1.0, "")
mapdl.rmore(0.0, 0, 1.0, "", 1.0, 0.5)
mapdl.rmore(0, 1.0, 1.0, 0.0, "", 1.0)
mapdl.keyopt(108, 4, 0)
mapdl.keyopt(108, 5, 0)
mapdl.keyopt(108, 7, 0)
mapdl.keyopt(108, 8, 0)
mapdl.keyopt(108, 9, 0)
mapdl.keyopt(108, 10, 2)
mapdl.keyopt(108, 11, 0)
mapdl.keyopt(108, 12, 6)
mapdl.keyopt(108, 2, 1)
mapdl.keyopt(107, 5, 0)

# Generate the target surface
mapdl.asel("S", "", "", 35)
mapdl.asel("a", "", "", 39)
mapdl.type(107)
mapdl.nsla("S", 1)
mapdl.esln("S", 0)
mapdl.esll("U")
mapdl.esel("U", "ENAME", "", 188, 189)
mapdl.nsle("A", "CT2")
mapdl.esurf()

# Generate the contact surface
mapdl.asel("S", "", "", 22)
mapdl.asel("a", "", "", 24)
mapdl.asel("a", "", "", 29)
mapdl.type(108)
mapdl.nsla("S", 1)
mapdl.esln("S", 0)
mapdl.nsle("A", "CT2")  # CZMESH patch (fsk qt-40109 8/2008)
mapdl.esurf()
mapdl.allsel()
mapdl.mp("MU", 201, 0.1)
mapdl.mat(201)
mapdl.mp("EMIS", 201, 7.88860905221e-031)
mapdl.r(7)
mapdl.real(7)
mapdl.et(109, 170)
mapdl.et(110, 174)
mapdl.r(7, "", "", 1.0, 0.1, 0, "")
mapdl.rmore("", "", 1.0E20, 0.0, 1.0, "")
mapdl.rmore(0.0, 0, 1.0, "", 1.0, 0.5)
mapdl.rmore(0, 1.0, 1.0, 0.0, "", 1.0)
mapdl.keyopt(110, 4, 0)
mapdl.keyopt(110, 5, 0)
mapdl.keyopt(110, 7, 0)
mapdl.keyopt(110, 8, 0)
mapdl.keyopt(110, 9, 0)
mapdl.keyopt(110, 10, 2)
mapdl.keyopt(110, 11, 0)
mapdl.keyopt(110, 12, 0)
mapdl.keyopt(110, 2, 1)
mapdl.keyopt(109, 5, 0)

# Generate the target surface
mapdl.asel("S", "", "", 20)
mapdl.asel("a", "", "", 26)
mapdl.asel("a", "", "", 31)
mapdl.type(109)
mapdl.nsla("S", 1)
mapdl.esln("S", 0)
mapdl.esll("U")
mapdl.esel("U", "ENAME", "", 188, 189)
mapdl.nsle("A", "CT2")
mapdl.esurf()

# Generate the contact surface
mapdl.asel("S", "", "", 44, 46, 1)
mapdl.type(110)
mapdl.nsla("S", 1)
mapdl.esln("S", 0)
mapdl.nsle("A", "CT2")  # CZMESH patch (fsk qt-40109 8/2008)
mapdl.esurf()
mapdl.allsel()

# Define surface-based constraint type of pair
mapdl.mat(201)
mapdl.r(6)
mapdl.real(6)
mapdl.et(111, 170)
mapdl.et(112, 174)
mapdl.keyopt(112, 12, 5)
mapdl.keyopt(112, 4, 2)
mapdl.keyopt(112, 2, 2)
mapdl.keyopt(111, 2, 0)
mapdl.keyopt(111, 4, 111111)
mapdl.type(111)
# Create a pilot node
mapdl.ksel("S", "", "", 111)
mapdl.katt(-1, 6, 111, -1)
mapdl.kmesh(111)
# Generate the contact surface
mapdl.asel("S", "", "", 41)
mapdl.cm("_CONTACT", "AREA")
mapdl.type(112)
mapdl.nsla("S", 0)
mapdl.esln("S", 0)
mapdl.nsle("A", "CT2")  # CZMESH patch (fsk qt-40109 8/2008)
mapdl.esurf()
mapdl.allsel()
mapdl.csys(2)
mapdl.asel("s", "area", "", 13)
mapdl.asel("a", "area", "", 33)
mapdl.asel("a", "area", "", 37)
mapdl.asel("a", "area", "", 18)
mapdl.asel("a", "area", "", 23)
mapdl.asel("a", "area", "", 28)
mapdl.nsla("s", 1)
mapdl.nrotat("all")

mapdl.d("all", "uz", 0)
mapdl.d("all", "uy", 0)
mapdl.csys(0)
mapdl.nsel("s", "loc", "y", 0)
mapdl.d("all", "uz", 0)
mapdl.f("all", "mz", moment / nz)
mapdl.allsel()
mapdl.cyclic()

# Plots before Solve
mapdl.eplot()

mapdl.run("/solu")
mapdl.run("solcontrol,on")
mapdl.nlgeom("on")
# nsubst,5
mapdl.outres("all")
mapdl.solve()
mapdl.post_processing.nodal_displacement()

mapdl.exit()
