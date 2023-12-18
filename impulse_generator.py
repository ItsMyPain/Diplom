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
#     return np.exp(-1e4 * np.power(t - 0.1, 2))

def f1(t):
    return np.exp(-1e5 * np.power(t - 0.02, 2)) - np.exp(-1e5 * np.power(t - 0.025, 2))


def generate_impulse(file):
    dt = 2.5e-05
    times = np.arange(0, 0.2, dt)
    values = f1(times)
    write(times, values, file)


def show(file):
    times, values = read(file)
    plt.plot(times, values)
    plt.show()


if __name__ == '__main__':
    generate_impulse('test_impulse.txt')
    show('test_impulse.txt')
    # show('source_rect_15Hz.txt')
