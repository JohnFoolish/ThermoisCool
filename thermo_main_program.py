# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 17:37:27 2020

@authors: John Lewis Corker and Somil Joshi

@version 7
"""

import numpy as np
import argparse as arg
from graph_class import graph_data

def get_range_interval(range_data, num_points = 20):
    diff = range_data[1] - range_data[0]
    if (diff < num_points):
        factor = 1
    else:    
        factor = diff // num_points
    remainder = diff % factor 
    
    return (range_data[0], range_data[1] + remainder + 1, factor)

def main():
    """
    This is the main function of the state space grapher. From the project 
    members John Lewis, Somil, and Chesson, we apologize for the mess of 
    documentation you will find in the code. You can find all the information
    about how to run the program from the command line on the README.
    
    This method takes in command line arguments and then feeds them into the 
    different scenarios in order to create the 3-D projections of 4-D state
    space.
    
    If you have any questions about the functioning of the code, please email
    jcorker3@gatech.edu.
    
    """
    
    state_variables = ['energy', 'temperature', 'volume', 'pressure', 'Energy',
                       'Temperature', 'Volume', 'Pressure', 'E', 'T', 'V', 'P', 'U']
    
    
    parser = arg.ArgumentParser(description = "Input the first state variable that will"
                                + " be varied, the two integer values that the"
                                + " variable will vary between, and then"
                                + " repeat this again for the second state variable."
                                + "\n This will graph plots showing the 3-D state"
                                + "space for the variables and ranges which are specified.")
    
    state_var_1 = parser.add_argument_group("State Variable 1", description = 
                                            "Information about the first state "
                    + "variable that will be displayed, including the range of "
                    + "its variation.")
    
    state_var_2 = parser.add_argument_group("State Variable 2", description = 
                                            "Information about the second state "
                    + "variable that will be displayed, including the range of "
                    + "its variation.")
    
    state_var_1.add_argument("State_Variable_1", type = str, choices = state_variables,
                             help = "The first state" 
                             + " space variable that will be varied.\n")
    state_var_1.add_argument("Start_1", type = int, help = "The starting value for" 
                             + " the first varying state variable.")
    state_var_1.add_argument("End_1", type = int, help = "The ending value for the"
                             + " first varying state variable.")
    
    state_var_2.add_argument("State_Variable_2", type = str, choices = state_variables,
                             help = "The second state" 
                             + " space variable that will be varied.")
    state_var_2.add_argument("Start_2", type = int, help = "The starting value for" 
                             + " the second varying state variable.")
    state_var_2.add_argument("End_2", type = int, help = "The ending value for the"
                             + " second varying state variable.")
    state_var_2.add_argument("--fixed_VDW", type =bool, help = "Enables the pressure"
                             + " dependent VDW gas graphing... does not work if your"
                             + " two state variables are pressure and volume.")

    simulation_data = parser.parse_args()
    
    
    Ideal_S_S = Ideal_statmech_model(simulation_data)

    VDW_S = VDW_classical_model(simulation_data)
    
    Ideal_C_S = Ideal_classical_model(simulation_data)

    difference_plotter(VDW_S, Ideal_C_S, "% Difference between VDW and Thermo. Ideal Gas", simulation_data)

    difference_plotter(Ideal_S_S, Ideal_C_S, "% Difference between Stat Mech and Thermo. Ideal Gas", simulation_data)

    difference_plotter(Ideal_S_S, VDW_S, "% Difference between Stat Mech Ideal Gas and VDW Gas", simulation_data)

 
def difference_plotter(Slist1, Slist2, differences, simulation_data):

    state_variable_1 = simulation_data.State_Variable_1
    state_var_1_range = (simulation_data.Start_1, simulation_data.End_1)
    state_variable_2 = simulation_data.State_Variable_2
    state_var_2_range = (simulation_data.Start_2, simulation_data.End_2)

    graph_data_class = graph_data(differences, state_variable_1, state_variable_2,
                                "% Entropy Difference [%]", state_var_1_range,
                                state_var_2_range)  
    
    range_data_1 = get_range_interval(state_var_1_range)
    range_data_2 = get_range_interval(state_var_2_range)


    i = 0
    for sv1 in range(range_data_1[0], range_data_1[1], range_data_1[2]):
        for sv2 in range(range_data_2[0], range_data_2[1], range_data_2[2]):
            
                if (Slist2[i] == 0):
                    Slist2[i] = 1
            
                s_diff = np.abs(((Slist1[i] - Slist2[i])/Slist2[i])*100)
            
                graph_data_class.plot_point(sv1, sv2, s_diff, True)    
                i = i + 1
    
    graph_data_class.display()
    
def VDW_classical_model(simulation_data):
    """
    This function plots the results of the VDW model for entropy calculated 
    using classical Thermodynamics.

    Inputs:
    -------
    None

    Returns:
    --------
    Graph: A matplotlib graph of S, T, state-space.
    Equations:

    Ideal Gas:

    PV = NRT
    P = pressure
    V = volume
    N = moles of substance = N_particles / N_a
    R = ideal gas constant = N_a * K_b
    T = temperature in Kelvin

    U = cNRT
    U = energy
    c = (# degrees of freedom / 2)

    Molar Volume: v = V / N
    Molar Energy: u = U / N
    Molar Entropy: s = S / N

    Entropy is extensive:
    S(U, V, N) = N * S(U / N, V / N, 1) = N * s(u, v)

    ds = (1 / T) * du + (P /T) dv
    s = cR*log(u) + R*log(v) + constant

    VDW Gas:
    P = (RT) / (v -b) - a / (v^2)
    R = ideal gas constant = N_a * K_b
    a, b = material specific constants
    v = molar volume
    ...
    Molar Entropy: s(u, v) = cR*log(u + a/v) +R*log(v - b) + constant
    Entropy: S = s * N
    """

    # constants
    c = 3 / 2
    R = 8.3145
    V = 1
    T = 273
    P = 1
    
    # Van der Waals constants for helium gas
    a = 0.03646
    b = 0.0238
    N = 1.0

    # Populate list array with a range of different entropy values
    Slist = []
    Ulist = []
    Vlist = []
    Tlist = []
    Plist = [] 
    
    state_variable_1 = simulation_data.State_Variable_1
    state_var_1_range = (simulation_data.Start_1, simulation_data.End_1)
    state_variable_2 = simulation_data.State_Variable_2
    state_var_2_range = (simulation_data.Start_2, simulation_data.End_2)

    graph_data_class = graph_data("Van der Waals Gas", state_variable_1, state_variable_2,
                                "Entropy [J/K]", state_var_1_range,
                                state_var_2_range)  
    
    range_data_1 = get_range_interval(state_var_1_range)
    range_data_2 = get_range_interval(state_var_2_range)

    var_1 = graph_data_class.var1
    var_2 = graph_data_class.var2

    fixed_vdw = simulation_data.fixed_VDW

    # Now calculate the entropy for VDW gas as it goes towards
    # increasing temperature values
    i = 1
    j = 0
    k = 1
    l = 0
    for sv1 in range(range_data_1[0], range_data_1[1], range_data_1[2]):
        for sv2 in range(range_data_2[0], range_data_2[1], range_data_2[2]):
            
            
            if (var_1 == "p"):
                p = sv1
            elif (var_1 == "u"):
                U = sv1 
            elif (var_1 == "t"):
                T = sv1
            elif (var_1 == "v"):
                V = sv1
                
            if (var_2 == "p"):
                p = sv2
            elif (var_2 == "u"):
                U = sv2 
            elif (var_2 == "t"):
                T = sv2
            elif (var_2 == "v"):
                V = sv2
            
            
            if (var_1 != "u" and var_2 != "u"):    
                U = (3 / 2) * R * T
            u = U /N     
            
            if (fixed_vdw):
                if (var_1 == "p" or var_2 == "p"):                
                    
                    if (var_2 == "t" or var_1 == "t"):
                        poly = np.polynomial.Polynomial([-(a*b)/p, (a/b), -(b + (R*T)/p), 1])
                        V = poly.roots()
                        V_real = V.real[abs(V.imag)<1e-5]
    
                    elif (var_2 == "u" or var_1 == "u"):
                        poly = np.polynomial.Polynomial([-(a*b)/p, (a/b), -(b + ((u*2)/(3*R))/p), 1])
                        V = poly.roots()
                        V_real = V.real[abs(V.imag)<1e-5]
                        
                    elif (var_2 == "v" or var_1 == "v"):
                        T = (p * (V - b) + a*(1/V)**2*(V-b))/R
                        V_real = [V]
                
            else:
                V_real = [V]
                
            if (var_1 != "u" and var_2 != "u"):    
                U = (3 / 2) * R * T
            u = U /N     
            #print(V)        
            Ulist.append(U)
            Tlist.append(T)
            Plist.append(p)
            for V_item in V_real:  
                
                #print(V_item)
                v = V_item / N  
                u = U /N
                Vlist.append(v)                
                s = (c*R)*np.log(u + a/v) + R*np.log(v - b)
                
                #Add the data to the list
                Slist.append(s * N)
                
                
                if (len(Plist) < 2):
                    stable = True
                    i = 0
                    j = -1
                else:
                    if (fixed_vdw):
                        #At constant Volume, stability is found through dE/dT > 0.
                        if (var_1 == "p" or var_2 == "p"):
                            if (Vlist[k] == Vlist[l]):
                                stable = True
                            else:    
                                stab_test = (Plist[i] - Plist[j])/(Vlist[k] - Vlist[l])
                                k = k + 1
                                l = l + 1
                                #print(stab_test)
                                if stab_test > 0:
                                    stable = 0
                                elif stab_test < 0:
                                    stable = 1
                                else:
                                    stable = 2
                        else:     
                            
                            C_v = 1#(Ulist[1] - Ulist[0])/(Tlist[1] - Tlist[0])
                            
                            if(C_v > 0):
                                stable = True
                            else:
                                stable = False
                    else:
                        stable = True
                    #Reset the list so that we accurately calculate the stability 
                    #for each point
                    #tmpU = Ulist[1]
                    #tmpT = Tlist[1]
                    #Ulist.clear()
                    #Tlist.clear()
                    #Ulist.append(tmpU)
                    #Tlist.append(tmpT)
                
                
                
                graph_data_class.plot_point(sv1, sv2, s, stable)
            i = i + 1
            j = j + 1
            
    graph_data_class.display()
    return Slist

def Ideal_classical_model(simulation_data):
    """
    This function plots the results of the Ideal gas model for entropy
    calculated using classical Thermodynamics.

    Inputs:
    -------
    None

    Returns:
    --------
    Graph: A matplotlib graph of S, T, state-space.
    Equations:

    Ideal Gas:

    PV = NRT
    P = pressure
    V = volume
    N = moles of substance = N_particles / N_a
    R = ideal gas constant = N_a * K_b
    T = temperature in Kelvin

    U = cNRT
    U = energy
    c = (# degrees of freedom / 2)

    Molar Volume: v = V / N
    Molar Energy: u = U / N
    Molar Entropy: s = S / N

    Entropy is extensive:
    S(U, V, N) = N * S(U / N, V / N, 1) = N * s(u, v)

    ds = (1 / T) * du + (P /T) dv
    s = cR*log(u) + R*log(v) + constant
    """

    # constants
    c = 3 / 2
    R = 8.3145
    N = 1.0
    V = 1
    T = 273
    P = 1

    state_variable_1 = simulation_data.State_Variable_1
    state_var_1_range = (simulation_data.Start_1, simulation_data.End_1)
    state_variable_2 = simulation_data.State_Variable_2
    state_var_2_range = (simulation_data.Start_2, simulation_data.End_2)
    
    graph_data_class = graph_data("Thermodynamics Ideal Gas", state_variable_1, state_variable_2,
                              "Entropy [J/K]", state_var_1_range,
                              state_var_2_range)  

    range_data_1 = get_range_interval(state_var_1_range)
    range_data_2 = get_range_interval(state_var_2_range)

    var_1 = graph_data_class.var1
    var_2 = graph_data_class.var2

    # Populate list array with a range of different entropy values
    Slist = []
    Ulist = []
    Vlist = []
    Tlist = []
    Plist = []

    # Now calculate the entropy for VDW gas as it goes towards
    # increasing temperature values
    i = 1
    j = 0
    k = 1
    l = 0
    for sv1 in range(range_data_1[0], range_data_1[1], range_data_1[2]):
        for sv2 in range(range_data_2[0], range_data_2[1], range_data_2[2]):
            
            
            if (var_1 == "p"):
                P = sv1
            elif (var_1 == "u"):
                U = sv1 
            elif (var_1 == "t"):
                T = sv1
            elif (var_1 == "v"):
                V = sv1
                
            if (var_2 == "p"):
                P = sv2
            elif (var_2 == "u"):
                U = sv2 
            elif (var_2 == "t"):
                T = sv2
            elif (var_2 == "v"):
                V = sv2
            
            if (var_1 != "u" and var_2 != "u"):    
                U = (3 / 2) * R * T           
                
            if (var_1 == "p" or var_2 == "p"):
                if (var_2 == "t" or var_1 == "t"):
                    V = (T*N*R)/P
                elif (var_2 == "u" or var_1 == "u"):
                    V = (U*2*N*R)/(3*P*R)
                elif (var_2 == "v" or var_1 == "v"):
                    U = (3 * P * V ) / (2 * N)
        
            v = V / N
            u = U /N
            s = (c*R)*np.log(u) + R*np.log(v)
            Slist.append(s * N)
            Ulist.append(U)
            Vlist.append(V)
            Tlist.append(T)


            if (len(Plist) < 2):
                stable = True
                i = 0
                j = -1
            else:
                
                #At constant Volume, stability is found through dE/dT > 0.
                if (var_1 == "p" or var_2 == "p"):
                    stab_test = (Plist[i] - Plist[j])/(Vlist[k] - Vlist[l])
                    k = k + 1
                    l = l + 1
                    #print(stab_test)
                    if stab_test > 0:
                        stable = 0
                    elif (stab_test < 0):
                        stable = 1
                    else:
                        stable = 2
                else:#At constant Volume, stability is found through dE/dT > 0.
                    C_v = 1#(Ulist[1] - Ulist[0])/(Tlist[1] - Tlist[0])
                
                    if(C_v > 0):
                        stable = True
                    else:
                        stable = False
                
                #Reset the list so that we accurately calculate the stability 
                #for each point
                #tmpU = Ulist[1]
                #tmpT = Tlist[1]
                #Ulist.clear()
                #list.clear()
                #Ulist.append(tmpU)
                #Tlist.append(tmpT)
            
            
            
            graph_data_class.plot_point(sv1, sv2, s, stable)
            
            
    graph_data_class.display()
    return Slist
    
def Ideal_statmech_model(simulation_data):
    """
    This function plots the entropy of an ideal gas system from the Statistical
    Mechanics model
    
    Inputs:
    -------
    None
    
    Returns:
    --------
    Graph: A matplotlib graph of S, T, state-space.   
    
    Equations:
    ----------
    m = mass of particle
    h = Plank's constant
    C = ((e * m) ^ (3/2) ) / h^3 * ((4pi * e) / 3) ^ (3/2)   
    v = Volume (Liters)
    N = number of particles
    n = scaling factor
    t = temperature
    U = Total Thermal energy given by 1/2 * K_b * t
    
    w = number of microstates 
    
    
    
    """

    #Fill in some dummy values for the Entropy Equation
    m = 6.647e-27 #kg
    h = 6.626070e-34 #Plankl
    v = 1.0 #L
    N = 6.02e23 #Num part
    t = 273
    P = 1

    #Populate list array with a range of different entropy values for the 
    #monatomic ideal gas
    Slist = []
    Tlist = []
    Vlist = []
    Ulist = []
    Plist = []
    
    state_variable_1 = simulation_data.State_Variable_1
    state_var_1_range = (simulation_data.Start_1, simulation_data.End_1)
    state_variable_2 = simulation_data.State_Variable_2
    state_var_2_range = (simulation_data.Start_2, simulation_data.End_2)
    graph_data_class = graph_data("Statistical Mechanics Ideal Gas", state_variable_1, state_variable_2,
                              "Entropy [J/K]", state_var_1_range,
                              state_var_2_range)
    
    range_data_1 = get_range_interval(state_var_1_range)
    range_data_2 = get_range_interval(state_var_2_range)
    
    var_1 = graph_data_class.var1
    var_2 = graph_data_class.var2
    
    #Now calculate the entropy for the Monotomic ideal gas as it goes towards 
    #increasing temperature values and increasing volumes 
    for sv1 in range(range_data_1[0], range_data_1[1], range_data_1[2]):
        for sv2 in range(range_data_2[0], range_data_2[1], range_data_2[2]):
            
            
            if (var_1 == "p"):
                P = sv1
            elif (var_1 == "u"):
                U = sv1 
            elif (var_1 == "t"):
                t = sv1
            elif (var_1 == "v"):
                v = sv1
                
            if (var_2 == "p"):
                P = sv2
            elif (var_2 == "u"):
                U = sv2 
            elif (var_2 == "t"):
                t = sv2
            elif (var_2 == "v"):
                v = sv2            
            
            
            
            if (var_1 != "u" and var_2 != "u"):  
            #Calculate the Thermal Energy of the system
                U = 3*N/2 * 1.380649e-23 * t
            
            s = (1.380649e-23 *( N*np.log((np.e * v) / (N * h**3)) + (3 * N) / 2 * np.log(4 * m * np.e * np.pi * U / (3 * N))))
        
            Slist.append((s))
            Tlist.append(t)
            Vlist.append(v)
            Ulist.append(U)
    
            if (len(Slist) < 2):
                stable = True
            else:
                
                #At constant Volume, stability is found through dE/dT > 0.
                C_v = 1#(Ulist[1] - Ulist[0])/(Tlist[1] - Tlist[0])
                
                if(C_v > 0):
                    stable = True
                else:
                    stable = False
                
                #Reset the list so that we accurately calculate the stability 
                #for each point
                tmpU = Ulist[1]
                tmpT = Tlist[1]
                Ulist.clear()
                Tlist.clear()
                Ulist.append(tmpU)
                Tlist.append(tmpT)
            
            
            
            graph_data_class.plot_point(sv1, sv2, s, stable)
            
            
    graph_data_class.display()
    return Slist


    
    


    
main()