import subprocess
from pathlib import Path

import numpy as np

STDOUT = subprocess.DEVNULL
STDERR = subprocess.DEVNULL

BINS_DIR = 'bins'
CONFIGS_DIR = 'configs'
INTERP_CFG_DIR = 'interpolation_configs'
INTERP_DIR = 'interpolation'

INTERP_COMM1 = 'direction=1 interpolation=barycentric rect/rect/build/interpolation'
INTERP_COMM2 = 'direction=2 interpolation=barycentric rect/rect/build/interpolation'
BUILD_COMM = 'rect/rect/build/rect'


class Axe:
    data: np.array
    size: int
    path: str | None

    def __init__(self, data: np.array, size: int):
        if len(data.shape) > 1:
            raise Exception(f"Неправильная размерность: {data.shape}")
        self.data = data
        self.size = size
        self.path = None

    def save(self, filename: str):
        self.path = filename
        self.data.astype('f').tofile(filename)


class Impulse:
    x: int
    y: int
    z: int
    filename: str

    def __init__(self, x, y, z, filename):
        self.x = x
        self.y = y
        self.z = z
        self.filename = filename


class Geometry:
    x: Axe
    y: Axe
    z: Axe
    filename: str
    path: str | None
    configured: bool
    impulse: None | Impulse

    def __init__(self, x: Axe, y: Axe, z: Axe, filename: str, impulse=None):
        if x.data.shape != y.data.shape or z.data.shape != y.data.shape:
            raise Exception("Не согласующиеся длины")
        self.x = x
        self.y = y
        self.z = z
        self.filename = filename
        self.path = None
        self.configured = False
        self.impulse = impulse

    def add_impulse(self, filename: str, x: int | float = None, y: int | float = None, z: int | float = None):
        base = (self.x.size, self.y.size, self.z.size)
        old = [x, y, z]
        new = []
        for i, j in zip(base, old):
            if j is None:
                new.append(int(i / 2))
            elif isinstance(j, float):
                new.append(int(j * i))
            else:
                new.append(j)

        for i in zip(base, new):
            if i[0] < i[1]:
                raise Exception(f"Неправильная размерность: {i}")
        self.impulse = Impulse(*new, filename)

    def save(self, directory=''):
        path = f'{BINS_DIR}/{directory}'
        Path(path).mkdir(parents=True, exist_ok=True)
        self.x.save(f'{path}/{self.filename}_x.bin')
        self.y.save(f'{path}/{self.filename}_y.bin')
        self.z.save(f'{path}/{self.filename}_z.bin')

    def configure(self, directory=''):
        self.save(f"{directory}/{self.filename}" if directory else self.filename)

        args = [self.filename,
                self.x.size, self.y.size, self.z.size,
                self.x.path, self.y.path, self.z.path]

        if self.impulse is not None:
            args.append(f"""[corrector]
                name = PointSourceCorrector3D
                compression = 1.0
                gauss_w = 1
                index = {self.impulse.x}, {self.impulse.y}, {self.impulse.z}
                axis = 0
                [impulse]
                    name = FileInterpolationImpulse
                    [interpolator]
                        name = PiceWiceInterpolator1D
                        file = {self.impulse.filename}
                    [/interpolator]
                [/impulse]
            [/corrector]""")
        else:
            args.append("")

        with open(f'{CONFIGS_DIR}/template.conf') as f:
            config = f.read()

        config = config.format(*args)

        path = f"{CONFIGS_DIR}/{directory}" if directory else CONFIGS_DIR
        Path(path).mkdir(parents=True, exist_ok=True)
        self.path = f"{path}/{self.filename}.conf"

        with open(self.path, 'w') as f:
            f.write(config)

        self.configured = True

    def sew(self, obj: 'Geometry', ghost_to: str, ghosts: tuple[int, int], directory=''
            ) -> tuple[str, str, str, str]:
        if not isinstance(obj, Geometry):
            raise Exception("Неверный тип данных")
        if not self.configured or not obj.configured:
            raise Exception("Геометрия не сконфигурирована")

        direct = f"{directory}/" if directory else ""
        main_config = f'"{self.path}"'
        obj_config = f'"{obj.path}"'
        output1 = f'"{INTERP_DIR}/{direct}forward_{self.filename}_{obj.filename}.txt"'
        output2 = f'"{INTERP_DIR}/{direct}backward_{self.filename}_{obj.filename}.txt"'

        with open(f'{INTERP_CFG_DIR}/template.cfg') as f:
            config = f.read()

        config = config.format(self.filename, obj.filename, main_config, obj_config,
                               output1, output2, ghost_to, ghosts[0], ghosts[1])

        path = f"{INTERP_CFG_DIR}/{directory}" if directory else CONFIGS_DIR
        Path(path).mkdir(parents=True, exist_ok=True)
        config_filename = f"{path}/{self.filename}_{obj.filename}.cfg"

        with open(config_filename, 'w') as f:
            f.write(config)

        out_path = f"{INTERP_DIR}/{directory}" if directory else INTERP_DIR
        Path(out_path).mkdir(parents=True, exist_ok=True)

        comm1 = f"{INTERP_COMM1} {config_filename}"
        print(comm1)
        proc = subprocess.run(comm1, shell=True, stdout=STDOUT, stderr=STDERR)
        if proc.returncode != 0:
            raise Exception(comm1)

        comm2 = f"{INTERP_COMM2} {config_filename}"
        print(comm2)
        proc = subprocess.run(comm2, shell=True, stdout=STDOUT, stderr=STDERR)
        if proc.returncode != 0:
            raise Exception(comm2)

        return self.filename, obj.filename, output1, output2