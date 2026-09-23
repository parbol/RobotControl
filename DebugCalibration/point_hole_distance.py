import re
import pathlib
import click
import matplotlib.pyplot as plt
import numpy as np

#### Units
mm = 1

def generate_holes():
    # In top left corner
    init_x = -132 * mm
    init_y = -222 * mm

    n_holes_x = 23
    n_holes_y = 30

    step_x = 12 * mm
    step_y = 12 * mm

    holes = {}
    for ix in range(n_holes_x):
        for iy in range(n_holes_y):
            # I need to revert the axis to start counting from bottom right corner
            holes[(n_holes_x - ix - 1, n_holes_y - iy - 1)] = (init_x + step_x * ix, init_y - step_y * iy)

    return holes

def extract_position(file_name):
    pattern = re.compile(
        r"picture_col_(?P<col>\d+)"
        r"_row(?P<row>\d+)"
        r"_X_(?P<x>-?\d+\.\d+)"
        r"Y_(?P<y>-?\d+\.\d+)"
        r"Z_(?P<z>-?\d+\.\d+)"
        r"RZ_(?P<rz>-?\d+\.\d+)"
    )
    
    m = pattern.search(file_name)
    
    if m:
        col = int(m["col"])
        row = int(m["row"])
        x = float(m["x"])
        y = float(m["y"])
        z = float(m["z"])
        rz = float(m["rz"])
    
        # print(file_name)
        # print(col, row, x, y)
    return col, row, x, y, z, rz

@click.command()
@click.argument(
    "folder",
    type=click.Path(exists=True, file_okay=False, path_type=pathlib.Path),
)
def main(folder):
    file_names = sorted(folder.glob("*.png"))
    holes = generate_holes()

    plt.figure(figsize=(8, 6))
    for h in holes.values():
        plt.scatter(h[0], h[1], c="black", marker="o", s=5)
    plt.xlabel("X [mm]")
    plt.ylabel("Y [mm]")
    plt.gca().set_aspect("equal", adjustable="box")
    
    distances = []
    for file in file_names:
        col, row, x, y, z, rz = extract_position(file.name)
        x_nom, y_nom = holes[(col, row)]

        dx = x - x_nom
        dy = y - y_nom
        d = np.sqrt(dx**2 + dy**2)

        print(f"For {file}, extracted col={col}, row={row}, x={x}, y={y}. Nominal position ({x_nom}, {y_nom}). Distances dx={dx}, dy={dy}, d={d}")
        plt.scatter(x, y, c="blue", marker = "o", s=5)
        distances.append(d)
    plt.show()

    plt.hist(distances, bins = 200)
    plt.xlabel("Distance / mm")
    plt.show()


if __name__ == "__main__":
    main()

