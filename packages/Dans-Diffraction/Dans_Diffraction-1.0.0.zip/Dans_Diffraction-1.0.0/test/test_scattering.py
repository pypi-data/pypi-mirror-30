"""
main.py
DansCrystal
"""

from CrystalProgs import DansGeneralProgs as dgp
from CrystalProgs import DansCrystalProgs as dcp
from CrystalProgs import DansXrayProgs as dxp
from CrystalProgs.DansCrystal import Crystal,Multi_Crystal

dd= 'C:/Users/dgpor/Dropbox/Structure Files/'
#dd= 'C:/Users/grp66007/Dropbox/Structure Files/'



f = dd+'Na0.8CoO2_P63mmc.cif'

xtl = Crystal(f)

# AFM Magnetic structure
xtl.Structure.mz[:2]=[1,-1]
#xtl.Structure.mx[:2]=[1,-1]

hkl=[[1,0,0],[2,0,0],[0,1,0],[0,2,0],[1,1,0],[2,1,0],[0,0,1],[0,0,2],[1,0,1],[1,0,2],[2,0,1]]
xtl.Scatter.print_intensity(hkl)

blab
IN=xtl.Scatter.magnetic_neutron(hkl)*1e4
IX=xtl.Scatter.xray_magnetic(hkl)*1e4
IXRss=xtl.Scatter.xray_resonant(hkl, 8, 'ss')
IXRsp=xtl.Scatter.xray_resonant(hkl, 8, 'sp')
IXRps=xtl.Scatter.xray_resonant(hkl, 8, 'ps')
IXRpp=xtl.Scatter.xray_resonant(hkl, 8, 'pp')

fmt = '(%2.0f,%2.0f,%2.0f)  %8.4f  %8.4f  ss=%8.4f  sp=%8.4f  ps=%8.4f  pp=%8.4f'
print '( h, k, l)   Neutron      xray'
for n in range(len(hkl)):
    vals=(hkl[n][0],hkl[n][1],hkl[n][2],IX[n],IN[n],IXRss[n],IXRsp[n],IXRps[n],IXRpp[n])
    print fmt%vals
"""
hkl = [0,0,1]
psi = np.arange(-180,180,0.2)
azir = [1,0,0]
IXRss=xtl.Scatter.xray_resonant(hkl, 8, 'ss',azim_zero=azir,PSI=psi)
IXRsp=xtl.Scatter.xray_resonant(hkl, 8, 'sp',azim_zero=azir,PSI=psi)
IXRps=xtl.Scatter.xray_resonant(hkl, 8, 'ps',azim_zero=azir,PSI=psi)
IXRpp=xtl.Scatter.xray_resonant(hkl, 8, 'pp',azim_zero=azir,PSI=psi)

plt.figure()
plt.subplot(2,2,1)
plt.plot(psi,IXRss.T)
dgp.labels('Sigma-Sigma','psi [Deg]')

plt.subplot(2,2,2)
plt.plot(psi,IXRsp.T)
dgp.labels('Sigma-Pi','psi [Deg]')

plt.subplot(2,2,3)
plt.plot(psi,IXRps.T)
dgp.labels('Pi-Sigma','psi [Deg]')

plt.subplot(2,2,4)
plt.plot(psi,IXRpp.T)
dgp.labels('Pi-Pi','psi [Deg]')
"""