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



f = dd+'Na0.8CoO2_P63mmc.cif'

xtl = Crystal(f)

#P = [[2,-1,0],[1,3,0],[0,0,1]] # 1/7th Supercell
#P = [[-1,3,0],[4,3,0],[0,0,1]] # Square Supercell
P = [[3,0,0],[4,5,0],[0,0,1]] # Stripe Supercell
#P = [[1,3,0],[3,-1,0],[0,0,1]]
#P = [[2,0,0],[0,2,0],[0,0,1]] # Double supercell
#sup = xtl.generate_superstructure(P)

xtl.Atoms.occupancy[2]=0
xtl.Atoms.occupancy[3]=1
xtl.generate_structure()
sup = Superstructure(xtl,P)

# Stripe Cell
# Na1 6,7 16,17 26,27 36,37 46,47 56,57 66,67 76,77 86,87 96,97 106,107 116,117 126,127 136,137 146,147
# Na2 8,9 18,19 28,29 38,39 48,49 58,59 68,69 78,79 88,89 98,99 108,109 118,119 128,129 138,139 148,149
sup.Structure.occupancy[[6,16,26,76,86,96]] = 1 # Na1
sup.Structure.occupancy[[8,18,28,79,89,99]] = 0 # Na2

# Double Cell
# Na1 6,7 16,17 26,27 36,37 
# Na2 8,9 18,19 28,29 38,39 
#sup.Structure.occupancy[[6,27]] = 1 # Na1
#sup.Structure.occupancy[[8,29]] = 0 # Na2

#sup.Plot.simulate_hk0()


blab
t0 = clock()

Qx,Qy,HKL = sup.Cell.reciprocal_space_plane([1,0,0], [0,1,0], [0,0,0], 4, 0.1)
t1 = clock()
print 'Generate plane: %4.1f s' % (t1-t0)
pHKL = sup.hkl_parent(HKL)
t3 = clock()
print 'Index Q with parent: %4.1f s' % (t3-t1)
I = sup.intensity(HKL)
t4 = clock()
print 'Calculate I: %4.1f s' % (t4-t3)
symHKL,symI = sup.Parent.Symmetry.symmetric_intensity(pHKL,I)
t5 = clock()
print 'Generate symmetric I: %4.1f s' % (t5-t4)
symQ=sup.Parent.Cell.calculateQ(symHKL)
t6 = clock()
print 'Cal Q Parent: %4.1f s' % (t6-t5)

plt.figure()
#plt.plot(Qx,Qy,'o',ms=12)
plt.plot(symQ[:,0],symQ[:,1],'o',ms=8)
t7 = clock()
print 'Plot Points: %4.1f s' % (t7-t6)
plt.axis('image')
plt.axis([-4,4,-4,4])
pQx,pQy,parentHKL = sup.Parent.Cell.reciprocal_space_plane([1,0,0], [0,1,0], [0,0,0], 4, 0.1)
dcp.plot_lattice_lines(sup.Parent.Cell.calculateQ(parentHKL), sup.Parent.Cell.UVstar()[0], sup.Parent.Cell.UVstar()[1])
t8 = clock()
print 'Lattice Lines: %4.1f s' % (t8-t7)




"""
Qx,Qy,HKL = sup.Cell.reciprocal_space_plane([1,0,0], [0,1,0], [0,0,0], 4, 0.1)
I = sup.intensity(HKL)

Q = sup.Cell.calculateQ(HKL)
pHKL = sup.Parent.Cell.indexQ(Q)
symHKL,symI = sup.Parent.Symmetry.symmetric_intensity(pHKL,I)
symQ=sup.Parent.Cell.calculateQ(symHKL)
"""