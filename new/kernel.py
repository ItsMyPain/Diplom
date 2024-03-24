from pathlib import Path

import numpy as np

from .config import *
from .consts import *

directions_sew = Literal['X0', 'X1', 'Y0', 'Y1', 'Z0', 'Z1']
directions_boundary_cyl = Literal['XY', 'Z', 'Z0', 'Z1']


class Helper:
    commands: list[str]

    def __init__(self):
        self.commands = []

    def add_command(self, command: str):
        self.commands.append(command)

    def to_file(self, filename: str = PREPARE_FILE):
        with open(filename, 'w') as f:
            f.write('set -e\n')
            f.write('\n'.join(self.commands))
        print(PREPARE_ALL)

    def sew(self, grid1: Grid, grid1_path: str, grid2: Grid, grid2_path: str, ghost_from: directions_sew,
            ghost_to: directions_sew, ghosts: tuple[int, int], directory: str):
        main_config = f'"{grid1_path}"'
        obj_config = f'"{grid2_path}"'

        out_path = f"{directory}/{INTERP_DIR}"
        Path(out_path).mkdir(parents=True, exist_ok=True)

        output1 = f'"{directory}/{INTERP_DIR}/forward_{grid1.id}_{grid2.id}.txt"'
        output2 = f'"{directory}/{INTERP_DIR}/backward_{grid1.id}_{grid2.id}.txt"'

        with open(f'{TEMPLATE_INTERP_CFG}') as f:
            config = f.read()

        config = config.format(grid1.id, grid2.id, main_config, obj_config,
                               output1, output2, ghost_to, ghost_from, ghosts[0], ghosts[1])

        Path(f"{directory}/{INTERP_CFG_DIR}").mkdir(parents=True, exist_ok=True)
        config_filename = f"{directory}/{INTERP_CFG_DIR}/{grid1.id}_{grid2.id}.cfg"

        with open(config_filename, 'w') as f:
            f.write(config)

        comm1 = f"{INTERP_COMM1} {config_filename}"
        self.add_command(comm1)

        comm2 = f"{INTERP_COMM2} {config_filename}"
        self.add_command(comm2)

        return [Contact(RectGridInterpolationCorrector, grid1.id, grid2.id, interpolation_file=output1,
                        predictor_flag=True, corrector_flag=False, axis=1),
                Contact(RectGridInterpolationCorrector, grid2.id, grid1.id, interpolation_file=output2,
                        predictor_flag=False, corrector_flag=True, axis=1)]

    def contact(self, grid1: Grid, grid2: Grid, directory: str):
        output = f'"{directory}/{CONTACT_DIR}/{grid1.id}_{grid2.id}.txt"'

        with open(f'{CONTACT_CFG_DIR}/{CONTACT_CFG}') as f:
            config = f.read()

helper = Helper()


class Bins:
    id: str
    data: tuple[np.ndarray, np.ndarray, np.ndarray]

    def __init__(self, id: str, data: tuple[np.ndarray, np.ndarray, np.ndarray]):
        self.id = id
        self.data = data

    def save(self, directory: str):
        Path(f"{directory}/{BINS_DIR}").mkdir(parents=True, exist_ok=True)

        path_x = f"{directory}/{BINS_DIR}/{self.id}_x.bin"
        path_y = f"{directory}/{BINS_DIR}/{self.id}_y.bin"
        path_z = f"{directory}/{BINS_DIR}/{self.id}_z.bin"

        self.data[0].astype('f').tofile(path_x)
        self.data[1].astype('f').tofile(path_y)
        self.data[2].astype('f').tofile(path_z)

        return path_x, path_y, path_z


class Base:
    id: str
    configured: bool
    path: str | None
    grids: Grids
    contacts: Contacts

    def __init__(self, id: str):
        self.id = id
        self.configured = False
        self.path = None
        self.grids = Grids()
        self.contacts = Contacts()

    def save(self, directory: str):
        pass

    def reconfigure(self):
        with open(TEMPLATE_CONFIG, 'r') as f:
            config = f.read()

        config = config.format(
            self.grids.to_config(),
            self.contacts.to_config()
        )

        with open(self.path, 'w') as f:
            f.write(config)

    def configure(self, directory: str):
        Path(directory).mkdir(parents=True, exist_ok=True)
        self.path = f"{directory}/{self.id}.conf"
        self.save(directory)

        self.reconfigure()
        self.configured = True


class Parallelepiped(Base):
    grid: Grid

    def __init__(self, id: str, material: Material, lg, w, h, h_lg, h_w, h_h, x0=0.0, y0=0.0, z0=0.0):
        super().__init__(id)

        size_x = int(lg / h_lg) + 1
        size_y = int(w / h_w) + 1
        size_z = int(h / h_h) + 1

        h_lg = (lg + h_lg) / size_x
        h_w = (w + h_w) / size_y
        h_h = (h + h_h) / size_z

        origin_x = x0 - lg / 2
        origin_y = y0 - w / 2
        origin_z = z0

        self.grid = Grid(
            id=id,
            node=Node(ElasticMetaNode3D),
            material=material,
            factory=Factory(RectGridFactory,
                            size=(size_x, size_y, size_z),
                            origin=(origin_x, origin_y, origin_z),
                            spacing=(h_lg, h_w, h_h)),
            schema=Schema(ElasticRectSchema3DRusanov3),
        )

    def save(self, directory: str):
        self.grids = Grids([self.grid])

    def add_filler(self, name: str, where: list[directions_boundary], condition: Condition | None = None):
        self.grid.add_filler(name, where, condition)

    def add_corrector(self, name: str, where: list[directions_boundary], condition: Condition | None = None):
        self.grid.add_corrector(name, where, condition)


class Prism(Base):
    grid: Grid

    def __init__(self, id: str, material: Material, lg_d, w_d, lg_u, w_u, h, h_lg, h_w, h_h, x0=0.0, y0=0.0, z0=0.0):
        super().__init__(id)

        self.x0 = x0
        self.y0 = y0
        self.z0 = z0
        self.lg_d = lg_d
        self.w_d = w_d
        self.lg_u = lg_u
        self.w_u = w_u
        self.h = h
        self.h_lg = h_lg
        self.h_w = h_w
        self.h_h = h_h

        self.size_x = int(min(lg_d, lg_u) / h_lg) + 1
        self.size_y = int(min(w_d, w_u) / h_w) + 1
        self.size_z = int(h / h_h) + 1

        self.grid = Grid(
            id=id,
            node=Node(ElasticMetaNode3D),
            material=material,
            factory=Factory(BINGridFactory,
                            size=(self.size_x, self.size_y, self.size_z)),
            schema=Schema(ElasticCurveSchema3DRusanov3),
        )

    def save(self, directory: str):
        lg = min(self.lg_d, self.lg_u)
        w = min(self.w_d, self.w_u)

        x = np.linspace(-lg / 2, lg / 2, self.size_x)
        y = np.linspace(-w / 2, w / 2, self.size_y)
        z = self.z0 + np.linspace(0, self.h, self.size_z)

        if self.lg_d > self.lg_u:
            k1 = np.linspace(self.lg_d / self.lg_u, 1, self.size_z)
        else:
            k1 = np.linspace(1, self.lg_u / self.lg_d, self.size_z)

        if self.w_d > self.w_u:
            k2 = np.linspace(self.w_d / self.w_u, 1, self.size_z)
        else:
            k2 = np.linspace(1, self.w_u / self.w_d, self.size_z)

        x, y = np.meshgrid(x, y)
        _, zz = np.meshgrid(x, z)

        xx = self.x0 + np.outer(k1, x).flatten()
        yy = self.y0 + np.outer(k2, y).flatten()
        zz = zz.flatten()

        bins = Bins(self.grid.id, (xx, yy, zz))
        self.grid.factory.path_x, self.grid.factory.path_y, self.grid.factory.path_z = bins.save(directory)

        self.grids = Grids([self.grid])

    def add_filler(self, name: str, where: list[directions_boundary], condition: Condition | None = None):
        self.grid.add_filler(name, where, condition)

    def add_corrector(self, name: str, where: list[directions_boundary], condition: Condition | None = None):
        self.grid.add_corrector(name, where, condition)


class Cylinder(Base):
    center: Grid
    top: Grid
    bottom: Grid
    right: Grid
    left: Grid

    def __init__(self, id: str, material: Material, r_d, r_u, h, h_r, h_h, x0=0.0, y0=0.0, z0=0.0):
        super().__init__(id)

        self.material = material
        self.r_d = r_d
        self.r_u = r_u
        self.h = h
        self.h_r = h_r
        self.h_h = h_h
        self.x0 = x0
        self.y0 = y0
        self.z0 = z0

        if r_d == r_u:
            m = 2 * r_d / (1 + np.sqrt(2))
            self._center = Parallelepiped(f'{id}_center', material,
                                          lg=m, w=m, h=h,
                                          h_lg=h_r, h_w=h_r, h_h=h_h,
                                          x0=x0, y0=y0, z0=z0)
        else:
            md = 2 * r_d / (1 + np.sqrt(2))
            mu = 2 * r_u / (1 + np.sqrt(2))
            self._center = Prism(f'{id}_center', material,
                                 lg_d=md, w_d=md, lg_u=mu, w_u=mu, h=h,
                                 h_lg=h_r, h_w=h_r, h_h=h_h,
                                 x0=x0, y0=y0, z0=z0)

    def save(self, directory: str):
        self._center.save(directory)
        self.center = self._center.grid

        m1 = self.r_d / (1 + np.sqrt(2))
        m2 = self.r_u / (1 + np.sqrt(2))
        m = min(m1, m2)
        n = int(2 * m / self.h_r)

        y1 = m + np.arange(0, (m + self.h_r / 2) / np.sqrt(2), self.h_r / np.sqrt(2))
        y2 = m + np.arange(0, (m + self.h_r / 2) * np.sqrt(2), self.h_r * np.sqrt(2))
        a = 1 / (1 / np.power(y1, 2) - 1 / np.power(y2, 2))
        b = y2
        x1 = np.linspace(-y1, y1, n + 1, axis=1)

        size_x = n + 1
        size_y = a.shape[0]
        size_z = int(self.h / self.h_h) + 1

        if self.r_d >= self.r_u:
            k = np.linspace(self.r_d / self.r_u, 1, size_z)
        else:
            k = np.linspace(1, self.r_u / self.r_d, size_z)

        x_vert = x1.flatten()
        y_vert = (b * np.sqrt(1 - np.power(x1, 2).T / a)).T.flatten()
        x_gor = np.flip(x1, axis=1).flatten()
        y_gor = np.flip((b * np.sqrt(1 - np.power(x1, 2).T / a)).T, axis=1).flatten()

        z = self.z0 + np.linspace(0, self.h, size_z)

        _, zz = np.meshgrid(x_vert, z)

        xx_vert = np.outer(k, x_vert).flatten()
        yy_vert = np.outer(k, y_vert).flatten()

        xx_gor = np.outer(k, y_gor).flatten()
        yy_gor = np.outer(k, x_gor).flatten()

        zz = zz.flatten()

        bins_top = Bins(f'{self.id}_top', (self.x0 + xx_vert, self.y0 + yy_vert, zz))
        path_x_top, path_y_top, path_z_top = bins_top.save(directory)
        self.top = Grid(
            id=f'{self.id}_top',
            node=Node(ElasticMetaNode3D),
            material=self.material,
            factory=Factory(BINGridFactory,
                            size=(size_x, size_y, size_z),
                            path_x=path_x_top, path_y=path_y_top, path_z=path_z_top),
            schema=Schema(ElasticCurveSchema3DRusanov3),
        )

        bins_right = Bins(f'{self.id}_right', (self.x0 + xx_gor, self.y0 + yy_gor, zz))
        path_x_right, path_y_right, path_z_right = bins_right.save(directory)
        self.right = Grid(
            id=f'{self.id}_right',
            node=Node(ElasticMetaNode3D),
            material=self.material,
            factory=Factory(BINGridFactory,
                            size=(size_x, size_y, size_z),
                            path_x=path_x_right, path_y=path_y_right, path_z=path_z_right),
            schema=Schema(ElasticCurveSchema3DRusanov3),
        )

        bins_bottom = Bins(f'{self.id}_bottom', (self.x0 - xx_vert, self.y0 - yy_vert, zz))
        path_x_bottom, path_y_bottom, path_z_bottom = bins_bottom.save(directory)
        self.bottom = Grid(
            id=f'{self.id}_bottom',
            node=Node(ElasticMetaNode3D),
            material=self.material,
            factory=Factory(BINGridFactory,
                            size=(size_x, size_y, size_z),
                            path_x=path_x_bottom, path_y=path_y_bottom, path_z=path_z_bottom),
            schema=Schema(ElasticCurveSchema3DRusanov3),
        )

        bins_left = Bins(f'{self.id}_left', (self.x0 - xx_gor, self.y0 - yy_gor, zz))
        path_x_left, path_y_left, path_z_left = bins_left.save(directory)
        self.left = Grid(
            id=f'{self.id}_left',
            node=Node(ElasticMetaNode3D),
            material=self.material,
            factory=Factory(BINGridFactory,
                            size=(size_x, size_y, size_z),
                            path_x=path_x_left, path_y=path_y_left, path_z=path_z_left),
            schema=Schema(ElasticCurveSchema3DRusanov3),
        )
        contacts = []

        contacts.extend(helper.sew(self.top, self.path, self.left, self.path, 'X0', 'X1', (1, 1), directory))
        contacts.extend(helper.sew(self.left, self.path, self.bottom, self.path, 'X0', 'X1', (1, 1), directory))
        contacts.extend(helper.sew(self.bottom, self.path, self.right, self.path, 'X0', 'X1', (1, 1), directory))
        contacts.extend(helper.sew(self.right, self.path, self.top, self.path, 'X0', 'X1', (1, 1), directory))

        contacts.extend(helper.sew(self.center, self.path, self.top, self.path, 'Y1', 'Y0', (1, 1), directory))
        contacts.extend(helper.sew(self.center, self.path, self.left, self.path, 'X0', 'Y0', (1, 1), directory))
        contacts.extend(helper.sew(self.center, self.path, self.bottom, self.path, 'Y0', 'Y0', (1, 1), directory))
        contacts.extend(helper.sew(self.center, self.path, self.right, self.path, 'X1', 'Y0', (1, 1), directory))

        self.grids = Grids([self.center, self.top, self.bottom, self.right, self.left])
        self.contacts = Contacts(contacts)
        helper.to_file()

    def add_filler(self, name: str, where: list[directions_boundary_cyl], condition: Condition | None = None):
        for i in where:
            if i == 'XY':
                self.top.add_filler(name, 'Y1', condition)
                self.left.add_filler(name, 'Y1', condition)
                self.bottom.add_filler(name, 'Y1', condition)
                self.right.add_filler(name, 'Y1', condition)
            else:
                self.top.add_filler(name, i, condition)
                self.left.add_filler(name, i, condition)
                self.bottom.add_filler(name, i, condition)
                self.right.add_filler(name, i, condition)
                self.center.add_filler(name, i, condition)

    def add_corrector(self, name: str, where: list[directions_boundary_cyl], condition: Condition | None = None):
        for i in where:
            if i == 'XY':
                self.top.add_corrector(name, 'Y1', condition)
                self.left.add_corrector(name, 'Y1', condition)
                self.bottom.add_corrector(name, 'Y1', condition)
                self.right.add_corrector(name, 'Y1', condition)
            else:
                self.top.add_corrector(name, i, condition)
                self.left.add_corrector(name, i, condition)
                self.bottom.add_corrector(name, i, condition)
                self.right.add_corrector(name, i, condition)
                self.center.add_corrector(name, i, condition)
