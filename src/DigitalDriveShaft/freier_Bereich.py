# -*- coding: utf-8 -*-
"""
Created on Tue Feb  8 16:49:24 2022

@author: s0166875
"""

import numpy as np
#import math



def freier_Bereich(D_Trennfuge,L_Welle,Last,Mat_Welle,Sicherheit,Steifigkeit):
    
    t_Umfangslagen = 0
    t_Axiallagen = 0
    
    "Festigkeitsberechnung"
    #Startwerte
    tau_vorh = 1
    #Abschätzung der Wandstärke mit Nabendurchmesser
    t_Welle = Sicherheit * Last.Mx * 1000/(2*np.pi*(D_Trennfuge/2)**2*Mat_Welle.tau_zul)
    
    #Iteration der Wandstärke bis geforderte Sicherheit gegen Bruch erreicht ist
    while abs(tau_vorh - Mat_Welle.tau_zul) > 0.1:
        
        
        D_Welle_Außen = D_Trennfuge + 2*t_Welle
        #Spannungsberechnung nach Excel von Sebastian
        tau_vorh = Sicherheit * Last.Mx * 1000/(2*np.pi*(D_Welle_Außen/2)**2*t_Welle)
    
        #print(tau_vorh/Mat_Welle.tau_zul)
        #Anpassung der Wellenwandstärke je nach Abweichung von zulässiger und vorhandener Spannung
        t_Welle = t_Welle + (tau_vorh/Mat_Welle.tau_zul)**7-1
    print('Wandstärke für Festigkeit: '+ str(round(t_Welle,1))+' mm')
    
    "Beulrechnung"
    k_s = 0.925 #Beiwert für gelenkige Lagerung
    k_l = 0.77 #Beiwert für Imperfektionsanfälligkeit
    E_Umfang = 20000 #MPa
    E_Axial = 20000 #MPa
    #Beulmomentberechnung nach Excel von Sebastian
    Beulmoment = k_s* k_l * np.pi**3 / 6 * (D_Welle_Außen/2)**(5/4)*t_Welle**(9/4)/np.sqrt(L_Welle)*E_Axial**(3/8)*(E_Umfang/(1-Mat_Welle.Ny12**2))**(5/8)/1000
    Sicherheit_TB = Beulmoment/Last.Mx
    print('Sicherheit gegen Torsionsbeulen:' + str(round(Sicherheit_TB,1)))
    
    #Prüfen ob Sicherheit gegen Beulen geringer ist als geforderte Sicherheit und wenn ja dann überschreiben
    if Sicherheit_TB < Sicherheit:
    
        if Steifigkeit == True:
            #Einführen einer umfangssteifen Schicht
            E_Umfang_erf = (Sicherheit * 1000 * Last.Mx/(k_s* k_l * np.pi**3 / 6 * (D_Welle_Außen/2)**(5/4)*t_Welle**(9/4)/np.sqrt(L_Welle)*E_Axial**(3/8))) **(8/5)*(1-Mat_Welle.Ny12**2)
            t_Umfangslagen = t_Welle * (E_Umfang-E_Umfang_erf)/(E_Umfang_erf-Mat_Welle.E1)
            print('zusätzliche Umfangslagen:' + str(round(t_Umfangslagen,1))+ 'mm')
            Beulmoment = k_s* k_l * np.pi**3 / 6 * (D_Welle_Außen/2)**(5/4)*t_Welle**(9/4)/np.sqrt(L_Welle)*E_Axial**(3/8)*(E_Umfang_erf/(1-Mat_Welle.Ny12**2))**(5/8)/1000
            Sicherheit_TB = Beulmoment/Last.Mx
            print('Sicherheit gegen Torsionsbeulen:' + str(round(Sicherheit_TB,1)))
            t_Gesamt = t_Welle + t_Umfangslagen
        else:
            
            #Erhöhung der Torsionsschicht
            #Startwert: Berechung der Wandstärke gegen Beulen mit dem Außendurchmesser aus der Festigkeitsberechung
            t_Welle_Beulen = ((6*Last.Mx*1000*Sicherheit*L_Welle**(1/2))/(k_s*k_l*np.pi**2*E_Axial**(3/8)*(D_Welle_Außen/2)**(5/4)) * (E_Umfang/(1-Mat_Welle.Ny12**2))**(-5/8))**(4/9)
            
            #Iteration der Wandstärke bis geforderte Sicherheit gegen Beulen erreicht ist
            while abs(Last.Mx*Sicherheit - Beulmoment ) > 0.1:
                D_Welle_Außen_Beulen = D_Trennfuge + 2*t_Welle_Beulen
                #Beulmomentberechnung nach Excel von Sebastian
                Beulmoment = k_s* k_l * np.pi**3 / 6 * (D_Welle_Außen_Beulen/2)**(5/4)*t_Welle_Beulen**(9/4)/L_Welle**(1/2)*E_Axial**(3/8)*(E_Umfang/(1-Mat_Welle.Ny12**2))**(5/8)/1000
                
                #print((Sicherheit*Last.Mx)/Beulmoment)
                #Anpassung der Wellenwandstärke je nach Abweichung von zulässiger und vorhandener Beulmoment
                t_Welle_Beulen = t_Welle_Beulen + ((Sicherheit*Last.Mx)/Beulmoment)**5-1
            
                    
            t_Erhoehung = t_Welle_Beulen-t_Welle
            t_Welle = t_Welle_Beulen
            D_Welle_Außen = D_Trennfuge + 2*t_Welle
            
            print('Erhöhung der Wandstärke gegen Torsionsbeulen um '+ str(round(t_Erhoehung,1))+' mm')
            Beulmoment = k_s* k_l * np.pi**3 / 6 * (D_Welle_Außen/2)**(5/4)*t_Welle**(9/4)/np.sqrt(L_Welle)*E_Axial**(3/8)*(E_Umfang/(1-Mat_Welle.Ny12**2))**(5/8)/1000
            Sicherheit_TB = Beulmoment/Last.Mx
            print('Sicherheit gegen Torsionsbeulen:' + str(round(Sicherheit_TB,1)))
    
    "Berechnung Biegekritische Drehzahl"
    
    # Formel für Berechnung von Biegekritischer Drehzahl aus Sebastians Excel
    Drehzahl_krit = 60/2*np.pi/np.sqrt(8)*D_Welle_Außen/L_Welle**2*np.sqrt(1000**3*E_Axial/(Mat_Welle.rho)) #u/min
    Sicherheit_Drehzahl = Drehzahl_krit/Last.Drehzahl
    print('Biegekritische Drehzahl:' + str(round(Drehzahl_krit,1)))
    print('Sicherheit gegen Instabilität:' + str(round(Sicherheit_Drehzahl,1)))
    
    if Sicherheit_Drehzahl < Sicherheit:
        E_Axial_erf_Drehzahl = ((Sicherheit*Last.Drehzahl*L_Welle**2*np.sqrt(8))/(30*np.pi*D_Welle_Außen))**2*Mat_Welle.rho/1000^3
        t_Axiallagen = t_Welle * (E_Axial-E_Axial_erf_Drehzahl)/(E_Axial_erf_Drehzahl-Mat_Welle.E1)
        print('zusätzliche Axiallagen:' + str(round(t_Axiallagen,1))+ 'mm')
        t_Gesamt = t_Welle + t_Axiallagen + t_Umfangslagen
    
    
    "Steifigkeitsberechnung"
    

    return (D_Welle_Außen)