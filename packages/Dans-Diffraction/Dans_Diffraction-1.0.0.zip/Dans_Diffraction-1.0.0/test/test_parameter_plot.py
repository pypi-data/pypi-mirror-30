"""
main.py
DansCrystal
"""

from CrystalProgs import DansGeneralProgs as dgp
from CrystalProgs import DansCrystalProgs as dcp
from CrystalProgs import DansXrayProgs as dxp
from CrystalProgs.DansCrystal import Crystal,Multi_Crystal,Superstructure
from time import clock

dd= 'C:/Users/dgpor/Dropbox/Structure Files/'
#dd= 'C:/Users/grp66007/Dropbox/Structure Files/'



f = dd+'LiNiO2.cif'

xtl = Crystal(f)
xtl.Atoms.addatom(0, 0, 0, 'Ni', 'Ni2', 0)

parameter_idx = -1
parameter_type = 'occupancy'
parameter_vals = np.arange(0,1.01,0.01)

parameter = getattr(xtl.Atoms,parameter_type)
QQ = np.zeros([len(parameter_vals),16000])
II = np.zeros([len(parameter_vals),16000])
for n in range(len(parameter_vals)):
    parameter[parameter_idx] = parameter_vals[n]
    xtl.generate_structure()
    Q,I = xtl.Plot.generate_powder()
    QQ[n,:] = Q
    II[n,:] = I

dgp.sliderplot(II, QQ, slidervals=parameter_vals)
ttl = '%s\n%s %s' %(xtl.name,xtl.Atoms.label[parameter_idx],parameter_type)
dgp.labels(ttl,'Q','I')