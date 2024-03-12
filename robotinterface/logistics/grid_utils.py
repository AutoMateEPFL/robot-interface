if __name__ == "__main__":

    import os
    import sys
    import platform
    if platform.system() == 'Windows':
        sys.path.append(os.path.join(sys.path[0], '..'))

from logistics.grid import Grid
from logistics.positions import GridPosition
from logistics.non_pickable import PlateHolder
from logistics.pickable import *
import numpy as np



def fill_grid(grid : Grid, experiment_data) :
    '''
    Fill a grid with plateholders and petri dishes at the correct place
    Args :
        experiment_data : list of experiments and markers returned by using the interactive user interface
        grid
    '''
    # Compute number of plateholders and number of plates in the last stack
    max_plateholders = 8
    max_plates = 12
    number_plates = sum(len(experiment_data[i][2]) for i in range(len(experiment_data)))
    total_plateholders = int(np.ceil(number_plates/max_plates))
    if total_plateholders > max_plateholders :
        raise Exception('Problem with the program, too many plateholders')
    number_plates_last_stack = number_plates % max_plates

    #Fill the grid with plateholders and petri dishes
    for number_plateholder in range(total_plateholders) :
        # Compute position of plateholders
        x_id = 0 if number_plateholder in [0, 1, 2, 3] else 1
        y_id = number_plateholder if number_plateholder in [0, 1, 2, 3] else number_plateholder - 4
        grid_pos = GridPosition(x_id, y_id)
        # Add plateholders
        grid.add_object([PlateHolder()], grid_pos)
    # Add petri dishes, Start with the last experiment
    x_id = 0
    y_id = 0
    plates_in_plate_holder = 0
    for experiment in reversed(experiment_data) :
        experiment_name = experiment[1]
        plates_in_experiment = len(experiment[2])
        for plate in range(plates_in_experiment-1, -1, -1) :
            if plates_in_plate_holder >= max_plates :
                plates_in_plate_holder = 0
                if y_id == 3:
                    x_id = 1
                    y_id = 0
                else :
                    y_id += 1
            grid_pos = GridPosition(x_id, y_id)
            marker_name = experiment[2][plate]
            add_petridish(grid, grid_pos, number=plate, associated_name=marker_name, associated_experiment=experiment_name)
            plates_in_plate_holder += 1


# Add a petri dish (bottom and top) to a grid in a specified grid position
def add_petridish(grid : Grid, grid_pos : GridPosition, number="", associated_name="", brand="SARSTEDT", associated_experiment="") :
    grid.add_object([SmallPetriBottom(number=number, associated_name=associated_name, brand=brand, associated_experiment=associated_experiment),
                     SmallPetriTop(number=number, associated_name=associated_name, brand=brand, associated_experiment=associated_experiment)],
                     grid_pos)


if __name__ == "__main__":
    grid = Grid(x_max=-800, x_dist=-199, y_max=-620, y_dist=-200)
    # experiment_data = [(1, 'Oui', ['ori', 'ble', 'bsd', 'hyg', 'kan', 'nat', 'pat']), (2, 's', ['ori', 'ble', 'bsd', 'hyg', 'kan', 'nat', 'pat']), 
    #                    (3, 'sf', ['ori', 'ble', 'bsd', 'hyg', 'kan', 'nat', 'pat']), (4, 'f', ['ori', 'ble', 'bsd'])]   
    # experiment_data = [(1, 'Oui', ['ori', 'ble', 'bsd', 'hyg', 'kan']), (2, 'dd', ['ori', 'ble', 'bsd', 'hyg', 'kan']), 
    #                    (3, 'dd', ['ori', 'ble', 'bsd', 'hyg', 'kan', 'nat']), (4, 'd', ['ori', 'ble', 'bsd', 'hyg', 'kan', 'nat']), 
    #                    (5, 's', ['ori', 'ble', 'bsd', 'hyg', 'kan', 'nat'])]
    
    # experiment_data = [(1, 'Oui', ['ori', 'ble', 'bsd', 'hyg', 'kan', 'nat', 'pat']), (2, 'Non', ['ori', 'ble', 'bsd', 'hyg', 'kan', 'nat', 'pat']), 
    #                    (4, 'PoSD', ['ori', 'ble', 'bsd', 'hyg', 'kan', 'nat', 'pat']), (5, 'SDF', ['ori', 'ble', 'bsd', 'hyg', 'kan', 'nat', 'pat']), 
    #                    (6, 'Jhgc', ['ori', 'ble', 'bsd', 'hyg', 'kan', 'nat', 'pat']), (7, 'F', ['ori', 'bsd', 'hyg', 'kan', 'nat', 'pat'])]
    
    # experiment_data = [(1, 'a', ['ori', 'ble', 'bsd', 'hyg', 'kan', 'nat', 'pat']), (2, 'z', ['ori', 'ble', 'bsd', 'hyg', 'kan', 'nat', 'pat']), 
    #                    (3, 'e', ['ori', 'ble', 'bsd', 'hyg', 'kan', 'nat', 'pat']), (4, 'r', ['ori', 'ble', 'bsd', 'hyg', 'kan', 'nat', 'pat']), 
    #                    (5, 't', ['ori', 'ble', 'bsd', 'hyg', 'kan', 'nat', 'pat']), (6, 'y', ['ori', 'ble', 'bsd', 'hyg', 'kan', 'nat', 'pat'])]
    
    experiment_data = [(1, 'Oui', ['ori', 'ble', 'bsd', 'hyg', 'kan', 'nat', 'pat']), (2, 'Non', ['ori', 'ble', 'bsd', 'hyg', 'kan', 'nat', 'pat'])]

    fill_grid(grid, experiment_data)