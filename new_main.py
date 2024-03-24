from new.kernel import *

mat = Material(2850.0, 1650.0, 2400.0)
cyl = Cylinder('C1', mat, r_d=15, r_u=15, h=20, h_r=0.3, h_h=0.3)

cyl.configure(directory='C1')

cyl.add_filler('RectNoReflectFiller', ['XY', 'Z0'])
cyl.add_corrector('ForceRectElasticBoundary3D', ['XY', 'Z0'])
cyl.right.add_impulse("test_impulse.txt", x=0.5, y=0.5, z=0.5)

cyl.reconfigure()
