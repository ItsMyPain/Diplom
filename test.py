import os

from objects import *

R_bottom = 30
R_top = 20
H0 = 10
H1 = 20
H2 = 50
H_R = 0.5
H_H = 0.5
FILLER = 'RectNoReflectFiller'
CORRECTOR = f'ForceRectElasticBoundary{DIMS}D'


def par_par():
    h = 0.5
    p1 = Parallelepiped('P1', lg=10, w=10, h=10, h_l=h, h_w=h, h_h=h)
    p2 = Parallelepiped('P2', lg=20, w=20, h=20, z0=10, h_l=h, h_w=h, h_h=h)

    p2.data.add_impulse("test_impulse.txt", x=0.5, y=0.5, z=0.5)

    p3 = TwoParallelepiped('P3', p1, p2)
    p3.configure()
    p3.build()


def cyl():
    c1 = Cylinder('C1', r1=10, r2=15, h=10, h_r=0.5, h_h=0.5)
    c1.add_property(Filler, FILLER, ['XY'])
    c1.add_property(Corrector, CORRECTOR, ['XY'])
    # c1 = Cylinder('C1', r1=R_top, r2=R_top, h=H_H, h_r=H_R, h_h=H_H + 1)
    # c1.top.add_impulse("test_impulse.txt", x=0.5, y=0.5, z=0)
    # c1.left.add_impulse("test_impulse.txt", x=0.5, y=0.5, z=0)
    # c1.bottom.add_impulse("test_impulse.txt", x=0.5, y=0.9, z=0)
    # c1.right.add_impulse("test_impulse.txt", x=0.5, y=0.5, z=0)
    c1.center.data.add_impulse("test_impulse.txt", x=0.5, y=0.8, z=0.5)
    c1.configure()
    c1.build()


def col():
    parts = [(15, 10, 5), (10, 10, 10)]
    origin = (0, 0, 0)
    col1 = Column(f'col1', parts, origin=origin, h_r=0.25, h_h=0.25)
    col1.cylinders[1].right.add_impulse("test_impulse.txt", x=0.5, y=0.5, z=0.5)
    col1.add_property(Filler, FILLER, ['XY', 'Z1'])
    col1.add_property(Corrector, CORRECTOR, ['XY', 'Z1'])
    col1.configure()
    col1.build()


def par_cyl():
    c1 = Cylinder('C1', r1=10, h=20, h_r=0.25, h_h=0.25)
    p1 = Parallelepiped('P1', lg=30, w=30, h=20, z0=20, h_l=0.25, h_w=0.25, h_h=0.25)

    p1.data.add_impulse("test_impulse.txt", x=0.5, y=0.7, z=0.5)

    t1 = ParallelepipedCylinder('T1', p1, c1)
    t1.configure()
    t1.build()


def plat():
    parts = [(10, 5, 5), (5, 5, 10)]
    origins = [(25, 25, 5), (25, -25, 5), (-25, 25, 5), (-25, -25, 5)]
    cols = []
    for i, origin in enumerate(origins):
        cols.append(Column(f'col{i}', parts, origin=origin, h_r=H_R, h_h=H_H))

    cols[0].cylinders[0].top.add_impulse("source_rect_15Hz.txt", x=0.5, y=0.5, z=0.5)

    p1 = Parallelepiped('P1', lg=35, w=35, h=5, h_l=0.5, h_w=0.5, h_h=0.5)
    p2 = Parallelepiped('P2', lg=35, w=35, h=5, h_l=0.5, h_w=0.5, h_h=0.5, z0=20)
    pl = Platform('pl1', p1, p2, cols)

    pl.configure()
    pl.build()


if __name__ == '__main__':
    os.system("rm result/*.*")
    # par_par()
    # cyl()
    # col()
    # par_cyl()
    plat()
