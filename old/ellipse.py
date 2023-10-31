import numpy as np
from matplotlib import pyplot as plt

R = 2
L = R / (1 + np.sqrt(2))
print(L)
h = 0.1
N = int(R / h)
print(N)

x = np.linspace(-L, L, N)
y = np.linspace(-L, L, N)
xy = np.meshgrid(x, y)
print(xy[0].shape, xy[0][0][0], xy[0][0][-1])
xx = xy[0].flatten()
yy = xy[1].flatten()

Y1 = L + np.arange(h / np.sqrt(2), (L + h / 2) / np.sqrt(2), h / np.sqrt(2))
Y2 = L + np.arange(h * np.sqrt(2), (L + h / 2) * np.sqrt(2), h * np.sqrt(2))
a = 1 / (1 / np.power(Y1, 2) - 1 / np.power(Y2, 2))
b = Y2

for i in range(a.shape[0]):
    x = np.linspace(-Y1[i], Y1[i], N)
    y_ud = b[i] * np.sqrt((1 - np.power(x, 2) / a[i]))
    x_lr = b[i] * np.sqrt((1 - np.power(x, 2) / a[i]))
    xx = np.concatenate((xx, x[:-1], x[1:], x_lr[1:], -x_lr[:-1]))
    yy = np.concatenate((yy, y_ud[:-1], -y_ud[1:], x[1:], x[:-1]))
    # xx = np.concatenate((xx, x, x, x_lr, -x_lr))
    # yy = np.concatenate((yy, y_ud, -y_ud, x, x))

zz = np.zeros(xx.shape)

xx.flatten().astype('f').tofile('x.bin')
yy.flatten().astype('f').tofile('y.bin')
zz.flatten().astype('f').tofile('z.bin')

print(len(set(xx)))
print(len(set(yy)))
print(len(set(zz)))

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(xx, yy, zz.flatten())
ax.set_xlim3d(-2, 2)
ax.set_ylim3d(-2, 2)
plt.show()
