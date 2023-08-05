"""
CrystalProgs Examples
Calculate list of reflections
"""

import sys,os
import numpy as np
import matplotlib.pyplot as plt # Plotting
from Dans_Diffraction import functions_general as fg
from Dans_Diffraction import functions_plotting as fp
from Dans_Diffraction import Crystal

cf=os.path.dirname(__file__)


f = cf+'/Ca2RuO4_Pbca.cif'

xtl = Crystal(f)
xtl.Atoms.changeatom(1,mxmymz=[0,3,0])
xtl.generate_structure()

xtl.Plot.plot_crystal()

#xtl._scattering_type = 'xray magnetic' # neutron magnetic
xtl.Scatter.setup_scatter(type='xray magnetic', energy_kev = 2.838, specular=[1,0,0], min_theta=-20, min_twotheta=0, max_twotheta=130)
print "X-Ray Magnetic Reflections"
xtl.Scatter.print_all_reflections(print_symmetric=True, min_intensity=0.1)

#xtl.Scatter.print_ref_reflections(min_intensity=0.1)


# L/S ratio
# From Neubeck et al., J. Phys. Chem. Solids 62, 2173-2180 (2001) egu. (2)
def LS(xtl,HKL,energy_kev=2.838,psi=0):
    theta = np.deg2rad(xtl.Cell.tth(HKL,energy_kev)/2)
    n1,n2,n3 = xtl.Scatter.scatteringcomponents([0,1,0], HKL, azim_zero=[0,1,0], psi=psi)
    Iss = np.sin(2*theta)*n2 # (sin2th)S2
    Isp = np.sin(2*theta)*(2*np.sin(theta)**2*(n2*1.2)) # sin2th[2inth^2 L2+S2]
    IspIss = Isp/Iss
    A = (1/np.sin(theta))*np.sqrt(n2**2/n1**2)
    B = np.tan(theta)*(n3/n1)
    LS = A*np.sqrt(IspIss) - B -1
    print
    print '(%1.0f,%1.0f,%1.0f) psi=%2.0f' %(HKL[0],HKL[1],HKL[2],psi)
    print '1/sin(th) = %5.2f  tan(th) = %5.2f' %(1/np.sin(theta),np.tan(theta))
    print '(n1,n2,n3) = (%5.2f,%5.2f,%5.2f)' %(n1,n2,n3)
    print 'Iss = %5.2f  Isp = %5.2f  Isp/Iss = %5.2f' % (Iss,Isp,IspIss)
    print 'A = %5.2f  B = %5.2f' %(A,B)
    print 'L/S = +/- %5.2f' % LS

"""
LS(xtl,[1,0,4],energy_kev=5,psi=0)
LS(xtl,[1,0,4],energy_kev=5,psi=90)
LS(xtl,[1,0,4],energy_kev=5,psi=45)

LS(xtl,[0,1,5],energy_kev=5,psi=0)
LS(xtl,[0,1,5],energy_kev=5,psi=90)
LS(xtl,[0,1,5],energy_kev=5,psi=45)

LS(xtl,[1,0,8],energy_kev=5,psi=0)
LS(xtl,[1,0,8],energy_kev=5,psi=90)
LS(xtl,[1,0,8],energy_kev=5,psi=45)
"""

LS(xtl,[1,0,4],energy_kev=5,psi=10)
LS(xtl,[0,1,5],energy_kev=5,psi=20)
LS(xtl,[1,0,6],energy_kev=5,psi=30)
LS(xtl,[0,1,7],energy_kev=5,psi=35)
LS(xtl,[1,0,8],energy_kev=5,psi=45)

