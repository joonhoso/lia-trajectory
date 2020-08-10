#%% Script information
# Name: fnc.py
# Authors: Trajectory Team (Matias Pellegrini, Pablo Lobo)
# Owner: LIA Aerospace
# Date: August 2020
#
#%% Script description
#
# The aim of this module is defining functions to be used in the simulation.
#
#%% Packages
import numpy as np

#%% Atmospheric properties

def layer(Hz: float)->float: 
    # The aim of this function is to define which layer is the vehicle
    # currently flying through (according to Table 4 of the Standard)
    # 
    # === INPUTS ===
    # Hz [m] - Geopotential height
    # === OUTPUTS === 
    # b [adim] - Subscript of the layer
    #
    # Cases
    if Hz>=0 and Hz<11000:
        b = 0
    elif Hz>=11000 and Hz<20000:    
        b = 1
    elif Hz>=20000 and Hz<32000:
        b = 2
    elif Hz>=32000 and Hz<47000:
        b = 3
    elif Hz>=47000 and Hz<51000:
        b = 4
    elif Hz>=51000 and Hz<71000:
        b = 5  
    elif Hz>=71000 and Hz<84852:
        b = 6
    elif Hz==84852:
        b = 7
    return b
        
def table4(z: float):
    # The aim of this function is to define   the constants provided by 
    # Table 4 given the current geometrical height at which the vehicle is.
    # === INPUTS ===
    # z [m] - Geometric height
    # === OUTPUTS === 
    # b [adim]      Subscript of the layer
    # Lmb [K/km']   Molecular-scale temperature gradient (Table 4)
    # Tmb [K]       Temperature constant
    #   This value is calculated as Tm,b = Tm,b-1 + Lm,b-1 * (Hb - Hb-1) 
    # Hb [km']      Geopotential Height of the layer (Table 4)
    # Hz [km']      Geopotential Height of the vehicle
    # Pb [N/m^2]    Pressure constant 
    #   This value is calculated making sure p(z) is continuous.
    # Function
    # The layer is defined.
    ro = 6356.766 * 10**3       # [m] - Earth's radius - (Page 4)
    Hz = (z*ro) / (ro + z)      # [m'] - Geopotential height of the vehicle
    b = layer(Hz)               # [adim] - Subscript of the layer
    Hz = Hz*0.001               # [km'] - Geopotential height of the vehicle
    Hb_vec = np.array([0, 11, 20, 32, 47, 51, 71, 84.852])
    Lmb_vec = np.array([-6.5, 0, 1, 2.8, 0, -2.8, -2, 0])
    Tmb_vec = np.array([288.15, 216.65, 216.65, 228.65, 270.65, 270.65, 214.65, 186.946])
    pb_vec = np.array([101325, 22632.06, 5474.88, 868.01, 110.90, 66.93, 3.95])
    Hb = Hb_vec[b]
    Lmb = Lmb_vec[b]
    Tmb = Tmb_vec[b]
    Pb = pb_vec[b]
    return b, Lmb, Tmb, Hb, Hz, Pb

def tm(Tmb,Lmb,Hz,Hb):
    # The aim of this function is to estimate the Tm value according to
    # equation (23) of the US Standard Atmosphere 1976.
    # This function gives the temperature for the range 0-76km.
    # === INPUTS ===
    # Tmb [K]       Temperature constant
    # Lmb [K/km']   Molecular-scale temperature gradient
    # Hz [km']      Geopotential height of interest
    # Hb [km']      Geopotential Height for the particular layer (Table 4)
    # === OUTPUTS === 
    # Tm [K]     Temperature at given geopotential height Hz
    Tm = Tmb + Lmb*(Hz-Hb)     #  [K] - Temperature at given geopotential height Hz
    return Tm

def p(Tmb,Lmb,Hz,Hb,Pb):
    # The aim of this function is to estimate the P value according to
    # equation (33a 33b) of the US Standard Atmosphere 1976.
    # This function gives the pressure for the range 0-76km.
    # === INPUTS ===
    # Tmb [K]       Temperature constant
    # Lmb [K/km']   Molecular-scale temperature gradient
    # Hz [km']      Geopotential height of interest
    # Hb [km']      Geopotential Height for the particular layer (Table 4)
    # Pb [N/m^2]    Pressure constant
    # === OUTPUTS === 
    # P [N/m^2]     Pressure at given geopotential height Hz
    # === CONSTANTS ===
    go = 9.80665                # [m^2/s^2.m] - Gravity @ SL (Page 2)
    R = 8.31432 * 10**-3        # [Nm / (kmol.K)] - Gas constant (Page 2)
    Mo = 28.9644                # [kg/kmol] - Mean Molecular Weight - (Page 9)
    if Lmb!=0:
        P = Pb*(Tmb / (Tmb + (Lmb*(Hz-Hb))))**((go*Mo)/(R*Lmb*1000))
    elif Lmb==0:
        P = Pb*np.exp((-go*Mo*(Hz-Hb))/(R*Tmb*1000))
    return P
        