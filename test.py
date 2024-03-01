import os

from objects import *

R_bottom = 30
R_top = 20
H0 = 10
H1 = 20
H2 = 50
H_R = 1
H_H = 1


def cyl():
    c1 = Cylinder('C2', r1=R_top, r2=R_bottom, h=H1, h_r=H_R, h_h=H_H)
    # c1 = Cylinder('C1', r1=R_top, r2=R_top, h=H_H, h_r=H_R, h_h=H_H + 1)
    # c1.top.add_impulse("test_impulse.txt", x=0.5, y=0.5, z=0)
    # c1.left.add_impulse("test_impulse.txt", x=0.5, y=0.5, z=0)
    # c1.bottom.add_impulse("test_impulse.txt", x=0.5, y=0.9, z=0)
    # c1.right.add_impulse("test_impulse.txt", x=0.5, y=0.5, z=0)
    c1.center.data.add_impulse("test_impulse.txt", x=0.5, y=0.5, z=0.5)
    c1.configure()
    # c1.center.data.sewed.add((2, 0))
    # c1.right.sewed.add((2, 0))
    # c1.left.sewed.add((2, 0))
    # c1.top.sewed.add((2, 0))
    # c1.bottom.sewed.add((2, 0))
    c1.update_config()
    c1.build()


def col():
    parts = [(R_bottom, R_top, H1), (R_top, R_top, H2)]
    origin = (0, 0, 0)
    col1 = Column(f'col', parts, origin=origin, h_r=H_R, h_h=H_H)
    col1.cylinders[1].right.add_impulse("test_impulse.txt", x=0.5, y=0.99, z=0.3)
    col1.configure()
    col1.update_config()
    col1.build()


def plat():
    parts = [(R_bottom, R_top, H1), (R_top, R_top, H2)]
    origins = [(50, 50, H0), (50, -50, H0), (-50, 50, H0), (-50, -50, H0)]
    cols = []
    for i, origin in enumerate(origins):
        cols.append(Column(f'col{i}', parts, origin=origin, h_r=H_R, h_h=H_H))
    # col1.cylinders[0].top.add_impulse("source_rect_15Hz.txt", x=0.5, y=0.5, z=0.5)

    p1 = Parallelepiped('P1', lg=150, w=150, h=10, z0=H0 + H1 + H2,
                        h_l=H_R, h_w=H_R, h_h=H_H)
    pl = Platform('pl1', p1, *cols)

    pl.configure()
    pl.build()

    # pl.update_config()

    # p1.data.sewed.remove((2, 0))
    # p1.update_config()


if __name__ == '__main__':
    os.system("rm result/*.*")
    # cyl()
    # col()
    # plat()

    p2 = Parallelepiped('P2', lg=180, w=180, h=10, h_l=H_R, h_w=H_R, h_h=H_H)
    p2.configure()
    p2.build()
    pass

# p1 = Parallelepiped('P1', lg=4 * R1, w=4 * R1, h=5, z0=H1, h_l=H_R, h_w=H_R, h_h=H_H)
# p1.data.add_impulse("source_rect_15Hz.txt", x=0.5, y=0.5, z=0.5)
# p1.configure()
# p1.build()

# c1 = Cylinder('C1', r1=R_top, r2=R_bottom, h=H1, h_r=H_R, h_h=H_H)
# c1.center.data.add_impulse("source_rect_15Hz.txt", x=0.5, y=0.5, z=0.8)
# c1.right.add_impulse("source_rect_15Hz.txt", x=0.5, y=0.8, z=0.5)
# c1.configure()
# c1.build()

# c2 = Cylinder('C2', r1=R_top, h=H2, z0=H1, h_r=H_R, h_h=H_H)
# c2.center.data.add_impulse("source_rect_15Hz.txt", x=0.5, y=0.5, z=0.5)
# c2.right.add_impulse("source_rect_15Hz.txt", x=0.5, y=0.8, z=0.2)
#
# c3 = Cylinder('C3', r1=R2, r2=R1, h=H1, z0=H1 + H2, h_r=H_R, h_h=H_H)
# c3.center.data.add_impulse("source_rect_15Hz.txt", x=0.5, y=0.5, z=0.5)


# col1 = Column('col1', c1, c2)
# p1 = Parallelepiped('P1', lg=4 * R_top, w=4 * R_top, h=5, z0=H1 + H2, h_l=H_R, h_w=H_R, h_h=H_H)
#
# pl = Platform('pl1', p1, col1)
# pl.configure()
# pl.build()
