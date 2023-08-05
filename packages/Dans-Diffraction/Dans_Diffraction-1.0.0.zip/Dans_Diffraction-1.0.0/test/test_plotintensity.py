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
self = Crystal(f)

x_axis=[1,0,0]
y_axis=[0,1,0]
z_point=0.0
q_max=8.0
cut_width=0.05
background=0.001
peak_width=0.1
        
# Determine the directions
x_axis = dgp.norm(x_axis)
y_axis = dgp.norm(y_axis)
z_axis = dgp.norm(np.cross( x_axis, y_axis ))

y_axis = np.cross(x_axis,z_axis) # make sure y is 90deg to x
z_point = z_axis*z_point

# Generate lattice of reciprocal space points
hmax,kmax,lmax  = dcp.maxHKL(q_max,self.Cell.UVstar())
HKL = dcp.genHKL([hmax,-hmax],[kmax,-kmax],[lmax,-lmax])
Qm = self.Cell.Qmag(HKL)
HKL = HKL[Qm<=q_max,:]
Q = self.Cell.calculateQ(HKL)

print hmax,kmax,lmax
print len(HKL)

# generate box in reciprocal space
CELL = np.array([q_max*x_axis,q_max*y_axis,cut_width*z_axis])

# find reflections within this box
inplot = dgp.isincell(Q,z_point,CELL)
HKL = HKL[inplot,:]
Q = Q[inplot,:]

#dgp.newplot(Q[:,0],Q[:,1],'bo')

# Calculate intensities
I = self.intensity(HKL)

# create background mesh
pixels = 100
mesh_x = np.linspace(-q_max,q_max,pixels)
X,Y = np.meshgrid(mesh_x,mesh_x)
bkg = np.random.normal(background,np.sqrt(background), [pixels,pixels])

# add reflections to background
# scipy.interpolate.griddata?
pixel_coord = dgp.index_coordinates(Q, CELL)
pixel_coord = pixel_coord + 0.5
pixel_coord = (pixel_coord*pixels).astype(int)

bkg[pixel_coord[:,0],pixel_coord[:,1]] = bkg[pixel_coord[:,0],pixel_coord[:,1]] + I

# create figure
dgp.newplot()
plt.pcolormesh(X,Y,bkg)
dgp.labels(str(z_point),str(x_axis),str(y_axis))