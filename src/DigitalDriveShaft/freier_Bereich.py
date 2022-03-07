# -*- coding: utf-8 -*-
"""
Created on Tue Feb  8 16:49:24 2022

@author: s0166875
"""

import numpy as np


# Import local packages.
from abd import abdcal, deformation, failure, homogenization


def freier_Bereich(D_Trennfuge,L_Welle,Last,Mat_Welle,Sicherheit,Auslegungsziel):
    
    t_Umfangslagen = 0
    t_Axiallagen = 0
    
    "Festigkeitsberechnung"
    #Berechnung der erforderlichen Schichtdicke der Diagonallagen gegen Torsionsbruch 
    #Startwerte
    tau_vorh = 1
    #Abschätzung der Wandstärke mit Nabendurchmesser
    t_Diagonallagen = Sicherheit * Last.Mx * 1000/(2*np.pi*(D_Trennfuge/2)**2*Mat_Welle.tau_zul)
    
    #Iteration der Wandstärke bis geforderte Sicherheit gegen Bruch erreicht ist
    while abs(Sicherheit * tau_vorh - Mat_Welle.tau_zul) > 0.1:
        
        #Anpassung der Wellenwandstärke je nach Abweichung von zulässiger und vorhandener Spannung
        t_Diagonallagen = t_Diagonallagen + (Sicherheit *tau_vorh/Mat_Welle.tau_zul)**7-1
        
        D_Welle_Außen = D_Trennfuge + 2*t_Diagonallagen
        #Spannungsberechnung nach Excel von Sebastian
        tau_vorh =  Last.Mx * 1000/(2*np.pi*(D_Welle_Außen/2)**2*t_Diagonallagen)
        Sicherheit_Torsionsbruch = Mat_Welle.tau_zul/tau_vorh
    
        #print(Sicherheit *tau_vorh/Mat_Welle.tau_zul)
        
        
    print('Wandstärke der Diagonalschicht für Torsionsfestigkeit: '+ str(round(t_Diagonallagen,1))+' mm')
    print('Sicherheit gegen Torsionsbruch '+ str(round(Sicherheit_Torsionsbruch,1)))
    
    
   
    
    ###############################################################################
     #Lagenaufbau für Torsionsfestigkeit berechnen                                                          #
    ###############################################################################
    
    # Calculate the ply stiffness matricess matrix
    Q_Einzel = abdcal.QPlaneStress(Mat_Welle.E1, Mat_Welle.E2, Mat_Welle.Ny12, Mat_Welle.G12)
    

    # Define the stacking sequence.
    angles_deg = [+45,-45,90,0,90,-45,+45]
    thickness = [t_Diagonallagen/4, t_Diagonallagen/4, t_Umfangslagen/2, t_Axiallagen, t_Umfangslagen/2, t_Diagonallagen/4, t_Diagonallagen/4]
                
    
      
    
    ###############################################################################
    # Laminate Properites                                                         #
    ###############################################################################
    
    Q = [Q_Einzel] * len(angles_deg)
    
    # Calculate the ABD matrix and its inverse.
    abd = abdcal.abd(Q, angles_deg, thickness)
    #abd_inv = abdcal.matrix_inverse(abd)
    
    
    "Beulrechnung"
    k_s = 0.925 #Beiwert für gelenkige Lagerung
    k_l = 0.77 #Beiwert für Imperfektionsanfälligkeit
    E_Axial= abd[0,0]/t_Diagonallagen  #MPa #20000 bei Sebastian
    E_Umfang = abd[1,1]/t_Diagonallagen #MPa #20000 bei Sebastian
    #Beulmomentberechnung nach Excel von Sebastian
    Beulmoment = k_s* k_l * np.pi**3 / 6 * (D_Welle_Außen/2)**(5/4)*t_Diagonallagen**(9/4)/np.sqrt(L_Welle)*E_Axial**(3/8)*(E_Umfang/(1-Mat_Welle.Ny12**2))**(5/8)/1000
    Sicherheit_TB = Beulmoment/Last.Mx
    print('Sicherheit gegen Torsionsbeulen:' + str(round(Sicherheit_TB,1)))
    
    #Prüfen ob Sicherheit gegen Beulen geringer ist als geforderte Sicherheit und wenn ja dann überschreiben
    if Sicherheit_TB < Sicherheit:
    
        if Auslegungsziel == 'Steifigkeit':
            #Erreichen der Beulfestigkeit mit geringster Erhöhung der Axialsteifigkeit
            #Einführen einer umfangssteifen Schicht in der Mitte des Laminats
            
            while abs(Last.Mx*Sicherheit - Beulmoment) > 0.1:
                #iterative Anpassung der Umfangslagen auf Basis des Ergebnisses
                t_Umfangslagen = t_Umfangslagen + ((Sicherheit*Last.Mx)/Beulmoment)**2-1
                #print('zusätzliche Umfangslagen:' + str(round(t_Umfangslagen,2))+ 'mm')
                
                #Lagendicken neu Berechnen
                thickness = [t_Diagonallagen/4, t_Diagonallagen/4, t_Umfangslagen/2, t_Axiallagen, t_Umfangslagen/2, t_Diagonallagen/4, t_Diagonallagen/4]
                t_Gesamt = sum(thickness)
                D_Welle_Außen = D_Trennfuge + 2*t_Gesamt
                
                #Laminatmatrizen
                abd = abdcal.abd(Q, angles_deg, thickness)
                #resultierende Steifigkeiten
                E_Axial = abd[0,0]/t_Gesamt  #MPa 
                E_Umfang = abd[1,1]/t_Gesamt #MPa
                
                Beulmoment = k_s* k_l * np.pi**3 / 6 * (D_Welle_Außen/2)**(5/4)*t_Gesamt**(9/4)/np.sqrt(L_Welle)*E_Axial**(3/8)*(E_Umfang/(1-Mat_Welle.Ny12**2))**(5/8)/1000
                #print((Sicherheit*Last.Mx)/Beulmoment)
                
            #Alte Berechnung mit fixen Axial und Umfangssteifigkeiten
            #E_Umfang_erf = (Sicherheit * 1000 * Last.Mx/(k_s* k_l * np.pi**3 / 6 * (D_Welle_Außen/2)**(5/4)*t_Welle**(9/4)/np.sqrt(L_Welle)*E_Axial**(3/8))) **(8/5)*(1-Mat_Welle.Ny12**2)
            #t_Umfangslagen = t_Welle * (E_Umfang-E_Umfang_erf)/(E_Umfang_erf-Mat_Welle.E1)
            
            print('Wandstärke der Umfangslagen für Beulfestigkeit:' + str(round(t_Umfangslagen,1))+ 'mm')
            Sicherheit_TB = Beulmoment/Last.Mx
            print('Sicherheit gegen Torsionsbeulen:' + str(round(Sicherheit_TB,1)))
            
            
            
            
            
            
        if Auslegungsziel == 'Fertigung':
            #Erreichen der Beulfestigkeit durch Erhöhung der Torsionsschicht
            #Startwert: Berechung der Wandstärke gegen Beulen mit dem Außendurchmesser aus der Festigkeitsberechung
            t_Diagonallagen_Beulen = ((6*Last.Mx*1000*Sicherheit*L_Welle**(1/2))/(k_s*k_l*np.pi**2*E_Axial**(3/8)*(D_Welle_Außen/2)**(5/4)) * (E_Umfang/(1-Mat_Welle.Ny12**2))**(-5/8))**(4/9)
            
            #Iteration der Wandstärke bis geforderte Sicherheit gegen Beulen erreicht ist
            while abs(Last.Mx*Sicherheit - Beulmoment ) > 0.1:
                #Anpassung der Wellenwandstärke je nach Abweichung von zulässiger und vorhandener Beulmoment
                t_Diagonallagen_Beulen = t_Diagonallagen_Beulen + ((Sicherheit*Last.Mx)/Beulmoment)**5-1
                
                
                thickness = [t_Diagonallagen_Beulen/4, t_Diagonallagen_Beulen/4, t_Umfangslagen/2, t_Axiallagen, t_Umfangslagen/2, t_Diagonallagen_Beulen/4, t_Diagonallagen_Beulen/4]
                t_Gesamt = sum(thickness)
                D_Welle_Außen = D_Trennfuge + 2*t_Gesamt
                
                #Laminatmatrizen
                abd = abdcal.abd(Q, angles_deg, thickness)
                #resultierende Steifigkeiten
                E_Axial = abd[0,0]/t_Gesamt  #MPa 
                E_Umfang = abd[1,1]/t_Gesamt #MPa
                
                
                #Beulmomentberechnung nach Excel von Sebastian
                Beulmoment = k_s* k_l * np.pi**3 / 6 * (D_Welle_Außen/2)**(5/4)*t_Gesamt**(9/4)/L_Welle**(1/2)*E_Axial**(3/8)*(E_Umfang/(1-Mat_Welle.Ny12**2))**(5/8)/1000
                
                #print((Sicherheit*Last.Mx)/Beulmoment)
                
            
            #Berechnung der Wandstärkenerhöhung für Beulfestigkeit       
            t_Erhoehung_Beulen = t_Diagonallagen_Beulen-t_Diagonallagen
            t_Diagonallagen = t_Diagonallagen_Beulen
            
            
            print('Erhöhung der Diagonallagen gegen Torsionsbeulen um '+ str(round(t_Erhoehung_Beulen,1))+' mm')
            Beulmoment = k_s* k_l * np.pi**3 / 6 * (D_Welle_Außen/2)**(5/4)*t_Gesamt**(9/4)/np.sqrt(L_Welle)*E_Axial**(3/8)*(E_Umfang/(1-Mat_Welle.Ny12**2))**(5/8)/1000
            Sicherheit_TB = Beulmoment/Last.Mx
            print('Sicherheit gegen Torsionsbeulen:' + str(round(Sicherheit_TB,1)))
    
    "Berechnung Biegekritische Drehzahl"
    
    # Formel für Berechnung von Biegekritischer Drehzahl aus Sebastians Excel
    Drehzahl_krit = 60/2*np.pi/np.sqrt(8)*D_Welle_Außen/L_Welle**2*np.sqrt(1000**3*E_Axial/(Mat_Welle.rho)) #u/min
    Sicherheit_Drehzahl = Drehzahl_krit/Last.Drehzahl
    print('Biegekritische Drehzahl:' + str(round(Drehzahl_krit,1)))
    print('Sicherheit gegen Instabilität:' + str(round(Sicherheit_Drehzahl,1)))
    
    if Sicherheit_Drehzahl < Sicherheit:
        
        
        while abs(Last.Drehzahl*Sicherheit - Drehzahl_krit) > 0.1:
                #iterative Anpassung der Umfangslagen auf Basis des Ergebnisses
                t_Axiallagen = t_Axiallagen + ((Sicherheit*Last.Drehzahl)/Drehzahl_krit)**2-1
                #print('zusätzliche Axiallagen:' + str(round(t_Axiallagen,2))+ 'mm')
                
                #Lagendicken neu Berechnen
                thickness = [t_Diagonallagen/4, t_Diagonallagen/4, t_Umfangslagen/2, t_Axiallagen, t_Umfangslagen/2, t_Diagonallagen/4, t_Diagonallagen/4]
                t_Gesamt = sum(thickness)
                D_Welle_Außen = D_Trennfuge + 2*t_Gesamt
                
                #Laminatmatrizen
                abd = abdcal.abd(Q, angles_deg, thickness)
                #resultierende Steifigkeiten
                E_Axial = abd[0,0]/t_Gesamt  #MPa 
                E_Umfang = abd[1,1]/t_Gesamt #MPa
                
                Drehzahl_krit = 60/2*np.pi/np.sqrt(8)*D_Welle_Außen/L_Welle**2*np.sqrt(1000**3*E_Axial/(Mat_Welle.rho)) #u/min
                Sicherheit_Drehzahl = Drehzahl_krit/Last.Drehzahl
        
        #Alte Berechnung mit fixen Axialsteifigkeiten
        #E_Axial_erf_Drehzahl = ((Sicherheit*Last.Drehzahl*L_Welle**2*np.sqrt(8))/(30*np.pi*D_Welle_Außen))**2*Mat_Welle.rho/1000^3
        #t_Axiallagen = t_Diagonallagen * (E_Axial-E_Axial_erf_Drehzahl)/(E_Axial_erf_Drehzahl-Mat_Welle.E1)
        
        
        print('zusätzliche Axiallagen:' + str(round(t_Axiallagen,1))+ 'mm')
        
        print('Sicherheit gegen Instabilität:' + str(round(Sicherheit_Drehzahl,1)))
    
    "Steifigkeitsberechnung"
    

    return (D_Welle_Außen)