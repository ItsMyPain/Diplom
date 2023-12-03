import subprocess
from pathlib import Path
from typing import Sequence

import numpy as np

from geometry import Geometry, Axe, BUILD_COMM, CONFIGS_DIR

alpha = 0.2
betta = 0.4


class Base:
    filename: str
    configured: bool
    path: str | None

    def __init__(self, filename: str, *args, **kwargs):
        self.filename = filename
        self.configured = False
        self.path = None

    def _sew(self, obj):
        if not self.configured or not obj.configured:
            raise Exception(f"Не конфигурирован: {self.filename}")

    def _save_new_config(self, configs: Sequence, sews: list[tuple], directory: str):
        grids = [f'@include("{i.path}", "grids")' for i in configs]
        contacts = [f"""    [contact]
        name = RectGridInterpolationCorrector
        interpolation_file = {output2}
        grid1 = {overset}
        grid2 = {main}
        predictor_flag = false
        corrector_flag = true
        axis = 1
    [/contact]
    [contact]
        name = RectGridInterpolationCorrector
        interpolation_file = {output1}
        grid1 = {main}
        grid2 = {overset}
        predictor_flag = true
        corrector_flag = false
        axis = 1
    [/contact]""" for main, overset, output1, output2 in sews]

        old_contacts = [f'@include("{i.path}", "contacts")' for i in configs]
        contacts.extend(old_contacts)

        with open("main_template.conf") as f:
            config = f.read()

        config = config.format('\n'.join(grids), '\n'.join(contacts))

        path = f"{CONFIGS_DIR}/{directory}" if directory else CONFIGS_DIR
        Path(path).mkdir(parents=True, exist_ok=True)
        self.path = f"{path}/{self.filename}.conf"

        with open(self.path, 'w') as f:
            f.write(config)

    def build(self):
        if not self.configured:
            raise Exception(f"Не конфигурирован: {self.filename}")

        comm = f"{BUILD_COMM} {self.path}"
        print(comm)
        proc = subprocess.run(comm, shell=True)
        if proc.returncode != 0:
            raise Exception(comm)


class Parallelepiped(Base):
    data: Geometry

    def __init__(self, filename: str, lg, w, h, lg2=None, w2=None, h_l=None, h_w=None, h_h=None, x0=0.0, y0=0.0,
                 z0=0.0):
        super().__init__(filename)
        if lg2 is None:
            lg2 = lg
        if w2 is None:
            w2 = w
        if h_l is None:
            h_l = alpha * lg
        if h_w is None:
            h_w = alpha * w
        if h_h is None:
            h_h = alpha * h

        size_x = int(min(lg, lg2) / h_l) + 1
        size_y = int(min(w, w2) / h_w) + 1
        size_z = int(h / h_h) + 1

        x = np.linspace(-lg / 2, lg / 2, size_x)
        y = np.linspace(-w / 2, w / 2, size_y)
        z = z0 + np.linspace(0, h, size_z)

        k1 = np.linspace(lg2 / lg, 1, size_z)
        k2 = np.linspace(w2 / w, 1, size_z)

        x, y = np.meshgrid(x, y)
        _, zz = np.meshgrid(x, z)

        xx = x0 + np.outer(k1, x).flatten()
        yy = y0 + np.outer(k2, y).flatten()
        zz = zz.flatten()

        self.data = Geometry(Axe(xx, size_x), Axe(yy, size_y), Axe(zz, size_z), f'{filename}_data')

    def configure(self, directory=''):
        self.data.configure(f"{directory}/{self.filename}" if directory else self.filename)
        self.path = self.data.path
        self.configured = True

    def sew_geom(self, obj: Geometry, ghost_to: str, ghosts: tuple[int, int], direction: int, directory=''):
        super()._sew(obj)
        return self.data.sew(obj, ghost_to, ghosts, direction,
                             f"{directory}/{self.filename}" if directory else self.filename)

    def update_config(self):
        self.data.update_config()


class Ring(Base):
    data: Geometry

    def __init__(self, filename: str, r1, r2, h, h_r=None, h_h=None, x0=0, y0=0, z0=0):
        super().__init__(filename)
        if h_r is None:
            h_r = alpha * r1
        if h_h is None:
            h_h = alpha * h

        size_x = int(2 * np.pi * r2 / h_r) + 1
        size_y = int(r2 / h_r) + 1
        size_z = int(h / h_h) + 1

        fi = np.linspace(-np.pi, np.pi, size_x)
        r = np.linspace(r1, r2, size_y)

        x = x0 + np.outer(r, np.cos(fi)).flatten()
        y = y0 + np.outer(r, np.sin(fi)).flatten()
        z = z0 + np.linspace(0, h, size_z)

        xx, _ = np.meshgrid(x, z)
        yy, zz = np.meshgrid(y, z)

        self.data = Geometry(Axe(xx.flatten(), size_x), Axe(yy.flatten(), size_y), Axe(zz.flatten(), size_z),
                             f'{filename}_data')

    def configure(self, directory=''):
        self.data.configure(f"{directory}/{self.filename}" if directory else self.filename)
        self.path = self.data.path
        self.configured = True

    def update_config(self):
        self.data.update_config()


class Cylinder(Base):
    center: Parallelepiped
    top: Geometry
    bottom: Geometry
    right: Geometry
    left: Geometry

    def __init__(self, filename: str, r1, h, r2=None, h_r=None, h_h=None, x0=0.0, y0=0.0, z0=0.0):
        super().__init__(filename)
        if r2 is None:
            r2 = r1
        if h_h is None:
            h_h = alpha * h
        if h_r is None:
            h_r = alpha * r1

        m1 = r1 / (1 + np.sqrt(2))
        m2 = r2 / (1 + np.sqrt(2))
        m = min(m1, m2)
        n = int(2 * m / h_r)

        self.center = Parallelepiped(f'{filename}_center',
                                     lg=2 * m1, w=2 * m1, h=h, lg2=2 * m2, w2=2 * m2,
                                     h_l=h_r, h_w=h_r, h_h=h_h,
                                     x0=x0, y0=y0, z0=z0)

        y1 = m + np.arange(0, (m + h_r / 2) / np.sqrt(2), h_r / np.sqrt(2))
        y2 = m + np.arange(0, (m + h_r / 2) * np.sqrt(2), h_r * np.sqrt(2))
        a = 1 / (1 / np.power(y1, 2) - 1 / np.power(y2, 2))
        b = y2
        x1 = np.linspace(-y1, y1, n + 1, axis=1)

        size_x = n + 1
        size_y = a.shape[0]
        size_z = int(h / h_h) + 1

        if r2 >= r1:
            k = np.linspace(r2 / r1, 1, size_z)
        else:
            k = np.linspace(1, r1 / r2, size_z)

        x = x1.flatten()
        y = (b * np.sqrt(1 - np.power(x1, 2).T / a)).T.flatten()
        z = z0 + np.linspace(0, h, size_z)

        _, zz = np.meshgrid(x, z)

        xx = np.outer(k, x).flatten()
        yy = np.outer(k, y).flatten()
        zz = zz.flatten()

        self.top = Geometry(Axe(x0 + xx, size_x), Axe(y0 + yy, size_y), Axe(zz, size_z), f'{filename}_top')
        self.right = Geometry(Axe(x0 + yy, size_x), Axe(y0 + xx, size_y), Axe(zz, size_z), f'{filename}_right')
        self.bottom = Geometry(Axe(x0 - xx, size_x), Axe(y0 - yy, size_y), Axe(zz, size_z), f'{filename}_bottom')
        self.left = Geometry(Axe(x0 - yy, size_x), Axe(y0 - xx, size_y), Axe(zz, size_z), f'{filename}_left')

    def configure(self, directory=''):
        direct = f"{directory}/{self.filename}" if directory else self.filename

        self.center.configure(direct)
        self.top.configure(direct)
        self.bottom.configure(direct)
        self.right.configure(direct)
        self.left.configure(direct)

        sews = [self.top.sew(self.left, 'X0', (0, 1), 1, direct),
                self.left.sew(self.bottom, 'X0', (0, 1), 1, direct),
                self.bottom.sew(self.right, 'X0', (0, 1), 1, direct),
                self.right.sew(self.top, 'X0', (0, 1), 1, direct),
                self.center.sew_geom(self.top, 'Y0', (1, 0), 1, direct),
                self.center.sew_geom(self.left, 'Y0', (1, 0), 1, direct),
                self.center.sew_geom(self.bottom, 'Y0', (1, 0), 0, direct),
                self.center.sew_geom(self.right, 'Y0', (1, 0), 0, direct)
                ]

        self._save_new_config((self.top, self.left, self.bottom, self.right, self.center), sews, directory)

        self.configured = True

    def sew_cyl(self, cylinder: 'Cylinder', direction: int, directory=''):
        super()._sew(cylinder)
        direct = f"{directory}/{self.filename}" if directory else self.filename

        return [
            self.center.sew_geom(cylinder.center.data, 'Z0', (1, 0), direction, direct),
            self.top.sew(cylinder.top, 'Z0', (1, 0), direction, direct),
            self.right.sew(cylinder.right, 'Z0', (1, 0), direction, direct),
            self.bottom.sew(cylinder.bottom, 'Z0', (1, 0), direction, direct),
            self.left.sew(cylinder.left, 'Z0', (1, 0), direction, direct),
        ]

    def sew_par(self, parallelepiped: Parallelepiped, direction: int, directory=''):
        super()._sew(parallelepiped)
        direct = f"{directory}/{self.filename}" if directory else self.filename

        return [
            self.center.sew_geom(parallelepiped.data, 'Z0', (1, 1), direction, direct),
            self.top.sew(parallelepiped.data, 'Z0', (1, 1), direction, direct),
            self.right.sew(parallelepiped.data, 'Z0', (1, 1), direction, direct),
            self.bottom.sew(parallelepiped.data, 'Z0', (1, 1), direction, direct),
            self.left.sew(parallelepiped.data, 'Z0', (1, 1), direction, direct)
        ]

    def update_config(self):
        self.center.update_config()
        self.top.update_config()
        self.bottom.update_config()
        self.right.update_config()
        self.left.update_config()


class Column(Base):
    cylinders: list[Cylinder]

    def __init__(self, filename: str, parts: list[tuple], origin: tuple, h_r: float, h_h: float):
        super().__init__(filename)
        z = origin[2]
        self.cylinders = []
        for n, i in enumerate(parts):
            self.cylinders.append(Cylinder(filename=f'{filename}_cyl_{n}', r1=i[1], r2=i[0], h=i[2], h_r=h_r, h_h=h_h,
                                           x0=origin[0], y0=origin[1], z0=z))
            z += i[2]

    def configure(self, directory=''):
        direct = f"{directory}/{self.filename}" if directory else self.filename

        for i in self.cylinders:
            i.configure(direct)

        sews = []

        for i in range(len(self.cylinders) - 1):
            sews.extend(
                self.cylinders[i].sew_cyl(self.cylinders[i + 1], 1, direct)
            )

        self._save_new_config(self.cylinders, sews, directory)

        self.configured = True

    def update_config(self):
        for i in self.cylinders:
            i.update_config()


class Platform(Base):
    main: Parallelepiped
    columns: list[Column]
    pos: int

    def __init__(self, filename: str, main: Parallelepiped, *columns: Column, pos=-1):
        super().__init__(filename)
        self.main = main
        self.columns = list(columns)
        self.pos = pos

    def configure(self, directory=''):
        direct = f"{directory}/{self.filename}" if directory else self.filename

        self.main.configure(direct)

        for i in self.columns:
            i.configure(direct)

        sews = []

        for i in self.columns:
            sews.extend(i.cylinders[self.pos].sew_par(self.main, 1, direct))

        self._save_new_config((self.main, *self.columns), sews, directory)

        self.configured = True

    def update_config(self):
        self.main.update_config()
        for i in self.columns:
            i.update_config()
