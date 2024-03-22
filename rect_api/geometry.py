import numpy as np

from .config_parts import *


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


class Geometry:
    x: Axe
    y: Axe
    z: Axe
    filename: str
    path: str | None
    configured: bool
    impulse: None | Impulse
    fillers: list[Filler]
    correctors: list[Corrector]
    sewed: set[tuple[int, int]]

    def __init__(self, x: Axe, y: Axe, z: Axe, filename: str, impulse=None, fillers=None, correctors=None):
        if x.data.shape != y.data.shape or z.data.shape != y.data.shape:
            raise Exception("Не согласующиеся длины")
        self.x = x
        self.y = y
        self.z = z
        self.filename = filename
        self.path = None
        self.configured = False
        self.impulse = impulse
        self.sewed = set()
        if fillers is None:
            fillers = []
        if correctors is None:
            correctors = []
        self.fillers = fillers
        self.correctors = correctors

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

    def add_property(self, cls, name: str, where: str | list[str], condition: Condition | None = None):
        if isinstance(where, str):
            where = [where]
        if cls is Filler:
            data = self.fillers
        else:
            data = self.correctors
        for i in where:
            if i in AXES:
                data.append(cls(name, AXES[i], 0, condition))
                data.append(cls(name, AXES[i], 1, condition))
            else:
                data.append(cls(name, AXES[i[0]], int(i[1]), condition))

    def save(self, directory=''):
        path = f'{BINS_DIR}/{directory}'
        Path(path).mkdir(parents=True, exist_ok=True)
        self.x.save(f'{path}/{self.filename}_x.bin')
        self.y.save(f'{path}/{self.filename}_y.bin')
        self.z.save(f'{path}/{self.filename}_z.bin')

    def configure(self, directory='', reconfigure=False):
        if not reconfigure:
            self.save(f"{directory}/{self.filename}" if directory else self.filename)

        args = [
            self.filename,
            self.x.size, self.y.size, self.z.size,
            self.x.path, self.y.path, self.z.path,
            '\n'.join([i.to_config() for i in self.fillers])
        ]

        correctors = [i.to_config() for i in self.correctors]

        if self.impulse is not None:
            correctors.append(self.impulse.to_config())

        args.append('\n'.join(correctors))

        with open(f'{CONFIGS_DIR}/{BASE_CONF}') as f:
            config = f.read()

        config = config.format(*args)

        path = f"{CONFIGS_DIR}/{directory}" if directory else CONFIGS_DIR
        Path(path).mkdir(parents=True, exist_ok=True)
        self.path = f"{path}/{self.filename}.conf"

        with open(self.path, 'w') as f:
            f.write(config)

        self.configured = True

    def reconfigure(self, directory=''):
        if not self.configured:
            raise Exception("Геометрия не сконфигурирована")
        self.configure(directory=directory, reconfigure=True)

    def sew(self, obj: 'Geometry', ghost_from: Literal['X0', 'X1', 'Y0', 'Y1', 'Z0', 'Z1'],
            ghost_to: Literal['X0', 'X1', 'Y0', 'Y1', 'Z0', 'Z1'], ghosts: tuple[int, int],
            directory='') -> list[Contact]:
        """
        Метод, который пришивает переданную геометрию с помощью интерполяции.
        :param obj:         Геометрия для сшивки.
        :param ghost_from:  Ось и направление сшивки на исходной геометрии.
        :param ghost_to:    Ось и направление сшивки на переданной геометрии.
        :param ghosts:      Использовать ли ghost узлы для интерполяции.
        :param directory:   Директория, в которую будут сохранены данные.
        :return:            Два контакта - в прямом и обратном направлении.
        """
        if not isinstance(obj, Geometry):
            raise Exception("Неверный тип данных")
        if not self.configured or not obj.configured:
            raise Exception("Геометрия не сконфигурирована")

        direct = f"{directory}/" if directory else ""
        main_config = f'"{self.path}"'
        obj_config = f'"{obj.path}"'
        output1 = f'"{INTERP_DIR}/{direct}forward_{self.filename}_{obj.filename}.txt"'
        output2 = f'"{INTERP_DIR}/{direct}backward_{self.filename}_{obj.filename}.txt"'

        with open(f'{INTERP_CFG_DIR}/{INTERP_CFG}') as f:
            config = f.read()

        config = config.format(self.filename, obj.filename, main_config, obj_config,
                               output1, output2, ghost_to, ghost_from, ghosts[0], ghosts[1])

        path = f"{INTERP_CFG_DIR}/{directory}" if directory else CONFIGS_DIR
        Path(path).mkdir(parents=True, exist_ok=True)
        config_filename = f"{path}/{self.filename}_{obj.filename}.cfg"

        with open(config_filename, 'w') as f:
            f.write(config)

        out_path = f"{INTERP_DIR}/{directory}" if directory else INTERP_DIR
        Path(out_path).mkdir(parents=True, exist_ok=True)

        comm1 = f"{INTERP_COMM1} {config_filename}"
        helper.add_command(comm1)

        comm2 = f"{INTERP_COMM2} {config_filename}"
        helper.add_command(comm2)

        return [Contact(RectGridInterpolationCorrector, self.filename, obj.filename, interpolation_file=output1,
                        predictor_flag=True, corrector_flag=False, axis=1),
                Contact(RectGridInterpolationCorrector, obj.filename, self.filename, interpolation_file=output2,
                        predictor_flag=False, corrector_flag=True, axis=1)]

    def contact(self, obj: 'Geometry', directory='') -> Contact:
        """
        Метод, который создает контактную границу с переданной геометрией.
        :param obj:         Геометрия для сшивки.
        :param directory:   Директория, в которую будут сохранены данные.
        :return:            Контакт.
        """
        if not isinstance(obj, Geometry):
            raise Exception("Неверный тип данных")
        if not self.configured or not obj.configured:
            raise Exception("Геометрия не сконфигурирована")
        direct = f"{directory}/" if directory else ""
        output = f'"{CONTACT_DIR}/{direct}{self.filename}_{obj.filename}.txt"'

        with open(f'{CONTACT_CFG_DIR}/{CONTACT_CFG}') as f:
            config = f.read()

        config = config.format(self.filename, obj.filename, output,
                               self.x.size, self.y.size, self.z.size,
                               self.x.path, self.y.path, self.z.path,
                               obj.x.size, obj.y.size, obj.z.size,
                               obj.x.path, obj.y.path, obj.z.path)

        path = f"{CONTACT_CFG_DIR}/{directory}" if directory else CONTACT_CFG_DIR
        Path(path).mkdir(parents=True, exist_ok=True)
        config_filename = f"{path}/{self.filename}_{obj.filename}.cfg"

        with open(config_filename, 'w') as f:
            f.write(config)

        out_path = f"{CONTACT_DIR}/{directory}" if directory else CONTACT_DIR
        Path(out_path).mkdir(parents=True, exist_ok=True)

        comm = f"{CONTACT_COMM} {config_filename}"
        helper.add_command(comm)

        return Contact(GlueRectElasticContact, self.filename, obj.filename, contact_file=output)
