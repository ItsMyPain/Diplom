import subprocess

import numpy as np
from matplotlib import pyplot as plt

alpha = 0.2
betta = 0.4


class Axe:
    data: np.array
    size: int
    path: str

    def __init__(self, data: np.array, size: int, path: str = ''):
        if len(data.shape) > 1:
            raise Exception(f"Неправильная размерность: {data.shape}")
        self.data = data
        self.size = size
        self.path = path


class Geometry:
    x: Axe
    y: Axe
    z: Axe

    def __init__(self, x: Axe, y: Axe, z: Axe, filename_bin=''):
        if x.data.shape != y.data.shape or z.data.shape != y.data.shape:
            raise Exception("Не согласующиеся длины")
        x.path = f'bins/x{filename_bin}'
        y.path = f'bins/y{filename_bin}'
        z.path = f'bins/z{filename_bin}'
        self.x = x
        self.y = y
        self.z = z

    def extend(self, obj: 'Geometry'):
        if obj.x.data.shape != obj.y.data.shape or obj.z.data.shape != obj.y.data.shape:
            raise Exception("Не согласующиеся длины")
        return Geometry(
            Axe(np.append(self.x.data, obj.x.data), self.x.size + obj.x.size),
            Axe(np.append(self.y.data, obj.y.data), self.y.size + obj.y.size),
            Axe(np.append(self.z.data, obj.z.data), self.z.size + obj.z.size)
        )

    def show(self, lim=False):
        print(self.x.data.shape)
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(self.x.data, self.y.data, self.z.data)
        if lim:
            ax.set_xlim3d(-10, 10)
            ax.set_ylim3d(-10, 10)
            ax.set_zlim3d(0, 10)
        plt.show()

    def save(self, filename_bin=''):
        self.x.data.astype('f').tofile(f'{self.x.path}{filename_bin}.bin')
        self.y.data.astype('f').tofile(f'{self.y.path}{filename_bin}.bin')
        self.z.data.astype('f').tofile(f'{self.z.path}{filename_bin}.bin')

    def to_vtk(self, filename: str, filename_bin=''):
        self.save(filename_bin)

        with open('template.conf') as f:
            config = f.read()

        if filename_bin is None:
            config = config.format(f'vtk/{filename}', self.x.size, self.y.size, self.z.size, self.x.path,
                                   self.y.path, self.z.path)
        else:
            config = config.format(f'vtk/{filename}', self.x.size, self.y.size, self.z.size,
                                   f'bins/x{filename_bin}.bin', f'bins/y{filename_bin}.bin',
                                   f'bins/z{filename_bin}.bin')

        with open(f"configs/{filename}.conf", 'w') as f:
            f.write(config)

        print(f"rect/rect/build/rect configs/{filename}.conf")
        proc = subprocess.run(["rect/rect/build/rect", f"configs/{filename}.conf"])
        if proc.returncode != 0:
            raise Exception(f"rect/rect/build/rect configs/{filename}.conf failed")


class Parallelepiped:
    data: Geometry

    def __init__(self, lg, w, h, lg2=None, w2=None, h_l=None, h_w=None, h_h=None, x0=0, y0=0, z0=0):
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

        size_x = int(lg / h_l) + 1
        size_y = int(w / h_w) + 1
        size_z = int(h / h_h) + 1

        x = x0 + np.linspace(-lg / 2, lg / 2, size_x)
        y = y0 + np.linspace(-w / 2, w / 2, size_y)
        z = z0 + np.linspace(0, h, size_z)

        k1 = np.linspace(1, lg2 / lg, size_z)
        k2 = np.linspace(1, w2 / w, size_z)

        x, y = np.meshgrid(x, y)
        _, zz = np.meshgrid(x, z)

        xx = np.outer(k1, x).flatten()
        yy = np.outer(k2, y).flatten()
        zz = zz.flatten()

        self.data = Geometry(Axe(xx, size_x), Axe(yy, size_y), Axe(zz, size_z))

    def to_vtk(self, filename: str, filename_bin='_p'):
        self.data.to_vtk(filename, filename_bin)

    def show(self, lim=False):
        self.data.show(lim)

    def save(self, filename_bin='_p'):
        self.data.save(filename_bin)


class Ring:
    data: Geometry

    def __init__(self, r1, r2, h, h_r=None, h_h=None, x0=0, y0=0, z0=0):
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

        self.data = Geometry(Axe(xx.flatten(), size_x), Axe(yy.flatten(), size_y), Axe(zz.flatten(), size_z))

    def to_vtk(self, filename: str, filename_bin='_r'):
        self.data.to_vtk(filename, filename_bin)

    def show(self, lim=False):
        self.data.show(lim)

    def save(self, filename_bin='_r'):
        self.data.save(filename_bin)


class Cylinder:
    center: Parallelepiped
    top: Geometry
    bottom: Geometry
    right: Geometry
    left: Geometry

    def __init__(self, r1, h, r2=None, h_r=None, h_h=None, x0=0, y0=0, z0=0):
        if r2 is None:
            r2 = r1
        if h_h is None:
            h_h = alpha * h
        if h_r is None:
            h_r = alpha * r1

        m = r1 / (1 + np.sqrt(2))
        n = int(2 * m / h_r)
        m2 = r2 / (1 + np.sqrt(2))

        self.center = Parallelepiped(lg=2 * m, w=2 * m, h=h, lg2=2 * m2, w2=2 * m2, h_l=h_r, h_w=h_r, h_h=h_h, x0=x0,
                                     y0=y0, z0=z0)

        y1 = m + np.arange(0, (m + h_r / 2) / np.sqrt(2), h_r / np.sqrt(2))
        y2 = m + np.arange(0, (m + h_r / 2) * np.sqrt(2), h_r * np.sqrt(2))
        a = 1 / (1 / np.power(y1, 2) - 1 / np.power(y2, 2))
        b = y2
        x1 = np.linspace(-y1, y1, n + 1, axis=1)

        size_x = n + 1
        size_y = a.shape[0]
        size_z = int(h / h_h) + 1

        k = np.linspace(1, r2 / r1, size_z)

        x = x1.flatten()
        y = (b * np.sqrt(1 - np.power(x1, 2).T / a)).T.flatten()
        z = z0 + np.linspace(0, h, size_z)

        _, zz = np.meshgrid(x, z)

        xx = np.outer(k, x).flatten()
        yy = np.outer(k, y).flatten()
        zz = zz.flatten()

        self.top = Geometry(Axe(x0 + xx, size_x), Axe(y0 + yy, size_y), Axe(zz, size_z))
        self.right = Geometry(Axe(x0 + yy, size_x), Axe(y0 + xx, size_y), Axe(zz, size_z))
        self.bottom = Geometry(Axe(x0 - xx, size_x), Axe(y0 - yy, size_y), Axe(zz, size_z))
        self.left = Geometry(Axe(x0 - yy, size_x), Axe(y0 - xx, size_y), Axe(zz, size_z))

    def to_vtk(self, filename: str, filename_bin='_cyl'):
        self.center.to_vtk(f"{filename}_center", filename_bin=f'{filename_bin}_center')
        self.top.to_vtk(f"{filename}_top", filename_bin=f'{filename_bin}_top')
        self.right.to_vtk(f"{filename}_right", filename_bin=f'{filename_bin}_right')
        self.bottom.to_vtk(f"{filename}_bottom", filename_bin=f'{filename_bin}_bottom')
        self.left.to_vtk(f"{filename}_left", filename_bin=f'{filename_bin}_left')

    def show(self, lim=False):
        data = self.center.data.extend(self.top).extend(self.right).extend(self.bottom).extend(self.left)
        data.show(lim)

    def save(self, filename_bin='_cyl'):
        self.center.save(f"{filename_bin}_center")
        self.top.save(f"{filename_bin}_top")
        self.right.save(f"{filename_bin}_right")
        self.bottom.save(f"{filename_bin}_bottom")
        self.left.save(f"{filename_bin}_left")


R1 = 3
R2 = 5
H1 = 1
H2 = 5
H_R = 0.2
H_H = 0.1

# c1 = Cylinder(R, H, x0=10, y0=10, h_r=0.1)
# c2 = Cylinder(R, H, x0=10, y0=-10)
# c3 = Cylinder(R, H, x0=-10, y0=-10)
# c4 = Cylinder(R, H, x0=-10, y0=10)
#
# c1.to_vtk('cylinder_1')
# c2.to_vtk('cylinder_2')
# c3.to_vtk('cylinder_3')
# c4.to_vtk('cylinder_4')

# p1 = Parallelepiped(7, 7, 1)
# p1.to_vtk('parallelepiped')
#
# r1 = Ring(5, 10, 1)
# r1.to_vtk('ring')

cn1 = Cylinder(r1=5, r2=10, h=5, h_r=0.2)
cn1.to_vtk('cone')
