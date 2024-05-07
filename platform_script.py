import os

from orm import Material, Cylinder, Parallelepiped, Column, Platform, Impulse

os.system("rm result/*.*")
os.system("rm mises/*.*")

SOIL = Material(2300.0, 1600.0, 1900.0)
BETON = Material(3700.0, 1900.0, 2400.0)

CYL_D = (14, 8, 24)
CYL_U = (8, 8, 32)
ORIGINS = 28

GROUND = (110, 110, 15)
PAR_D = (90, 90, 12)
PAR_U = (85, 85, 10)

H_R = 0.5
H_H = 0.5
H_L = 0.5

IMPULSE_CENTER = (-57, 0, -5)
IMPULSE_DIR = (1, 0, 1)
IMPULSE_MAGN = 1
IMPULSE = Impulse('riker_impulse.txt')

columns = []

for n, origin in enumerate([(ORIGINS, ORIGINS), (ORIGINS, -ORIGINS), (-ORIGINS, -ORIGINS), (-ORIGINS, ORIGINS)]):
    cyl_d = Cylinder(f"cyl_d_{n}", BETON, *CYL_D, H_R, H_H, *origin, GROUND[2] + PAR_D[2])
    cyl_u = Cylinder(f"cyl_u_{n}", BETON, *CYL_U, H_R, H_H, *origin, GROUND[2] + PAR_D[2] + CYL_D[2])
    col = Column(f'col_{n}', cyl_d, cyl_u)
    columns.append(col)

ground = Parallelepiped('ground', SOIL, *GROUND, H_L, H_L, H_H)
par_d = Parallelepiped('par_d', BETON, *PAR_D, H_L, H_L, H_H, z0=GROUND[2])
par_u = Parallelepiped('par_u', BETON, *PAR_U, H_L, H_L, H_H, z0=GROUND[2] + PAR_D[2] + CYL_D[2] + CYL_U[2])

platform = Platform('platform', ground, par_d, par_u, columns, IMPULSE_CENTER, IMPULSE_DIR, IMPULSE_MAGN, IMPULSE)

platform.configure('projects')

# par_d.grid.add_impulse('riker_impulse.txt', x=0.5, y=0.8, z=0.5)

platform.reconfigure()
platform.build()
