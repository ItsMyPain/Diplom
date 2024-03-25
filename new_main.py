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

# mat = Material(2850.0, 1650.0, 2400.0)
# par = Parallelepiped('P1', mat, lg=30, w=30, h=10, h_lg=0.4, h_w=0.4, h_h=0.4, z0=5)
# cyl = Cylinder('C1', mat, r_d=7, r_u=7, h=5, h_r=0.3, h_h=0.3)
# par.grid.add_impulse('test_impulse.txt', x=0.5, y=0.8, z=0.5)
# parcyl = ParCyl('PC1', par, cyl)
# parcyl.configure(directory='projects')
# parcyl.build()

mat = Material(2850.0, 1650.0, 2400.0)
cyl_d = Cylinder('C1', mat, r_d=10, r_u=7, h=10, h_r=0.3, h_h=0.3)
cyl_u = Cylinder('C2', mat, r_d=7, r_u=7, h=15, h_r=0.3, h_h=0.3, z0=10)
col1 = Column('Col1', cyl_d, cyl_u)

col1.configure(directory='projects')

col1.cyl_d.right.add_impulse('test_impulse.txt', x=0.5, y=0.8, z=0.5)

col1.reconfigure()

col1.build()
