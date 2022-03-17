# -*- coding: utf-8 -*-
from pydantic import BaseModel
from typing import Optional

from basic import Vector, Loading, Material, Ply, Stackup, SimpleDriveShaft
from analysis import calc_strength


"parameter definition"

Auslegungsziel = 'Fertigung' #Steifigkeit, Masse, Fertigung

"Geometry"
innen_durchmesser = 171  # mm
wellen_laenge = 400  # mm

"Lasten"
# x in Längsachse der Welle, y, z out of plane
load = Last(mz= 168960, drehzahl = 136000)


force = Vector()  # N
moment = Vector(x=168960)  # Nm
Drehzahl = 6600  # U/min

# Zusammenfassung zu Array
Lasten = force.as_list() + moment.as_list() + [Drehzahl]

Sicherheit = 1.6

"Verschiebungen"

"Materialauswahl"
# benötigte Materialkarten importieren
Mat_Comp = Material("HTS40")
Mat_Comp.Ex = 240  # GPa
Mat_Comp.Ey = 70  # GPa
Mat_Comp.E1 = 145200 #MPa
Mat_Comp.E2 = 6272.7 #MPa
Mat_Comp.Ny12 = 0.28
Mat_Comp.G12 = 2634.2 #MPa

Mat_Comp.Xt = 850 #MPa
Mat_Comp.Xc = 630.93 #MPa
Mat_Comp.Yt = 55  # MPa
Mat_Comp.Yc = 200  # MPa
Mat_Comp.Smax = 120  # MPa

Mat_Comp.rho = 1.515 #g/cm^3

Mat_Nabe = Material("Stahl")
Mat_Nabe.E = 210  # GPa
Mat_Nabe.R = 1100  # MPa

Mat_Bolzen = Material("Stahl")

composite_mat = OrthotropicMaterial(240, 70, 0.28, 0.28, 2634.2, 2634.2, 1.515)
# bolzen_mat = IsotropicMaterial()

ply0 = Ply(composite_mat.get_stiffness(), 1)
ply45 = ply0.rotate(45)
stackup = Stackup([ply45, ply0, ply45])

shaft = SimpleDriveShaft(innen_durchmesser, wellen_laenge, stackup)
calc_torsionsfestigkeit(shaft, load)


"Auslegung freier Bereich"
# Übergabe der Parameter an die Funktion zur Auslegung des freien Bereichs
Auslegung_freier_Bereich = freier_Bereich(Durchmesser_Trennfuge, Bauraum_Laenge, Last, Mat_Comp,Sicherheit,Auslegungsziel)

"Auslegung Interface A"
# Übergabe der Parameter an die Funktion zur Auslegung der Interfaces
#Auslegung_Interfaces = Interfaces(Durchmesser_Trennfuge, Lasten, Mat_Comp, Mat_Nabe, Mat_Bolzen)

"Auslegung Interface B"
# Übergabe der Parameter an die Funktion zur Auslegung der Interfaces
