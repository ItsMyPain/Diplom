import os

from objects import *

H_R = 0.35
H_H = 0.35

R_bottom_cyl = 15
R_top_cyl = 10
H_bottom_cyl = 15
H_top_cyl = 30

LN_platform = 100
WG_platform = 100
H_platform = 10

parts = [(R_bottom_cyl, R_top_cyl, H_bottom_cyl), (R_top_cyl, R_top_cyl, H_top_cyl)]
origins = [(30, 30, 0), (-30, 30, 0), (30, -30, 0), (-30, -30, 0)]
Z_platform = sum(i[2] for i in parts)

os.system("rm result/*.*")

# c2.center.data.add_impulse("source_rect_15Hz.txt", x=0.5, y=0.5, z=0.5)
columns = []

for n, i in enumerate(origins):
    columns.append(Column(f'col_{n}', parts, origin=i, h_r=H_R, h_h=H_H))

p1 = Parallelepiped('P1', lg=LN_platform, w=WG_platform, h=H_platform, z0=Z_platform,
                    h_l=H_R, h_w=H_R, h_h=H_H)

pl = Platform('pl1', p1, *columns)
pl.configure()
pl.build()
