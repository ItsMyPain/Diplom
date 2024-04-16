import os

from new import Material, Cylinder, Parallelepiped, Column, Platform

os.system("rm result/*.*")

BETON = Material(3700.0, 3200.0, 2400.0)
SOIL = Material(2100.0, 2300.0, 1900.0)

CYL_D = (14, 8, 24)
CYL_U = (8, 8, 32)
ORIGINS = 28

GROUND = (110, 110, 15)
PAR_D = (94, 94, 12)
PAR_U = (85, 85, 10)

H_R = 0.25
H_H = 0.25
H_L = 0.25

columns = []

for n, origin in enumerate([(ORIGINS, ORIGINS), (ORIGINS, -ORIGINS), (-ORIGINS, -ORIGINS), (-ORIGINS, ORIGINS)]):
    cyl_d = Cylinder(f"cyl_d_{n}", BETON, *CYL_D, H_R, H_H, *origin, PAR_D[2])
    cyl_u = Cylinder(f"cyl_u_{n}", BETON, *CYL_U, H_R, H_H, *origin, PAR_D[2] + CYL_D[2])
    col = Column(f'col_{n}', cyl_d, cyl_u)
    columns.append(col)

ground = Parallelepiped('ground', SOIL, *GROUND, H_L, H_L, H_H, z0=-GROUND[2])
par_d = Parallelepiped('par_d', BETON, *PAR_D, H_L, H_L, H_H)
par_u = Parallelepiped('par_u', BETON, *PAR_U, H_L, H_L, H_H, z0=PAR_D[2] + CYL_D[2] + CYL_U[2])

platform = Platform('platform', ground, par_d, par_u, columns)

platform.configure('projects')

par_d.grid.add_impulse('riker_impulse.txt', x=0.5, y=0.8, z=0.5)

platform.reconfigure()
platform.build()
