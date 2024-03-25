import os

from new.objects import *

os.system("rm result/*.*")

# mat = Material(2850.0, 1650.0, 2400.0)
# cyl = Cylinder('C1', mat, r_d=15, r_u=15, h=20, h_r=0.3, h_h=0.3)
#
# cyl.configure(directory='C1')
#
# cyl.add_filler('RectNoReflectFiller', ['XY', 'Z0'])
# cyl.add_corrector('ForceRectElasticBoundary3D', ['XY', 'Z0'])
# cyl.right.add_impulse("test_impulse.txt", x=0.5, y=0.5, z=0.5)
#
# cyl.reconfigure()

mat = Material(2850.0, 1650.0, 2400.0)
par = Parallelepiped('P1', mat, lg=20, w=20, h=10, h_lg=0.4, h_w=0.4, h_h=0.4, z0=20)
cyl = Cylinder('C1', mat, r_d=7, r_u=7, h=20, h_r=0.4, h_h=0.4)
par.grid.add_impulse('test_impulse.txt', x=0.5, y=0.5, z=0.5)
parcyl = ParCyl('PC1', par, cyl)
parcyl.configure(directory='.')
helper.to_file()
# prism = Prism('P2')
