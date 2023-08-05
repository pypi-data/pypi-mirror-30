from __future__ import print_function

import numpy as np
import scipy as sp


def lambda_iak(rho, alpha, beta, kV=200.0):
    '''
    Inelastic mean free scattering length of electrons through a
    material with specific gravity rho using Iakabouvskii's method 
    from 2008, as documented in p298 of Egerton.
    
    Parameters
    ----------
    rho : scalar
        Specific gravity in g/cm^3.
    alpha : scalar
        Convergence semi-angle in mrad.
    beta : scalar
        Collect semi-anfle in mrad.
    kV : scalar, optional
        Accelerating voltage in kV.
   
    Returns
    -------
    lambda : scalar
        Inelastic mean free path length in nm
    
    '''
    
    F = (1.0+kV/1022.0) / (1+kV/511.0)**2
    d2 = np.abs(alpha**2 - beta**2)
    tc = 20.0
    te = 5.5*rho**0.3/(F*kV)
    a2 = alpha**2
    b2 = beta**2
    
    lnarg = (a2+b2+d2+2.0*te**2) / (a2+b2+d2+2.0*tc**2) * tc**2/te**2
    lam = 200.0*F*kV/(11.0*rho**0.3) / np.log(lnarg)

    return lam 


def e_lambda(kV=200.0, rel=True):
    '''
    Electron wavelength at acceleration voltage kV.
    
    Returns wavelength in metres. 
    
    Parameters
    ----------
    kV : scalar
        Accelerating voltage in kV.
    rel : bool, optional
        If True, use relativistic calculation, else use classical.
    
    Returns
    -------
    Wavelength : scalar
        Electron wavelength in meters.
    
    '''
    
    me = sp.constants.m_e
    h = sp.constants.h
    e = sp.constants.e
    c = sp.constants.c
    
    V = kV * 1000.0
    
    if rel:
        lam = h/np.sqrt(2*me*e*V*(1+e*V/(2*me*c**2)))
    else:
        lam = h/np.sqrt(2*me*e*V)
    return lam


def d_from_two_theta(two_theta, kV=200.0):
    '''
    d-spacing from deflection angle of Bragg scattered electron
    accelerated through voltage kV.
    
    Parameters
    ----------
    two_theta : scalar
        Deflection in mrad. The angle to the undeflected spot.
    kV : scalar, optional
        Electron accelerating voltage in kilovolts.
    
    Returns
    -------
    Returns d-spacing in nm.
    
    '''
    
    theta = np.asarray(two_theta, float)/2.0/1000
    lam_nm = e_lambda(kV, rel=True) * 1e9
    d = lam_nm/(2.0*np.sin(theta))
    
    return d


def hkl_cube(alpha, n=10, kV=200.0, struct='fcc', print_first=10):
    '''
    Compute diffraction parameters for a cubic lattice.
    
    Returns unique hkl values, d-spacing and deflection angles.
    
    Parameters
    ----------
    alpha : scalar
        Cube edge length in nm.
    n : integer, optional
        Number of values of each hkl to consider.
    kV : scalar, optional
        Electron accelerating voltage in kV.
    struct : string, optional
        String controlling structure of the cell.
        Only 'fcc' is currently understood.
    print_first : int
        Controls the printing of the calculated results. If non-zero, the first
        `print_first` lines are printed. 
    
    Returns
    -------
    Tuple of hkl, d, bragg_2t_mrad
    hkl : ndarray
        Sorted hkl of unique d-spacing.
    d : ndarray
        Sorted d-spacing in nm.
    bragg_2t_mrad: ndarray
        Deflection from the direct (undeviated) spot in mrad.
    
    '''
    
    import itertools
    hkl = np.asarray(list(itertools.product(list(range(n)),
                                            list(range(n)), 
                                            list(range(n)))))[1:,:]

    if struct == 'fcc':
        # fcc H,K,L all odd or all even
        n_odd = (hkl & 0x1).sum(-1)    # number of odd
        fcc_i = np.where(np.logical_or(n_odd == 3, n_odd == 0))[0]
        hkl = hkl[fcc_i, :]          # allowed
    else:
        print("Struct not supported, returning all reflections.")
        
    hkl2 = (hkl**2).sum(-1)     # sumsq
    hkl2_si = np.argsort(hkl2)  # index of increasing size
    hkl2s = hkl2[hkl2_si]       # sorted sumsq
    hkls = hkl[hkl2_si, :]      # sorted hkl
    hkl2s_u, hkl2s_i = np.unique(hkl2s, return_index=True)
    
    # unique reflection spacing
    d = alpha/hkl2s_u**0.5                  
    elam_nm = e_lambda(kV, rel=True)*1e9
    # mrad of angle from undeviated
    bragg_2t_mrad = 2*np.arcsin(elam_nm/(2*d))*1000
    
    hkl = hkls[hkl2s_i]
    
    if print_first:
        print_first = min(print_first, len(hkl))
        print('hkl      d (nm)  2theta (mrad)')
        print('-----------------------------')
        for i in range(print_first):
            print(hkl[i], ' %0.4f  %0.3f' %(d[i], bragg_2t_mrad[i]))
    
    return hkl, d, bragg_2t_mrad


def rutherford_cs(z, mrad=None, kV=200.0, plot=False):
    '''
    Relativistic screened rutherford differential cross-section, following
    equation 3.6 in chapter 3 of Williams and Carter.
    
    Parameters
    ----------
    z : 1-D iterable or scalar
        Element z-numbers.
    mrad : 1-D array or None
        Scattering angles used in the calculation. If None, 
        mrad = np.linspace(0, 100, 1000).
    kV : scalar
        Electron acceleration voltage in kV.
    plot : bool
        If True, the results are plotted.
    
    Returns
    -------
    tuple of dif_cs, mrad
    dif_cs : 
        Relativistically corrected rutherford differential cross-section in barns/rad.
        A barn is 1e-28 m**2.
    mrad : 1-D array
        See parameters.
    
    Examples
    --------
    Calculate cross-section for Ne, Al, and Fe.
    
    >>> import fpd
    >>> import matplotlib.pyplot as plt
    >>> plt.ion()
    
    >>> z = [10, 13, 26]
    >>> leg_txt = 'Ne Al Fe'.split()
    >>> 
    >>> dif_cs, mrad = fpd.tem_tools.rutherford_cs(z)
    
    >>> f, ax = plt.subplots(figsize=(4,3))
    >>> ax.loglog(mrad, dif_cs.T)
    >>> ax.set_xlabel('Angle (mrad)')
    >>> ax.set_ylabel('Differential cross-section (barns/rad)')
    >>> ax.legend(leg_txt, fontsize=10, loc=0)
    >>> plt.tight_layout()

    
    '''
    
    import scipy.constants as sc
    e = sc.e
    h = sc.h
    me = sc.m_e
    ep0 = sc.epsilon_0
    pi = sp.pi
    c = sc.c
    
    # condition inputs
    V = kV * 1e3
    
    if mrad is None:
        mrad = np.linspace(0, 100, 1000)
    rad = mrad / 1000.0
    
    import collections
    if not isinstance(z, collections.Iterable):
        z = [z]
    Z = np.array(z)[:,None]
    
    # relativistic screened calculation from W&C
    lam = e_lambda(kV, rel=True)
    a0 = h**2*ep0/(pi*me*e**2)  # (3.5)
    t0 = 0.117*Z**(1.0/3) / (kV)**0.5  # (3.4)
    
    dif_cs_dA = (Z*lam**2/(8.*pi**2*a0))**2 / (np.sin(rad/2.0)**2+(t0/2.0)**2)**2 # (3.6)
    dif_cs =  dif_cs_dA * 2*pi*np.sin(rad) 
    # convert to barns / rad
    dif_cs /= 1e-28
    
    if plot:
        import matplotlib.pyplot as plt
        plt.ion()
        
        f, ax = plt.subplots(figsize=(4,3))
        ax.loglog(mrad, dif_cs.T)
        ax.set_xlabel('Angle (mrad)')
        ax.set_ylabel('Differential cross-section (barns/rad)')
        leg_txt = [str(zi) for zi in Z]
        ax.legend(leg_txt, fontsize=10, loc=0)
        plt.tight_layout()
    
    return dif_cs, mrad

