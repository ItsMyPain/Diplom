from typing import Sequence

from .config_parts import *
from .geometry import Geometry, Axe, helper

alpha = 0.2


class Base:
    filename: str
    configured: bool
    path: str | None
    contacts: list[Contact]

    def __init__(self, filename: str, material: Material, *args, **kwargs):
        self.filename = filename
        self.material = material
        self.configured = False
        self.path = None

    def _check_configured(self, obj):
        if not self.configured or not obj.configured:
            raise Exception(f"Не сконфигурирован: {self.filename}")

    def _save_new_config(self, configs: Sequence, directory: str):
        grids = [f'    @include("{i.path}", "grids")' for i in configs]
        contacts = [f'    @include("{i.path}", "contacts")' for i in configs]
        contacts.extend([i.to_config() for i in self.contacts])

        with open(MAIN_CONF) as f:
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
        helper.add_command(comm)
        helper.to_file()


class NewParallelepiped(Base):
    data: Geometry

    def __init__(self, filename: str, material: Material, lg, w, h, h_l=None, h_w=None, h_h=None, x0=0.0, y0=0.0,
                 z0=0.0):
        super().__init__(filename, material)
        if h_l is None:
            h_l = alpha * lg
        if h_w is None:
            h_w = alpha * w
        if h_h is None:
            h_h = alpha * h

        size_x = int(lg / h_l) + 1
        size_y = int(w / h_w) + 1
        size_z = int(h / h_h) + 1

        self.data = Geometry(
            filename, material,
            Factory(RectGridFactory, Axe(size_x), Axe(size_y), Axe(size_z),
                    origin=(x0, y0, z0),
                    spacing=(h_l, h_w, h_h)),
            Schema(ElasticRectSchema3DRusanov3)
        )


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

        self.data = Geometry(Axe(xx, size_x), Axe(yy, size_y), Axe(zz, size_z), filename)

    def configure(self, directory=''):
        self.data.configure(f"{directory}/{self.filename}" if directory else self.filename)
        self.path = self.data.path
        self.configured = True

    def reconfigure(self, directory=''):
        self._check_configured(self)
        self.data.reconfigure(f"{directory}/{self.filename}" if directory else self.filename)
        self.path = self.data.path

    def add_property(self, cls, name: str, where: str | list[str], condition: Condition | None = None):
        self.data.add_property(cls, name, where, condition)

    def sew_geom(self, obj: Geometry, ghost_from: Literal['X0', 'X1', 'Y0', 'Y1', 'Z0', 'Z1'],
                 ghost_to: Literal['X0', 'X1', 'Y0', 'Y1', 'Z0', 'Z1'], ghosts: tuple[int, int], directory=''):
        self._check_configured(obj)
        return self.data.sew(obj, ghost_from, ghost_to, ghosts,
                             f"{directory}/{self.filename}" if directory else self.filename)

    def contact(self, obj: Geometry, directory=''):
        self._check_configured(obj)
        return self.data.contact(obj, f"{directory}/{self.filename}" if directory else self.filename)


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

        self.data = Geometry(Axe(xx.flatten(), size_x), Axe(yy.flatten(), size_y), Axe(zz.flatten(), size_z), filename)

    def configure(self, directory=''):
        self.data.configure(f"{directory}/{self.filename}" if directory else self.filename)
        self.path = self.data.path
        self.configured = True


class Cylinder(Base):
    center: Geometry
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
                                     x0=x0, y0=y0, z0=z0).data

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

        x_vert = x1.flatten()
        y_vert = (b * np.sqrt(1 - np.power(x1, 2).T / a)).T.flatten()
        x_gor = np.flip(x1, axis=1).flatten()
        y_gor = np.flip((b * np.sqrt(1 - np.power(x1, 2).T / a)).T, axis=1).flatten()

        z = z0 + np.linspace(0, h, size_z)

        _, zz = np.meshgrid(x_vert, z)

        xx_vert = np.outer(k, x_vert).flatten()
        yy_vert = np.outer(k, y_vert).flatten()

        xx_gor = np.outer(k, y_gor).flatten()
        yy_gor = np.outer(k, x_gor).flatten()

        zz = zz.flatten()

        self.top = Geometry(Axe(x0 + xx_vert, size_x), Axe(y0 + yy_vert, size_y), Axe(zz, size_z),
                            filename=f'{filename}_top')
        self.right = Geometry(Axe(x0 + xx_gor, size_x), Axe(y0 + yy_gor, size_y), Axe(zz, size_z),
                              filename=f'{filename}_right')
        self.bottom = Geometry(Axe(x0 - xx_vert, size_x), Axe(y0 - yy_vert, size_y), Axe(zz, size_z),
                               filename=f'{filename}_bottom')
        self.left = Geometry(Axe(x0 - xx_gor, size_x), Axe(y0 - yy_gor, size_y), Axe(zz, size_z),
                             filename=f'{filename}_left')

    def configure(self, directory=''):
        direct = f"{directory}/{self.filename}" if directory else self.filename

        self.center.configure(direct)
        self.top.configure(direct)
        self.bottom.configure(direct)
        self.right.configure(direct)
        self.left.configure(direct)

        contacts = []
        contacts.extend(self.top.sew(self.left, 'X0', 'X1', (1, 1), direct))
        contacts.extend(self.left.sew(self.bottom, 'X0', 'X1', (1, 1), direct))
        contacts.extend(self.bottom.sew(self.right, 'X0', 'X1', (1, 1), direct))
        contacts.extend(self.right.sew(self.top, 'X0', 'X1', (1, 1), direct))
        contacts.extend(self.center.sew(self.top, 'Y1', 'Y0', (1, 1), direct))
        contacts.extend(self.center.sew(self.left, 'X0', 'Y0', (1, 1), direct))
        contacts.extend(self.center.sew(self.bottom, 'Y0', 'Y0', (1, 1), direct))
        contacts.extend(self.center.sew(self.right, 'X1', 'Y0', (1, 1), direct))

        self.contacts = contacts

        self._save_new_config((self.top, self.left, self.bottom, self.right, self.center), directory)
        self.configured = True

    def reconfigure(self, directory=''):
        self._check_configured(self)
        direct = f"{directory}/{self.filename}" if directory else self.filename
        self.center.reconfigure(direct)
        self.top.reconfigure(direct)
        self.bottom.reconfigure(direct)
        self.right.reconfigure(direct)
        self.left.reconfigure(direct)

    def add_property(self, cls, name: str, where: list[Literal['Z', 'Z0', 'Z1', 'XY']],
                     condition: Condition | None = None):
        for i in where:
            if 'Z' in i:
                self.top.add_property(cls, name, i, condition)
                self.left.add_property(cls, name, i, condition)
                self.bottom.add_property(cls, name, i, condition)
                self.right.add_property(cls, name, i, condition)
                self.center.add_property(cls, name, i, condition)
            if i == 'XY':
                self.top.add_property(cls, name, 'Y1', condition)
                self.left.add_property(cls, name, 'Y1', condition)
                self.bottom.add_property(cls, name, 'Y1', condition)
                self.right.add_property(cls, name, 'Y1', condition)

    def sew_cyl(self, cylinder: 'Cylinder', ghost_from: Literal['Z0', 'Z1'], ghost_to: Literal['Z0', 'Z1'],
                ghosts: tuple[int, int], directory=''):
        super()._check_configured(cylinder)
        direct = f"{directory}/{self.filename}" if directory else self.filename

        contacts = []
        contacts.extend(self.center.sew(cylinder.center, ghost_from, ghost_to, ghosts, direct))
        contacts.extend(self.top.sew(cylinder.top, ghost_from, ghost_to, ghosts, direct))
        contacts.extend(self.right.sew(cylinder.right, ghost_from, ghost_to, ghosts, direct))
        contacts.extend(self.bottom.sew(cylinder.bottom, ghost_from, ghost_to, ghosts, direct))
        contacts.extend(self.left.sew(cylinder.left, ghost_from, ghost_to, ghosts, direct))

        return contacts

    def sew_par(self, parallelepiped: Parallelepiped, ghost_from: Literal['Z0', 'Z1'], ghost_to: Literal['Z0', 'Z1'],
                ghosts: tuple[int, int], directory=''):
        super()._check_configured(parallelepiped)
        direct = f"{directory}/{self.filename}" if directory else self.filename

        contacts = []
        contacts.extend(self.center.sew(parallelepiped.data, ghost_from, ghost_to, ghosts, direct))
        contacts.extend(self.top.sew(parallelepiped.data, ghost_from, ghost_to, ghosts, direct))
        contacts.extend(self.right.sew(parallelepiped.data, ghost_from, ghost_to, ghosts, direct))
        contacts.extend(self.bottom.sew(parallelepiped.data, ghost_from, ghost_to, ghosts, direct))
        contacts.extend(self.left.sew(parallelepiped.data, ghost_from, ghost_to, ghosts, direct))

        return contacts


class Column(Base):
    cylinders: list[Cylinder]

    def __init__(self, filename: str, parts: list[tuple], origin: tuple = (0, 0, 0), h_r: float = None,
                 h_h: float = None):
        super().__init__(filename)
        z = origin[2]
        self.cylinders = []
        for n, i in enumerate(parts):
            self.cylinders.append(Cylinder(filename=f'{filename}_cyl{n}', r1=i[1], r2=i[0], h=i[2], h_r=h_r, h_h=h_h,
                                           x0=origin[0], y0=origin[1], z0=z))
            z += i[2]

    def configure(self, directory=''):
        direct = f"{directory}/{self.filename}" if directory else self.filename

        for i in self.cylinders:
            i.configure(direct)

        contacts = []

        for i in range(len(self.cylinders) - 1):
            contacts.extend(
                self.cylinders[i].sew_cyl(self.cylinders[i + 1], 'Z1', 'Z0', (1, 1), direct)
            )

        self.contacts = contacts

        self._save_new_config(self.cylinders, directory)
        self.configured = True

    def reconfigure(self, directory=''):
        super()._check_configured(self)
        direct = f"{directory}/{self.filename}" if directory else self.filename
        for i in self.cylinders:
            i.reconfigure(direct)

    def add_property(self, cls: type, name: str, where: list[Literal['Z', 'Z0', 'Z1', 'XY']],
                     condition: Condition | None = None):
        for i in where:
            if i in ('Z', 'Z0'):
                self.cylinders[0].add_property(cls, name, ['Z0'], condition)
            if i in ('Z', 'Z1'):
                self.cylinders[-1].add_property(cls, name, ['Z1'], condition)
            if i == 'XY':
                for cyl in self.cylinders:
                    cyl.add_property(cls, name, ['XY'], condition)

    def sew_par(self, parallelepiped: Parallelepiped, ghost_from: Literal['Z0', 'Z1'], ghost_to: Literal['Z0', 'Z1'],
                ghosts: tuple[int, int], directory=''):
        if ghost_from == 'Z0':
            idx = 0
        else:
            idx = -1
        return self.cylinders[idx].sew_par(parallelepiped, ghost_from, ghost_to, ghosts, directory)
