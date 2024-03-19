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
    times = np.arange(0, 0.01, dt)
    print(times.shape[0])
    # values = f1(times)
    values = riker(1500, 0.00075, times)
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
