import os

from orm.objects import *

os.system("rm mises/*.*")
os.system("rm result/*.*")

SOIL = Material(2300.0, 1600.0, 1900.0)
BETON = Material(3700.0, 1900.0, 2400.0)


def par():
    # mat = Material(2850.0, 1650.0, 2400.0, 300)
    par1 = Parallelepiped('P1', SOIL, lg=30, w=30, h=5, h_lg=0.5, h_w=0.5, h_h=0.5)
    par1.configure(directory='.')

    # par1.grid.add_impulse('test_impulse.txt', x=0.5, y=0.8, z=0.5)
    # par1.grid.add_impulse('test_impulse.txt', x=0.5, y=0.2, z=0.5)
    # par1.add_filler(RectNoReflectFiller, ['X', 'Y', 'Z'])
    # par1.add_corrector(ForceRectElasticBoundary, ['X', 'Y', 'Z'])

    imp = Impulse('riker_impulse.txt')
    par1.grid.add_filler(ElasticWaveFiller, ['X', 'Y', 'Z0'], center=(-16, 0, -2), direction=(1, 0, 1),
                         velocity_magnitude=5, impulse=imp)
    par1.add_filler(RectNoReflectFiller, ['Z1'])

    par1.add_corrector(ForceRectElasticBoundary, ['Z1'])

    par1.reconfigure()
    par1.build()


def ring():
    mat = Material(2850.0, 1650.0, 2400.0)
    ring1 = Ring('R1', mat, r_id=10, r_od=20, r_iu=10, r_ou=15, h=10, h_r=0.5, h_h=0.5)

    ring1.configure('.')

    ring1.add_filler('RectNoReflectFiller', ['Y', 'Z'])
    ring1.add_filler('RectPeriodFiller', ['X'])
    ring1.add_corrector('ForceRectElasticBoundary3D', ['Y', 'Z'])

    ring1.grid.add_impulse('riker_impulse.txt', x=0.7, y=0.5, z=1)

    ring1.reconfigure()
    ring1.build()


def cyl2():
    cl2 = Cylinder2('cyl2', BETON, r_d=15, r_u=10, h=10, h_r=0.5, h_h=0.5)
    cl2.configure('.')

    cl2.add_filler('RectNoReflectFiller', ['XY'])
    cl2.add_corrector('ForceRectElasticBoundary3D', ['XY'])
    cl2.center.add_impulse('riker_impulse.txt', x=0.7, y=0.5, z=0.9)

    cl2.reconfigure()
    cl2.build()


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
    h = 0.1
    par_d = Parallelepiped('P1', SOIL, lg=110, w=110, h=15, h_lg=h, h_w=h, h_h=h)
    par_u = Parallelepiped('P2', BETON, lg=94, w=94, h=12, h_lg=h, h_w=h, h_h=h, z0=par_d.h)

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
    # ring()
    cyl2()
    # par_par()
    # par_contact()
    # par_cyl()
