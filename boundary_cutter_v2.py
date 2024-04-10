import argparse

parser = argparse.ArgumentParser("boundary_cutter")
parser.add_argument("config_file", type=str)
args = parser.parse_args()

config = args.config_file

with open(config) as f:
    grid = f.readline().split()[-1].strip()
    out_file = f.readline().split()[-1].strip()
    z = tuple(map(int, f.readline().split()[2:]))
    c_type = f.readline().split()[-1].strip()
    input_files = f.readline().split()[2:]

ind = [(0, 2), (3, 5)]
print(grid)
print(out_file)
print(z)
print(c_type)
print(input_files)

points = set()

if c_type == 'interpolation':
    for input_file in input_files:
        with open(input_file) as input_f:
            input_f.readline()
            input_f.readline()
            input_f.readline()
            for line in input_f:
                x_i, y_i = map(int, line.split()[:2])
                for z_i in z:
                    points.add((x_i, y_i, z_i))

elif c_type == 'contact':
    for input_file in input_files:
        with open(input_file) as input_f:
            grids = input_f.readline().split()
            if grid not in grids:
                raise Exception(f'Grid {grid} not in {grids}')
            sl = ind[grids.index(grid)]
            input_f.readline()
            for line in input_f:
                x_i, y_i = map(int, line.split()[sl[0]:sl[1]])
                for z_i in z:
                    points.add((x_i, y_i, z_i))

with open(out_file, 'w') as output_f:
    output_f.write(f'{len(points)}\n')
    for point in points:
        output_f.write(f'{point[0]} {point[1]} {point[2]}\n')