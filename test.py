import os

from objects import *

R_bottom = 15
R_top = 10
H1 = 20
H2 = 30
H_R = 0.35
H_H = 0.35

os.system("rm result/*.*")


def par_col():
    parts = [(R_bottom, R_top, H1)]
    origin = (0, 0, 0)
    col = Column(f'col', parts, origin=origin, h_r=H_R, h_h=H_H)

    col.cylinders[0].bottom.add_impulse("source_rect_15Hz.txt", x=0.5, y=0.5, z=0.1)

    p1 = Parallelepiped('P1', lg=3 * R_top, w=3 * R_top, h=H1, z0=H1,
                        h_l=H_R, h_w=H_R, h_h=H_H)
    pl = Platform('pl1', p1, col)

    pl.configure()
    # pl.update_config()

    # p1.data.sewed.remove((2, 0))
    # p1.update_config()

    pl.build()


if __name__ == '__main__':
    par_col()

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