# -*- coding: utf-8 -*-
"""
Created on Wed Mar 23 12:18:50 2022

@author: s0166875
"""

from basic import Vector, Loading, Material, Ply, Stackup, SimpleDriveShaft


'Test für Torsionsfestigkeit nur Druckfestigkeit der Fasern'


# Material
Mat_Comp = Material("HTS40/Epoxy")
Mat_Comp.E1 = 145200 #MPa
Mat_Comp.E2 = 6272.7 #MPa
Mat_Comp.Ny12 = 0.28
Mat_Comp.G12 = 2634.2 #MPa

Mat_Comp.Xc = 630.93 #MPa

Mat_Comp.rho = 1.58 #g/cm^3

#Geometrie
r_innen = 85.5 #mm
r_innen_2 = 146 #mm

#Stackup 
"45 -45 -45 45"
t_Stackup_r1 = 10.1 #mm
t_Stackup_r2 = 3.8 #mm

#Last
Loading.mx = 168960 #Nm


#Ergebnisse
safety = 1
#Faserspannung 630.3 MPa






'Test für Beulfestigkeit und dyn. Stabilität'

#Material wie oben

#Stackup
"45 -45 -45 45"
t_Stackup1 = 15.58

"45 -45 90 0 90 -45 45"
t_Stackup2 = 11.02

#Geometrie
r_außen = 95 #mm
length = 400 #mm

#Last
Loading.mx = 168960 #Nm


#Ergebnisse
safety_Beulen = 3.6 #gilt für beide Stackups
RPM_crit_Stackup1 = 98839  #u/min
safety_dyn_Stabilitaet_Stackup1 = 15

RPM_crit_Stackup2 = 197439 #u/min
safety_dyn_Stabilitaet_Stackup2 = 29.9
