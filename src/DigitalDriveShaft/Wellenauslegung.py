# -*- coding: utf-8 -*-
from freier_Bereich import freier_Bereich
from load import Vector


# Definition der Materialklasse
class Material(object):
    def __init__(self, materialname):
        self.Materialname = materialname


"Parameterdefinition"

"Geometrie"
Durchmesser_Trennfuge = 171  # mm
Bauraum_Laenge = 400  # mm

"Lasten"
# x in Längsachse der Welle, y, z out of plane
force = Vector()  # N
moment = Vector(x=168960)  # Nm
Drehzahl = 6600  # U/min

# Zusammenfassung zu Array
Lasten = force.as_list() + moment.as_list() + [Drehzahl]

"Verschiebungen"

"Materialauswahl"
# benötigte Materialkarten importieren
Mat_Comp = Material("HTS40")
Mat_Comp.Ex = 240  # GPa
Mat_Comp.Ey = 70  # GPa

Mat_Nabe = Material("Stahl")
Mat_Nabe.E = 210  # GPa
Mat_Nabe.R = 1100  # MPa

Mat_Bolzen = Material("Stahl")

"Auslegung freier Bereich"
# Übergabe der Parameter an die Funktion zur Auslegung des freien Bereichs
Auslegung_freier_Bereich = freier_Bereich(Durchmesser_Trennfuge, Lasten, Mat_Comp)

"Auslegung Interface A"
# Übergabe der Parameter an die Funktion zur Auslegung der Interfaces
Auslegung_Interfaces = Interfaces(Durchmesser_Trennfuge, Lasten, Mat_Comp, Mat_Nabe, Mat_Bolzen)

"Auslegung Interface B"
# Übergabe der Parameter an die Funktion zur Auslegung der Interfaces
