from pathlib import Path

import numpy as np

from .config import *

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

    @staticmethod
    def _check_configured(obj):
        if not obj.configured:
            raise Exception("Объект не сконфигурирован")

    def sew(self, grid1: Grid, grid1_path: str, grid2: Grid, grid2_path: str, ghost_from: directions_sew,
            ghost_to: directions_sew, ghosts: tuple[int, int], directory: str):
        main_config = f'"{grid1_path}"'
        obj_config = f'"{grid2_path}"'

        out_path = f"{directory}/{INTERP_DIR}"
        Path(out_path).mkdir(parents=True, exist_ok=True)

        output1 = f'"{directory}/{INTERP_DIR}/forward_{grid1.id}_{grid2.id}.txt"'
        output2 = f'"{directory}/{INTERP_DIR}/backward_{grid1.id}_{grid2.id}.txt"'

        with open(TEMPLATE_INTERP_CFG) as f:
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

    def sew_par_cyl(self, par: 'Parallelepiped', cyl: 'Cylinder', ghost_from: Literal['Z0', 'Z1'],
                    ghost_to: Literal['Z0', 'Z1'], ghosts: tuple[int, int], directory: str):
        self._check_configured(par)
        self._check_configured(cyl)

        contacts = []
        contacts.extend(self.sew(par.grid, par.path, cyl.center, cyl.path, ghost_from, ghost_to, ghosts, directory))
        contacts.extend(self.sew(par.grid, par.path, cyl.top, cyl.path, ghost_from, ghost_to, ghosts, directory))
        contacts.extend(self.sew(par.grid, par.path, cyl.right, cyl.path, ghost_from, ghost_to, ghosts, directory))
        contacts.extend(self.sew(par.grid, par.path, cyl.bottom, cyl.path, ghost_from, ghost_to, ghosts, directory))
        contacts.extend(self.sew(par.grid, par.path, cyl.left, cyl.path, ghost_from, ghost_to, ghosts, directory))

        return contacts

    def sew_cyl_cyl(self, cyl1: 'Cylinder', cyl2: 'Cylinder', ghost_from: Literal['Z0', 'Z1'],
                    ghost_to: Literal['Z0', 'Z1'], ghosts: tuple[int, int], directory: str):
        self._check_configured(cyl1)
        self._check_configured(cyl2)

        contacts = []
        contacts.extend(
            self.sew(cyl1.center, cyl1.path, cyl2.center, cyl2.path, ghost_from, ghost_to, ghosts, directory))
        contacts.extend(self.sew(cyl1.top, cyl1.path, cyl2.top, cyl2.path, ghost_from, ghost_to, ghosts, directory))
        contacts.extend(self.sew(cyl1.right, cyl1.path, cyl2.right, cyl2.path, ghost_from, ghost_to, ghosts, directory))
        contacts.extend(
            self.sew(cyl1.bottom, cyl1.path, cyl2.bottom, cyl2.path, ghost_from, ghost_to, ghosts, directory))
        contacts.extend(self.sew(cyl1.left, cyl1.path, cyl2.left, cyl2.path, ghost_from, ghost_to, ghosts, directory))

        return contacts

    def cut_boundary(self, grid: Grid, contacts: list[Contact], direction: Literal['forward', 'backward', 'contact'],
                     side: Literal['Z1', 'Z0'], directory: str) -> Condition:
        path = f"{directory}/{grid.id}/{BOUNDARY_DIR}"
        Path(path).mkdir(parents=True, exist_ok=True)
        out_file = f"{path}/erased_nodes.txt"

        if side == 'Z1':
            z = (grid.factory.size[2] - 1, grid.factory.size[2], grid.factory.size[2] + 1)
        else:
            z = (0, -1, -2)
        z = ' '.join(map(str, z))

        if hasattr(contacts[0], 'interpolation_file'):
            c_type = 'interpolation'
        else:
            c_type = 'contact'

        input_files = []
        for contact in contacts:
            if c_type == 'interpolation' and ((contact.grid1 == grid.id and direction == 'backward') or (
                    contact.grid2 == grid.id and direction == 'forward')):
                input_files.append(contact.interpolation_file[1:-1])
            if c_type == 'contact':
                input_files.append(contact.contact_file[1:-1])
        input_files = ' '.join(input_files)

        with open(TEMPLATE_CUT_BOUNDARY_CFG) as f:
            config = f.read()

        config = config.format(grid.id, out_file, z, c_type, input_files)

        Path(f"{directory}/{grid.id}/{BOUNDARY_CFG_DIR}").mkdir(parents=True, exist_ok=True)
        config_filename = f"{directory}/{grid.id}/{BOUNDARY_CFG_DIR}/{grid.id}.cfg"

        with open(config_filename, 'w') as f:
            f.write(config)

        self.add_command(f"python3 {BOUNDARY_CUTTER_V2} {config_filename}")

        return Condition(RectNodeMatchConditionNoneOf, RectNodeMatchConditionInFixedSet, out_file)

    def contact(self, grid1: Grid, grid2: Grid, directory: str):
        Path(f"{directory}/{CONTACT_DIR}").mkdir(parents=True, exist_ok=True)
        output = f'"{directory}/{CONTACT_DIR}/{grid1.id}_{grid2.id}.txt"'

        with open(TEMPLATE_CONTACT_CFG) as f:
            config = f.read()

        config = config.format(grid1.id, grid2.id, output, GlueRectElasticContact,
                               grid1.factory.to_config()[18:-18], grid2.factory.to_config()[18:-18])

        Path(f"{directory}/{CONTACT_CFG_DIR}").mkdir(parents=True, exist_ok=True)
        config_filename = f"{directory}/{CONTACT_CFG_DIR}/{grid1.id}_{grid2.id}.cfg"

        with open(config_filename, 'w') as f:
            f.write(config)

        comm = f"{CONTACT_COMM} {config_filename}"
        self.add_command(comm)

        return Contact(GlueRectElasticContact, grid1.id, grid2.id, contact_file=output)


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
    include: list[str]

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
        directory = f"{directory}/{self.id}"
        Path(directory).mkdir(parents=True, exist_ok=True)
        self.path = f"{directory}/{self.id}.conf"
        self.save(directory)

        self.reconfigure()
        self.configured = True

    def build(self):
        if not self.configured:
            raise Exception(f"Не конфигурирован: {self.id}")

        comm = f"{BUILD_COMM} {self.path}"
        helper.add_command(comm)
        helper.to_file()


class Parallelepiped(Base):
    grid: Grid

    def __init__(self, id: str, material: Material, lg, w, h, h_lg, h_w, h_h, x0=0.0, y0=0.0, z0=0.0):
        super().__init__(id)

        self.lg = lg
        self.w = w
        self.h = h
        self.h_lg = h_lg
        self.h_w = h_w
        self.h_h = h_h
        self.x0 = x0
        self.y0 = y0
        self.z0 = z0

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
                            spacing=(f'{h_lg:.10f}', f'{h_w:.10f}', f'{h_h:.10f}')),
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

        self.lg_d = lg_d
        self.w_d = w_d
        self.lg_u = lg_u
        self.w_u = w_u
        self.h = h
        self.h_lg = h_lg
        self.h_w = h_w
        self.h_h = h_h
        self.x0 = x0
        self.y0 = y0
        self.z0 = z0

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


class Ring(Base):
    grid: Grid

    def __init__(self, id: str, material: Material, r_id, r_od, r_iu, r_ou, h, h_r, h_h, x0=0.0, y0=0.0, z0=0.0):
        super().__init__(id)

        self.r_id = r_id
        self.r_od = r_od
        self.r_iu = r_iu
        self.r_ou = r_ou
        self.h = h
        self.h_r = h_r
        self.h_h = h_h
        self.x0 = x0
        self.y0 = y0
        self.z0 = z0

        self.size_x = int(2 * np.pi * max(r_id, r_od, r_iu, r_ou) / h_r) + 1
        self.size_y = int(max(r_od - r_id, r_ou - r_iu) / h_r) + 1
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
        fi = np.linspace(-np.pi, np.pi, self.size_x)

        r_u = np.linspace(self.r_iu, self.r_ou, self.size_y)
        r_d = np.linspace(self.r_id, self.r_od, self.size_y)

        x_u = self.x0 + np.outer(r_u, np.cos(fi))
        y_u = self.y0 + np.outer(r_u, np.sin(fi))
        x_d = self.x0 + np.outer(r_d, np.cos(fi))
        y_d = self.y0 + np.outer(r_d, np.sin(fi))

        z = self.z0 + np.linspace(self.h, 0, self.size_z)

        xx = np.linspace(x_u, x_d, self.size_z).flatten()
        yy = np.linspace(y_u, y_d, self.size_z).flatten()
        _, zz = np.meshgrid(x_u, z)
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

    def add_filler(self, name: str, where: list[directions_boundary_cyl], condition: Condition | None = None):
        for i in where:
            if i == 'XY':
                self.top.add_filler(name, 'Y1', condition)
                self.left.add_filler(name, 'Y1', condition)
                self.bottom.add_filler(name, 'Y1', condition)
                self.right.add_filler(name, 'Y1', condition)
            else:
                i: Literal['Z', 'Z0', 'Z1']
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
                i: Literal['Z', 'Z0', 'Z1']
                self.top.add_corrector(name, i, condition)
                self.left.add_corrector(name, i, condition)
                self.bottom.add_corrector(name, i, condition)
                self.right.add_corrector(name, i, condition)
                self.center.add_corrector(name, i, condition)


class Cylinder2(Base):
    center: Grid
    external: Grid

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
            self._center = Parallelepiped(f'{id}_center', material,
                                          lg=r_d, w=r_d, h=h,
                                          h_lg=h_r / 2, h_w=h_r / 2, h_h=h_h,
                                          x0=x0, y0=y0, z0=z0)
        else:
            self._center = Prism(f'{id}_center', material,
                                 lg_d=r_d, w_d=r_d, lg_u=r_u, w_u=r_u, h=h,
                                 h_lg=h_r / 2, h_w=h_r / 2, h_h=h_h,
                                 x0=x0, y0=y0, z0=z0)

        self._external = Ring(f'{id}_external', material,
                              r_id=r_d / 2, r_od=r_d, r_iu=r_u / 2, r_ou=r_u, h=h,
                              h_r=h_r, h_h=h_h,
                              x0=x0, y0=y0, z0=z0)

        self._external.add_filler(RectPeriodFiller, ['X'])

    def save(self, directory: str):
        self._center.save(directory)
        self.center = self._center.grid

        self._external.save(directory)
        self.external = self._external.grid

        contacts = []
        contacts.extend(helper.sew(self.center, self.path, self.external, self.path, 'X0', 'Y0', (1, 1), directory))
        contacts.extend(helper.sew(self.center, self.path, self.external, self.path, 'X1', 'Y0', (1, 1), directory))
        contacts.extend(helper.sew(self.center, self.path, self.external, self.path, 'Y0', 'Y0', (1, 1), directory))
        contacts.extend(helper.sew(self.center, self.path, self.external, self.path, 'Y1', 'Y0', (1, 1), directory))

        self.grids = Grids([self.center, self.external])
        self.contacts = Contacts(contacts)

    def add_filler(self, name: str, where: list[directions_boundary_cyl], condition: Condition | None = None):
        for i in where:
            if i == 'XY':
                self.external.add_filler(name, 'Y1', condition)
            else:
                i: Literal['Z', 'Z0', 'Z1']
                self.center.add_filler(name, i, condition)
                self.external.add_filler(name, i, condition)

    def add_corrector(self, name: str, where: list[directions_boundary_cyl], condition: Condition | None = None):
        for i in where:
            if i == 'XY':
                self.external.add_corrector(name, 'Y1', condition)
            else:
                i: Literal['Z', 'Z0', 'Z1']
                self.center.add_corrector(name, i, condition)
                self.external.add_corrector(name, i, condition)
