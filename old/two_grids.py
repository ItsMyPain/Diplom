import numpy as np
from matplotlib import pyplot as plt

R = 2
L = 1
h = 0.2

h_fi = np.pi * h / (4 * L)

fi = np.arange(-np.pi, np.pi, h_fi)
r = np.arange(L, R + h / 2, h)

x, y = np.mgrid[-L:L + h / 2:h, -L:L + h / 2:h]
# print(x.shape, r.shape)
x = x.flatten()
y = y.flatten()
# x = np.array([])
# y = np.array([])
print(r.shape, fi.shape)

xx = np.concatenate((x, np.outer(r, np.cos(fi)).flatten()))
yy = np.concatenate((y, np.outer(r, np.sin(fi)).flatten()))
zz = np.zeros(xx.shape)

xx.flatten().astype('f').tofile('x.bin')
yy.flatten().astype('f').tofile('y.bin')
zz.flatten().astype('f').tofile('z.bin')

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(xx, yy, zz.flatten())
ax.set_xlim3d(-2, 2)
ax.set_ylim3d(-2, 2)
plt.show()
