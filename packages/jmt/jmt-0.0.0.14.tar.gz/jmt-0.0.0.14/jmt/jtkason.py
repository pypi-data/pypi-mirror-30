# -*- coding: utf-8 -*-
"""
Created on Thu Mar 15 16:11:42 2018

@author: jticotin
"""

def bend(thk,angle=90,kfactor=False,IR=.029):
    #finds the bend relief based on thickness and angle (90 deg default)
    #if kfactor=True: it will return kfactor instead of relief
    from math import pi
    
    #using k-factor:
    kfact=((2*(IR+thk)-1.67*thk)/(pi/2)-IR)/thk
    if kfactor: return kfact
    
    #using bend deduction: (default)
    relief = thk*1.67*angle/90
    return relief


def maxAmpP2P(RPM):
    '''based on RPM this will give the maximum amplitude based on 5g's acceleration
    This function is used to calculate minimum clearance (in) with moving parts
    
    Derivation
    F=m*a=m*omega^2*r-->a=omega**2*r=5*g-->r=5*g/omega^2
    omega=RPM*2*pi/60#convert from radial velocity to RPM
    combining we get
    r=5*g/(RPM*2*pi/60)**2
    '''
    from math import pi
    
    g=386.09# inches/s**2
    P2P=2*(5*g)/(RPM*2*pi/60)**2
    return P2P


def MotorAmpP2P(RPM=1200,CF=None,W=139,Wu=20,e=4):
    '''Calculates the motor amplitude Peak to Peak
    RPM = Rotations Per Minute
    CF = Centifugal Force (lbs)
    k= spring constant (lbs/in)
    W = weight on springs (lbs)
    Wu=unbalanced weigth (lbs)
    e=eccentric distance from ctr mass to ctr rotation (inches)
    
    example:
    MotorAmpP2P(RPM=1200,CF=1621,W=139)#out=0.570 
    MotorAmpP2P(W=139,Wu=19.8125,e=4)#out=.570
    
    Derivation using Centrifugal Force
    this comes from standard spring-mass damper formula
    X=(F0/k)*(1/sqrt((1-r**2)**2+(2*gamma*r)*2))
    r=radial freq / natural freq
    F0=centrifugal force, k=spring const,gamma=damping ratio
    assuming negligible damping, gamma=0, X simplifies to
    X=(F0/k)*(1/abs(1-W*(pi*RPM)**2/(g*k*900)))
    for high RPM, the W*(pi*RPM)**2/(g*k*900) term is much larger than 1.
    therefore we can simplify further:
    X=(F0*g*900)/(W*(RPM*pi)**2)
    
    Derivation using eccentrics/weight plates
    start with equation where gamma=0 (no damping)
    X=(F0/k)*(1/abs(1-W*(pi*RPM)**2/(g*k*900)))
    F0=Wu*e*(pi*RPM)**2/(g*900)
    combining and simplifying we get:
    X=Wu*e/W
    
    '''
    from math import pi
    
    if not CF:
        #calculate amplitude based on weight plates and eccentrics
        P2P=Wu*e/W
        return P2P
    
    #calculate amplitude based on centrifugal force
    P2P=2*CF*900*386.04/(W*(pi*RPM)**2)
    return P2P
    

def cone(OD,od,Ht,thk,sections=1):
    '''calculates the small/large radius and angle to make a cone flat pattern
    
    r,R,angle = cone(OD,od,Ht,thk,sections=1)
    OD=large od
    od=small od
    Ht = height
    thk = material thickness
    sections = how many sections for the cone (1 by default)
    
    output variables
    r=small radius
    R=large radius
    Angle=angle (deg)
    
    example
    cone(OD=9.925,od=8,Ht=.9625,thk=.078)
    cone(OD=9.925,od=8,Ht=.9625,thk=.078,sections=2)
    '''
    from math import sqrt
    dx=thk*Ht/sqrt((OD-od)**2+4*Ht**2)
    OD_adj=OD-2*dx
    od_adj=od-2*dx
    L=sqrt(Ht**2+.25*(OD-od)**2)
    r=L*od_adj/(OD_adj-od_adj)
    R=L+r
    angle=360*OD_adj/(sections*2*R)
    return r,R,angle
    
    
    