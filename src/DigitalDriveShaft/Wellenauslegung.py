# -*- coding: utf-8 -*-
"""
Created on Tue Feb  8 15:46:13 2022

@author: s0166875
"""
from freier_Bereich import freier_Bereich

#Definition der Materialklasse
class Material(object):
    def __init__(self, materialname):
        self.Materialname = materialname

"Parameterdefinition"

"Geometrie"
Durchmesser_Trennfuge = 171 #mm
Bauraum_Laenge = 400 #mm

"Lasten"
# x in Längsachse der Welle, y, z out of plane
Fx = 0      #N
Fy = 0      #N
Fz = 0      #N
Mx = 168960    #Nm
My = 0      #Nm
Mz = 0      #Nm

Drehzahl = 6600 #U/min

#Zusammenfassung zu Array
Lasten = [Fx, Fy, Fz, Mx, My, Mz, Drehzahl]

"Verschiebungen"


"Materialauswahl"
#benötigte Materialkarten importieren
Mat_Comp = Material("HTS40")
Mat_Comp.Ex = 240 #GPa
Mat_Comp.Ey = 70 #GPa

Mat_Nabe = Material("Stahl")
Mat_Nabe.E = 210 #GPa
Mat_Nabe.R = 1100 #MPa

Mat_Bolzen = Material("Stahl")


"Auslegung freier Bereich"
#Übergabe der Parameter an die Funktion zur Auslegung des freien Bereichs
Auslegung_freier_Bereich = freier_Bereich(Durchmesser_Trennfuge, Lasten, Mat_Comp)



"Auslegung Interface A"
#Übergabe der Parameter an die Funktion zur Auslegung der Interfaces
Auslegung_Interfaces = Interfaces(Durchmesser_Trennfuge, Lasten, Mat_Comp, Mat_Nabe, Mat_Bolzen)


"Auslegung Interface B"
#Übergabe der Parameter an die Funktion zur Auslegung der Interfaces