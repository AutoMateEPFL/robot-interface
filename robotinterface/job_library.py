import os
import sys
import platform
import logging
import asyncio

def find_al_experiments(grid):
    list_of_experiments = []
    for x in range(grid.x_num_interval):
        for y in range(grid.y_num_interval):
            if grid.object_grid[y][x] != []:
                print('grid', grid.object_grid[y][x][0])
                print(str(type(grid.object_grid[y][x][0])) == "<class 'logistics.pickable.PlateHolder'>")
                if str(type(grid.object_grid[y][x][0])) == "<class 'logistics.pickable.PlateHolder'>":
                    print('EXPERIMENT FOUND', x, y)
                    list_of_experiments.append(grid.object_grid[y][x][0])
    return list_of_experiments
async def take_photo_of_all_experiments_and_reconstruct_piles(robot, grid, pic_pos, stack_pos):

    # FIND ALL EXPERIMENTS IN THE GRID, FOR NOW ONE EXPERIMENT = ONE PLATEHOLDER

    list_of_experiments = find_al_experiments(grid)

    # FOR EACH EXPERIMENT TAKE PICTURES AND DECONSTRUCT THE PILE

    for experiment in list_of_experiments:
        pos_experiment = grid.find_object(experiment)
        x_exp, y_exp = pos_experiment.x_id, pos_experiment.y_id
        n_petri = (len(grid.object_grid[y_exp][x_exp]) - 1) // 2
        print("n petri", n_petri)
        print(grid.object_grid[y_exp][x_exp])
        for num in range(n_petri):
            object = grid.object_grid[y_exp][x_exp][-2]
            next_object = grid.object_grid[y_exp][x_exp][-1]
            if object.name == "Small Petri Bottom":
                if next_object.name == "Small Petri Top":
                    target = [object, next_object]
                else:
                    target = [object]
        print("TARGET", target)

            await robot.pick_and_place(target, pic_pos)

            await robot.take_picture(target[0], obj_rem=target[1], folder_name="", suffix="_"+str(target[0].name))
            await robot.pick_and_place(target, stack_pos)

        # RECONSTRUCT THE PILE ON THE INITIAL POS
        x_stack, y_stack = stack_pos.x_id, stack_pos.y_id
        for num in range(len(grid.object_grid[y_stack][x_stack]) // 2):
            object = grid.object_grid[y_stack][x_stack][-2]
            next_object = grid.object_grid[y_stack][x_stack][-1]
            if object.name == "Small Petri Bottom":
                if next_object.name == "Small Petri Top":
                    target = [object, next_object]
                else:
                    target = [object]
            await robot.pick_and_place(target, pos_experiment)

    await robot.shutdown()
