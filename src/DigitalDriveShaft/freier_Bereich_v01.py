# -*- coding: utf-8 -*-
import numpy as np
from abd import abdcal, deformation, failure, homogenization
from typing import Optional, Final

"""
(0) x0
(1) eval -> Sicherheiten
(2) goal?
    (2.n.0) xi+1
    (2.n.1) -> (1)
"""



def Torsionsfestigkeit(D_Trennfuge, L_Welle, Last, Mat_Welle, Layup, Sicherheit: Optional[float] = 1.0):
    """
    Generates the optimal stackup and drive shaft diameter.

    Parameters
    ----------
    D_Trennfuge
    L_Welle
    Last
    Mat_Welle
    Sicherheit
    

    Returns
    -------
    returns stackup and drive_shaft diameter
    """
    
    
    "Festigkeitsberechnung"
    
# =============================================================================
#     Layup einlesen und ABD-Matrix berechnen
# =============================================================================
    #Layupinformationen auslesen    
    angles_deg
    thickness
    
    Laminatdicke = sum(thickness)
    D_Mittelflaeche = D_Trennfuge + Laminatdicke
    U_Welle = np.pi * D_Mittelflaeche
    
    
    # Calculate the ply stiffness matricess matrix
    Q_Einzel = abdcal.QPlaneStress(Mat_Welle.E1, Mat_Welle.E2, Mat_Welle.Ny12, Mat_Welle.G12)
    
    Q = [Q_Einzel] * len(angles_deg)
    # Calculate the ABD matrix and its inverse.
    abd = abdcal.abd(Q, angles_deg, thickness)
    abd_inv = abdcal.matrix_inverse(abd)


    ###############################################################################
    # Applied Running Loads                                                       #
    ###############################################################################
    nx = Last.Fx/U_Welle    #N/mm
    ny = 0                  #N/mm
    nxy = Last.Mx/D_Mittelflaeche/2/U_Welle     #N/mm #ggf. Ergänzung von Fy und Fz komponenten
    mx = 0                  #N
    my = np.sqrt((Last.My/1000/D_Mittelflaeche/2)**2 + (Last.Mz/1000/D_Mittelflaeche/2)**2)     #N
    mxy = 0                 #N
    
    # Calculate the deformation caused by a given running load.
    NM = np.matrix([nx, ny, nxy, mx, my, mxy]).T  # MPa/mm and MPa*mm/mm
    deformed = deformation.load_applied(abd_inv, NM)

    
    stress = deformation.ply_stress(deformed, Q, angles_deg, thickness, plotting=True)
    FI_Torsionsbruch = failure.max_stress(stress, Mat_Welle.Xt, Mat_Welle.Xc, Mat_Welle.Yt, Mat_Welle.Yc, Mat_Welle.Smax)
    
    
    
    
    # Abschätzung der Wandstärke mit Nabendurchmesser
# =============================================================================
#     t_Diagonallagen = Sicherheit * Last.Mx * 1000 / (2 * np.pi * (D_Trennfuge / 2) ** 2 * Mat_Welle.tau_zul)
# 
#     D_Welle_Außen = D_Trennfuge + 2 * t_Diagonallagen
#     # Spannungsberechnung nach Excel von Sebastian
#     tau_vorh = Last.Mx * 1000 / (2 * np.pi * (D_Welle_Außen / 2) ** 2 * t_Diagonallagen)
#     Sicherheit_Torsionsbruch = Mat_Welle.tau_zul / tau_vorh
# =============================================================================

    # print(Sicherheit *tau_vorh/Mat_Welle.tau_zul)

    
    print(f'Sicherheit gegen Torsionsbruch: {round(FI_Torsionsbruch, 1)}')

    return FI_Torsionsbruch

def Beulfestigkeit(D_Trennfuge, L_Welle, Last, Mat_Welle, Layup, Sicherheit: Optional[float] = 1.0):
    "Beulrechnung"
    
    # =============================================================================
    #     Layup einlesen und ABD-Matrix berechnen
    # =============================================================================
    #Layupinformationen auslesen    
    angles_deg
    thickness
    
    Laminatdicke = sum(thickness)
    D_Mittelflaeche = D_Trennfuge + Laminatdicke
    D_Welle_Außen = D_Trennfuge + 2*Laminatdicke
    U_Welle = np.pi * D_Mittelflaeche
    
    
    # Calculate the ply stiffness matricess matrix
    Q_Einzel = abdcal.QPlaneStress(Mat_Welle.E1, Mat_Welle.E2, Mat_Welle.Ny12, Mat_Welle.G12)
    
    Q = [Q_Einzel] * len(angles_deg)
    # Calculate the ABD matrix and its inverse.
    abd = abdcal.abd(Q, angles_deg, thickness)
    abd_inv = abdcal.matrix_inverse(abd)
    
    
    k_s = 0.925  # Beiwert für gelenkige Lagerung
    k_l = 0.77  # Beiwert für Imperfektionsanfälligkeit
    E_Axial = abd[0, 0] / Laminatdicke  # MPa #20000 bei Sebastian
    E_Umfang = abd[1, 1] / Laminatdicke  # MPa #20000 bei Sebastian
    # Beulmomentberechnung nach Excel von Sebastian
    Beulmoment = k_s * k_l * np.pi ** 3 / 6 * (D_Welle_Außen / 2) ** (5 / 4) * Laminatdicke ** (9 / 4) / np.sqrt(
        L_Welle) * E_Axial ** (3 / 8) * (E_Umfang / (1 - Mat_Welle.Ny12 ** 2)) ** (5 / 8) / 1000
    Sicherheit_TB = Beulmoment / Last.Mx
    print(f'Sicherheit gegen Torsionsbeulen:  {str(round(Sicherheit_TB, 1))}')


    return Sicherheit_TB




def Dynamische_Stabilitaet(D_Trennfuge, L_Welle, Last, Mat_Welle, Layup, Sicherheit: Optional[float] = 1.0):
    "Berechnung Biegekritische Drehzahl"

    # Formel für Berechnung von Biegekritischer Drehzahl aus Sebastians Excel
    Drehzahl_krit = 60 / 2 * np.pi / np.sqrt(8) * D_Welle_Außen / L_Welle ** 2 * np.sqrt(
        1000 ** 3 * E_Axial / (Mat_Welle.rho))  # u/min
    Sicherheit_Drehzahl = Drehzahl_krit / Last.Drehzahl
    print(f"Biegekritische Drehzahl: {round(Drehzahl_krit, 1)}")
    print('Sicherheit gegen Instabilität: ' + str(round(Sicherheit_Drehzahl, 1)))

    if Sicherheit_Drehzahl < Sicherheit:
        while abs(Last.Drehzahl * Sicherheit - Drehzahl_krit) > 0.1:
            # iterative Anpassung der Umfangslagen auf Basis des Ergebnisses
            t_Axiallagen = t_Axiallagen + ((Sicherheit * Last.Drehzahl) / Drehzahl_krit) ** 2 - 1
            # print('zusätzliche Axiallagen:' + str(round(t_Axiallagen,2))+ 'mm')

            # Lagendicken neu Berechnen
            thickness = [t_Diagonallagen / 4, t_Diagonallagen / 4, t_Umfangslagen / 2, t_Axiallagen, t_Umfangslagen / 2,
                         t_Diagonallagen / 4, t_Diagonallagen / 4]
            t_Gesamt = sum(thickness)
            D_Welle_Außen = D_Trennfuge + 2 * t_Gesamt

            # Laminatmatrizen
            abd = abdcal.abd(Q, angles_deg, thickness)
            # resultierende Steifigkeiten
            E_Axial = abd[0, 0] / t_Gesamt  # MPa
            E_Umfang = abd[1, 1] / t_Gesamt  # MPa

            Drehzahl_krit = 60 / 2 * np.pi / np.sqrt(8) * D_Welle_Außen / L_Welle ** 2 * np.sqrt(
                1000 ** 3 * E_Axial / (Mat_Welle.rho))  # u/min
            Sicherheit_Drehzahl = Drehzahl_krit / Last.Drehzahl

        # Alte Berechnung mit fixen Axialsteifigkeiten
        # E_Axial_erf_Drehzahl = ((Sicherheit*Last.Drehzahl*L_Welle**2*np.sqrt(8))/(30*np.pi*D_Welle_Außen))**2*Mat_Welle.rho/1000^3
        # t_Axiallagen = t_Diagonallagen * (E_Axial-E_Axial_erf_Drehzahl)/(E_Axial_erf_Drehzahl-Mat_Welle.E1)

        print('zusätzliche Axiallagen:' + str(round(t_Axiallagen, 1)) + 'mm')

        print('Sicherheit gegen Instabilität:' + str(round(Sicherheit_Drehzahl, 1)))

    "Steifigkeitsberechnung"

    return (D_Welle_Außen)
