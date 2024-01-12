import pytest
import numpy as np
from robotinterface.logistics.grid import Grid
from robotinterface.logistics.positions import GridPosition, CartesianPosition


# Define a mock Pickable class
class Pickable:
    name = "Pickable"
    height = 10
    def __init__(self):
        self.id = 0


@pytest.fixture
def grid():
    test_grid = Grid(20, 2, 10, 2)
    yield test_grid


@pytest.fixture
def obj():
    obj = Pickable()
    yield obj


def test_grid_init(grid, obj):
    assert np.array_equal(grid.xx, np.arange(0, 20, 2))
    assert np.array_equal(grid.yy, np.arange(0, 10, 2))
    assert grid.x_num_interval == 10
    assert grid.y_num_interval == 5


def test_add_object(grid, obj):
    grid.add_object([obj], GridPosition(2, 4))
    assert grid.object_grid[4][2][0] is obj
    assert grid.height_grid[4][2] == 10

def test_add_object_multiple(grid, obj):
    grid.add_object([obj, obj], GridPosition(2, 4))
    assert grid.object_grid[4][2][0] is obj
    assert grid.object_grid[4][2][1] is obj
    assert grid.height_grid[4][2] == 20


def test_remove_object(grid, obj):
    grid.add_object([obj], GridPosition(2, 4))
    grid.remove_object([obj])
    assert grid.object_grid[4][2] == []
    assert grid.height_grid[4][2] == 0

def test_remove_object_multiple(grid, obj):
    grid.add_object([obj, obj], GridPosition(2, 4))
    grid.remove_object([obj, obj])
    assert grid.object_grid[4][2] == []
    assert grid.height_grid[4][2] == 0


def test_find_object(grid, obj):
    grid.add_object([obj], GridPosition(4, 2))
    assert grid.find_object(obj) == GridPosition(4, 2)


def test_find_object_max_position(grid, obj):
    pos = GridPosition(grid.x_num_interval - 1, grid.y_num_interval -1 )
    grid.add_object([obj], pos)
    assert grid.find_object(obj) == pos


def test_find_None_Object(grid, obj):
    assert grid.find_object(obj) is None


def test_find_stack_position(grid, obj):
    grid.add_object([obj], GridPosition(4, 2))
    assert grid.find_stack_position(obj, GridPosition(4, 2)) == 10


def test_find_stack_position_None(grid, obj):
    obj2 = Pickable()
    grid.add_object([obj], GridPosition(4, 2))
    grid.add_object([obj2], GridPosition(4, 2))
    assert grid.find_stack_position(obj, GridPosition(4, 2)) is None


def test_get_coordinates(grid, obj):
    grid.add_object([obj], GridPosition(2, 2))
    assert grid.get_coordinates(obj) == CartesianPosition(4, 4, 10)


def test_get_coordinates_from_grid(grid, obj):
    grid.add_object([obj], GridPosition(2, 4))
    assert grid.get_coordinates_from_grid(GridPosition(4, 2)) == (8, 4)
