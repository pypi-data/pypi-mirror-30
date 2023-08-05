"""
test_isincell.py
DansCrystal
"""

import sys,os
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import convolve2d

# Add the current directory to path
propdir = os.path.abspath(os.path.dirname(__file__))+'/..'
if propdir not in sys.path:
    print('Adding to path: ''{}'''.format(propdir) )
    sys.path.insert(0,propdir)
from CrystalProgs import DansGeneralProgs as dgp
from CrystalProgs import DansCrystalProgs as dcp
from CrystalProgs import DansXrayProgs as dxp
from CrystalProgs.DansCrystal import Crystal

f = 'C:\Users\dgpor\Dropbox\Structure Files\Diamond.cif'
f = 'C:\Users\dgpor\Dropbox\Structure Files\Na0.8CoO2_P63mmc.cif'
f = "/home/i16user/Downloads/CrystalProgs/CrystalProgs/Na0.8CoO2_P63mmc.cif"
self = Crystal(f)

x_axis=[1,0,0]
y_axis=[0,1,0]
z_point=0.0
q_max=8.0
cut_width=0.05
background=1000
peak_width=0.1
        
# Determine the directions
x_axis = dgp.norm(x_axis)
y_axis = dgp.norm(y_axis)
z_axis = dgp.norm(np.cross( x_axis, y_axis ))

y_axis = np.cross(x_axis,z_axis) # make sure y is 90deg to x
z_point = z_axis*z_point

print x_axis
print y_axis
print z_axis
print z_point

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
mesh = np.zeros([pixels,pixels])
mesh_x = np.linspace(-q_max/2.0,q_max/2.0,pixels)
X,Y = np.meshgrid(mesh_x,mesh_x)
bkg = np.random.normal(background,np.sqrt(background), [pixels,pixels])

# add reflections to background
# scipy.interpolate.griddata?
pixel_coord = dgp.index_coordinates(Q, CELL)
pixel_coord = pixel_coord + 0.5
pixel_coord = (pixel_coord*pixels).astype(int)

mesh[pixel_coord[:,0],pixel_coord[:,1]] = I
#gauss = np.array([0,0.1,0.2,0.5,0.9,1,0.9,0.5,0.2,0.1,0])

gauss = np.array([[0,0,0,0,0], [0,0.1,0.5,0.1,0],[0,0.5,1,0.5,0],[0,0.1,0.5,0.1,0],[0,0,0,0,0]])

mesh = convolve2d(mesh,gauss, mode='same')

mesh = mesh+bkg



# create figure
plt.figure()
plt.pcolormesh(X,Y,mesh.T)
plt.axis('image')

#dcp.vecplot(self.Cell.UVstar())

print self.Cell.indexQ(x_axis)
print self.Cell.indexQ(y_axis)
print self.Cell.indexQ(z_axis)
xlab = str(dgp.norm(self.Cell.indexQ(x_axis)))
ylab = str(dgp.norm(self.Cell.indexQ(y_axis)))
zlab = str(dgp.norm(self.Cell.indexQ(z_axis)))

dgp.labels(str(z_point) + ' || ' +zlab,'Q || '+xlab,'Q || '+ylab)
plt.clim([0,10000])
plt.show()
