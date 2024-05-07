import matplotlib.pyplot as plt
import numpy as np


def read(file):
    times = []
    values = []
    with open(file, 'r') as f:
        for line in f:
            t, v = line.strip().split()
            times.append(float(t))
            values.append(float(v))

    return times, values


def write(times, values, file):
    with open(file, 'w') as f:
        for t, v in zip(times, values):
            f.write(f'{t} {v}\n')


# def f1(t):
#     return np.exp(-1e6 * np.power(t - 0.01, 2))

def f1(t):
    return np.exp(-1e7 * np.power(t - 0.002, 2)) - np.exp(-1e7 * np.power(t - 0.003, 2))


def riker(f, t0, t):
    return (1 - 2 * np.power(np.pi * f * (t - t0), 2)) * np.exp(-np.power(np.pi * f * (t - t0), 2))


def generate_impulse(file):
    dt = 5e-06
    n = 2000
    t0 = 1e-03
    # n = 35000
    # t0 = 0.023
    times = np.arange(0, n * dt, dt)
    print(dt * n)
    # values = riker(10, t0, times)
    values = riker(1000, t0, times)
    write(times, values, file)


def show(file):
    times, values = read(file)
    plt.plot(times, values)
    plt.grid()
    plt.show()


if __name__ == '__main__':
    generate_impulse('riker_impulse.txt')
    show('riker_impulse.txt')
    # show('source_rect_15Hz.txt')
