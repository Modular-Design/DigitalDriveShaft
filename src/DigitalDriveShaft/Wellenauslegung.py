# -*- coding: utf-8 -*-
from freier_Bereich import freier_Bereich
from load import Vector

# Import local packages.
from abd import abdcal, deformation, failure, homogenization


# Definition der Materialklasse
class Material(object):
    def __init__(self, materialname):
        self.Materialname = materialname

#Definition der Materialklasse
class Last(object):
    pass


"Parameterdefinition"

Steifigkeit = False

"Geometrie"
Durchmesser_Trennfuge = 171  # mm
Bauraum_Laenge = 400  # mm

"Lasten"
# x in Längsachse der Welle, y, z out of plane
Last.Fx = 0      #N
Last.Fy = 0      #N
Last.Fz = 0      #N
Last.Mx = 168960    #Nm
Last.My = 0      #Nm
Last.Mz = 0      #Nm

Last.Drehzahl = 6600 #U/min


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
Mat_Comp.tau_zul = 630.93 #MPa
Mat_Comp.rho = 1.515 #g/cm^3

Mat_Nabe = Material("Stahl")
Mat_Nabe.E = 210  # GPa
Mat_Nabe.R = 1100  # MPa

Mat_Bolzen = Material("Stahl")




###############################################################################
# Ply Properties                                                              #
###############################################################################


# List the other properties of the ply.
t = 1  # mm

# Calculate the ply stiffness matricess matrix.
Q = abdcal.QPlaneStress(Mat_Comp.E1, Mat_Comp.E2, Mat_Comp.Ny12, Mat_Comp.G12)


###############################################################################
# Laminate Properites                                                         #
###############################################################################
# Define the stacking sequence.
angles_deg = [45,-45,-45,45]
thickness = [t] * len(angles_deg)
Q = [Q] * len(angles_deg)

# Calculate the ABD matrix and its inverse.
abd = abdcal.abd(Q, angles_deg, thickness)
abd_inv = abdcal.matrix_inverse(abd)

"Auslegung freier Bereich"
# Übergabe der Parameter an die Funktion zur Auslegung des freien Bereichs
Auslegung_freier_Bereich = freier_Bereich(Durchmesser_Trennfuge, Bauraum_Laenge, Last, Mat_Comp,Sicherheit,Steifigkeit)

"Auslegung Interface A"
# Übergabe der Parameter an die Funktion zur Auslegung der Interfaces
#Auslegung_Interfaces = Interfaces(Durchmesser_Trennfuge, Lasten, Mat_Comp, Mat_Nabe, Mat_Bolzen)

"Auslegung Interface B"
# Übergabe der Parameter an die Funktion zur Auslegung der Interfaces
