import os

from new.objects import *

os.system("rm mises/*.*")
os.system("rm result/*.*")


def par():
    mat = Material(2850.0, 1650.0, 2400.0, 300)
    par1 = Parallelepiped('P1', mat, lg=30, w=30, h=5, h_lg=0.5, h_w=0.5, h_h=0.5, z0=10)
    par1.configure(directory='.')

    par1.grid.add_impulse('test_impulse.txt', x=0.5, y=0.8, z=0.5)
    par1.grid.add_impulse('test_impulse.txt', x=0.5, y=0.2, z=0.5)
    par1.add_filler(RectNoReflectFiller, ['X', 'Y', 'Z'])
    par1.add_corrector(ForceRectElasticBoundary, ['X', 'Y', 'Z'])

    par1.reconfigure()
    par1.build()


def par_par():
    mat = Material(5850.0, 3650.0, 2700.0, 6e-7)
    par_d = Parallelepiped('P1', mat, lg=20, w=1, h=20, h_lg=0.5, h_w=0.5, h_h=0.5)
    par_u = Parallelepiped('P2', mat, lg=10, w=1, h=10, h_lg=0.5, h_w=0.5, h_h=0.5, z0=par_d.h)

    pp = ParPar('PP', par_d, par_u)
    pp.configure('.')

    par_d.grid.add_impulse('test_impulse.txt', x=0.5, y=0.8, z=0.5)

    pp.reconfigure()
    pp.build()


def par_contact():
    h = 0.25
    mat1 = Material(2850.0, 1650.0, 2400.0, 12e+6)
    par_d = Parallelepiped('P1', mat1, lg=50, w=1, h=20, h_lg=h, h_w=h, h_h=h)

    mat2 = Material(5850.0, 3650.0, 2700.0, 35e+6)
    par_u = Parallelepiped('P2', mat2, lg=25, w=1, h=20, h_lg=h, h_w=h, h_h=h, z0=par_d.h)

    pp_cont = ParParContact('PP_C', par_d, par_u)
    pp_cont.configure('.')

    # par_d.grid.add_impulse('riker_impulse.txt', x=0.5, y=0.8, z=0.5)
    # par_u.grid.add_impulse('test_impulse.txt', x=0.5, y=0.8, z=0.5)

    pp_cont.reconfigure()
    pp_cont.build()


def par_cyl():
    mat = Material(2850.0, 1650.0, 2400.0, 1)

    cyl = Cylinder('C1', mat, r_d=10, r_u=10, h=10, h_r=0.5, h_h=0.5)
    par1 = Parallelepiped('P1', mat, lg=30, w=30, h=5, h_lg=0.5, h_w=0.5, h_h=0.5, z0=10)

    parcyl = ParCyl('PC1', par1, cyl)
    parcyl.configure(directory='.')

    par1.grid.add_impulse('test_impulse.txt', x=0.5, y=0.8, z=0.5)

    parcyl.reconfigure()
    parcyl.build()


if __name__ == '__main__':
    # par()
    # par_par()
    par_contact()
    # par_cyl()
