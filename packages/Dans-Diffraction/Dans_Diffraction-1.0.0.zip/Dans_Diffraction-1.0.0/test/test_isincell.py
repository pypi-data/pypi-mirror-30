"""
test_isincell.py
DansCrystal
"""

from CrystalProgs import DansGeneralProgs as dgp
from CrystalProgs import DansCrystalProgs as dcp
from CrystalProgs import DansXrayProgs as dxp
from CrystalProgs.DansCrystal import Crystal

f = 'C:\Users\dgpor\Dropbox\Structure Files\Diamond.cif'
f = 'C:\Users\dgpor\Dropbox\Structure Files\Na0.8CoO2_P63mmc.cif'
f = "C:\Users\grp66007\Dropbox\Structure Files\Na0.8CoO2_P63mmc.cif"
xtl = Crystal(f)

# Test isinbox
HKL=dcp.genHKL(2, 2, 5)
Q=xtl.Cell.calculateQ(HKL)
box_xyz=[-0.1,1.2,0.5]
box_size=[6,3,4]
box_rotation=[0,0,0]

A = np.asarray(Q,dtype=np.float).reshape((-1,3))
A = A - box_xyz
UV = np.eye(3)*box_size
UV = dgp.rot3D(UV,*box_rotation)
idx = dgp.index_coordinates(A,UV)
chk = np.all(np.abs(idx)<=0.5,axis=1)

for n in range(len(A)):
    print n,A[n],idx[n],chk[n]

dgp.newplot3(Q[:,0],Q[:,1],Q[:,2],'bo')
plt.gca().set_xlim([-5,5])
plt.gca().set_ylim([-5,5])
plt.gca().set_zlim([-5,5])

CELL = dgp.cell(box_size,box_rotation)
dgp.plot_cell(box_xyz, CELL)
iQ = dgp.isincell(Q, box_xyz, CELL)
plt.plot(Q[iQ,0],Q[iQ,1],Q[iQ,2],'ro')
