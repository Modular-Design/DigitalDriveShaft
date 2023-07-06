from ansys.mapdl.core import launch_mapdl
import numpy as np

"""
! /EXIT,MODEL
/BATCH
/COM,ANSYS RELEASE 2022 R1           BUILD 22.1      UP20211129       10:00:32
/input,menust,tmp,''
/GRA,POWER
/GST,ON
/PLO,INFO,3
/GRO,CURL,ON
/CPLANE,1
/REPLOT,RESIZE
WPSTYLE,,,,,,,,0
/PREP7
!*
ET,1,SHELL181
!*
KEYOPT,1,1,0
KEYOPT,1,3,0
KEYOPT,1,5,0
KEYOPT,1,8,1
KEYOPT,1,9,0
KEYOPT,1,10,0
KEYOPT,1,11,0
!*
!*
TB,ANEL,1,1,21,0
TBTEMP,0
TBDATA,,11,12,13,14,15,16
TBDATA,,22,23,24,25,26,33
TBDATA,,34,35,36,44,45,46
TBDATA,,55,56,66,,,
MPTEMP,,,,,,,,
MPTEMP,1,0
MPDATA,EX,2,,1
MPDATA,PRXY,2,,2
MPTEMP,,,,,,,,
MPTEMP,1,0
MPDATA,DENS,2,,3
sect,1,shell,,mid-plane
secdata, 1,1,10,3
secdata, 2,2,20,5
secoffset,MID
seccontrol,,,, , , ,
sect,2,shell,,user-input
secdata, 1,1,0.0,3
secdata, 1,1,0.0,3
secdata, 1,1,0.0,3
secoffset,USER,42
seccontrol,,,, , , ,
sect,3,shell,,top-plane
secdata, 0.0,1,0.0,3
secoffset,TOP
seccontrol,,,, , , ,
/REPLOT,RESIZE
/REPLOT,RESIZE
/REPLOT,RESIZE
sect,4,shell,,bottom-plane
secdata, 0.0,1,0.0,3
secoffset,BOT
seccontrol,,,, , , ,
/REPLOT,RESIZE
RECTNG,-0.02,0.02,-0.02,0.02,
MSHAPE,0,2D
MSHKEY,0
!*
CM,_Y,AREA
ASEL, , , ,       1
CM,_Y1,AREA
CHKMSH,'AREA'
CMSEL,S,_Y
!*
AMESH,_Y1
!*
CMDELE,_Y
CMDELE,_Y1
CMDELE,_Y2
!*
/UI,MESH,OFF
!*
/SHRINK,0
/ESHAPE,1.0
/EFACET,1
/RATIO,1,1,1
/CFORMAT,32,0
/REPLOT
"""


mapdl = launch_mapdl(mode="grpc")
mapdl.finish()
mapdl.run("/clear")
mapdl.run("/facet,fine")  # feinere Aufteilung der Facetten

mapdl.prep7()


mapdl.csys(
    1
)  # activate  global cylindrical coordinate system (now: x = R, y = Theta, z = Z)

start_id = 1

d_i = 0.2
dphi = 0.1
arc = 90
narc = 30  # segments on arc
z = np.arange(0, np.pi + dphi, dphi)
r = np.sin(z)  # TIPP: use fourier transformation later
theta = 0


node_start = start_id
for i in range(len(z)):
    mapdl.k(node_start + i, r[i] + d_i, theta, z[i])

node_end = start_id + (len(z) - 1)


for i in range(len(z) - 1):
    mapdl.l(node_start + i, node_start + i + 1)

mapdl.lplot()

# add axis keepoints
k_origin = node_end + 1
mapdl.k(k_origin, 0, 0, 0)

k_end = k_origin + 1
mapdl.k(k_end, 0, 0, 1)

mapdl.arotat(
    nl1="ALL",
    pax1=k_origin,
    pax2=k_end,
    arc=arc,
    nseg=narc,
)

mapdl.lplot()
mapdl.amesh("ALL")
mapdl.eplot()
mapdl.exit()
# """
