# -*- coding: utf-8 -*-
"""
Created on Tue Feb  8 16:49:24 2022

@author: s0166875
"""

import numpy as np
#import math



def freier_Bereich(D_Trennfuge,L_Welle,Last,Mat_Welle,Sicherheit):
    
    
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
    Beulmoment = k_s* k_l * np.pi**3 / 6 * (D_Welle_Außen/2)**(5/4)*t_Welle**(9/4)/L_Welle**(1/2)*E_Axial**(3/8)*(E_Umfang/(1-Mat_Welle.Ny12**2))**(5/8)/1000
    Sicherheit_TB = Beulmoment/Last.Mx
    print('Sicherheit gegen Torsionsbeulen:' + str(round(Sicherheit_TB,1)))
    
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
    
    #Prüfen ob Beulwandstärke höher als Festigkeitswandstärke und wenn ja dann überschreiben
    if t_Welle_Beulen > t_Welle:
        t_Erhoehung = t_Welle_Beulen-t_Welle
        t_Welle_Beulen = t_Welle
        D_Welle_Außen = D_Trennfuge + 2*t_Welle
        print('Erhöhung der Wandstärke gegen Torsionsbeulen um '+ str(round(t_Erhoehung,1))+' mm')
    
    
    "Berechnung Biegekritische Drehzahl"
    
    
    Drehzahl_krit = 30*np.pi/8**0.5*D_Welle_Außen/L_Welle**2*(1000**4*E_Axial/(Mat_Welle.rho*1000))**0.5 #u/min
    Sicherheit_Drehzahl = Drehzahl_krit/Last.Drehzahl
    print('Sicherheit gegen Instabilität:' + str(round(Sicherheit_Drehzahl,1)))
    
    
    return (D_Welle_Außen)