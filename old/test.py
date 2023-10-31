import numpy as np
from matplotlib import pyplot as plt

# x = np.array([1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3])
# y = np.array([1, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 2])
# z = np.array([0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1])


# x = np.array([1, 2, 3, 1, 2, 3])
# y = np.array([1, 1, 1, 2, 2, 2])
# z = np.array([0, 0, 0, 0, 0, 0])

# t = np.arange(-np.pi, np.pi, 0.1 * 2 * np.pi)
# r = np.arange(0.1, 1, 0.2).tolist()
#
# x = np.outer(r, np.cos(t)).flatten()
# y = np.outer(r, np.sin(t)).flatten()
# z = np.zeros(x.shape)
R = 2
L = 1
h = 0.2
y0 = 0
x0 = 0

xy = np.mgrid[-L:L + h / 2:h, -L:L + h / 2:h]
x = x0 + xy[0].flatten()
y = y0 + xy[1].flatten()
z = np.zeros(x.shape)

h_fi = np.pi * h / (4 * L)
fi = np.arange(np.pi / 4, 3 * np.pi / 4 + h_fi / 2, h_fi)
r = np.arange(0, R - L + h / 2, h)

xx1 = []
yy1 = []
for i in range(len(r)):
    xx1.extend((L + r[i]) * np.cos(fi))
    yy1.extend(L + (L + r[i]) * np.sin(fi))

xx1 = np.array(xx1)
yy1 = np.array(yy1)
zz1 = np.zeros(xx1.shape)

fi = np.arange(np.pi / 4, 3 * np.pi / 4 + h_fi / 2, h_fi)
xx2 = []
yy2 = []
for i in range(len(r)):
    xx2.extend((L + r[i]) * np.cos(fi))
    yy2.extend((L + r[i]) * np.sin(fi))

# xx = np.outer(r, np.cos(fi)).flatten()
# yy = np.outer(r, np.sin(fi)).flatten()
xx2 = np.array(xx2)
yy2 = np.array(yy2)
zz2 = np.zeros(xx2.shape)

# h_fi = np.pi * h / (4 * 2 * L)
#
#
#
# h_r = R * np.cos(fi)


print(x.shape)
print(len(set(x)))
print(len(set(y)))
print(len(set(z)))

# z = np.array([0, 1])
# x, _ = np.meshgrid(x, z)
# y, z = np.meshgrid(y, z)
# for i in range(len(r)):
#     x[i] = r[i] * np.cos(t)
#     y[i] = r[i] * np.sin(t)
#     z[i] = t


x.astype('f').tofile('x.bin')
y.astype('f').tofile('y.bin')
z.astype('f').tofile('z.bin')

# xx, zz = np.meshgrid(x.flatten(), z.flatten())
# yy, zz = np.meshgrid(y.flatten(), z.flatten())
# print(x.flatten().shape)
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(x.flatten(), y.flatten(), z.flatten())
ax.scatter(xx1.flatten(), yy1.flatten(), zz1.flatten())
ax.scatter(xx2.flatten(), yy2.flatten(), zz2.flatten())
ax.set_xlim3d(-2, 2)
ax.set_ylim3d(-2, 2)
plt.show()

#
# class Cone(Geometry):
#     def __init__(self, h, r_d, r_u, h_h=None, h_r=None, h_fi=None, x0=0, y0=0, z0=0):
#         super().__init__()
#         if h_h is None:
#             h_h = alpha * h
#         if h_r is None:
#             h_r = alpha * r_u
#         if h_fi is None:
#             h_fi = alpha * betta * 2 * np.pi
#
#         zz = np.arange(0, h + h_h / 2, h_h).tolist()
#         fi = np.arange(-np.pi, np.pi + h_fi / 2, h_fi)
#         k = (r_d - r_u) / h
#
#         x = np.array([])
#         y = np.array([])
#         z = np.array([])
#
#         for i in zz:
#             rr = np.arange(0, r_d - k * i + h_r / 2, h_r)
#             x = np.concatenate((x, x0 + np.outer(rr, np.cos(fi)).flatten()))
#             y = np.concatenate((y, y0 + np.outer(rr, np.sin(fi)).flatten()))
#             z = np.concatenate((z, np.full(len(rr) * len(fi), i)))
#
#         self.x = x.flatten()
#         self.y = y.flatten()
#         self.z = z.flatten()
