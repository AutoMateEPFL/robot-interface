
import os
import sys
import numpy as np

sys.path.append(os.path.join(sys.path[0], '..'))

from robotinterface.logistics.grid import Grid, GridPosition
from robotinterface.gui.user_gui import load_grid


grid = Grid(x_max=-800, x_dist=-199, y_max=-620, y_dist=-200)


grid.set_camera_position(GridPosition(2, 1))
grid.set_stack_positions([GridPosition(3, i) for i in range(0,4)]+[GridPosition(4, i) for i in range(0,4)])

# grid = load_grid(grid)

a = np.array([[4, 5,6 , 8, 9],[5, 2, 6, 5, 4],[5, 4,8 ,9, 6,]])
print(a)