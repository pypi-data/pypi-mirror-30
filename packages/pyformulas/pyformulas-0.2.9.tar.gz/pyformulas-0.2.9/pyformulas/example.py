import pyformulas as pf
import numpy as np
import random

points = [ tuple(point) for point in list(np.random.random((10,2))) ]
starting_point = random.sample(points, 1)[0]
initial_path = [starting_point]

def expansion_fn(path):# Expands the current node
    remaining_points = [point for point in points if point not in path[1:]]

    child_paths = [path + [next_point] for next_point in remaining_points]

    last_point = np.array(path[-1])
    step_costs = [np.linalg.norm(child_path[-1] - last_point) for child_path in child_paths]

    return child_paths, step_costs

def goal_fn(path):# goal test
    return all(point in path[:-1] for point in points) and np.array_equal(path[-1], starting_point)

def heuristic_fn(path):# Basic heuristic: longest optimal shortcut path of length k=3
    remaining_points = [point for point in points if point not in path[1:]]

    last_point = np.array(path[-1])
    k
    if len(remaining_points) == 0:
        return 0
    elif len(remaining_points) == 1:
        return np.linalg.norm()

    return np.max([ np.linalg.norm( next_point - last_point) for next_point in remaining_points ])

print('Searching')
path = pf.discrete_search(initial_path, expansion_fn, goal_fn, heuristic_fn)[-1] # A*
print('Done')

import matplotlib.pyplot as plt

x, y = zip(*path)
plt.scatter(x, y)
plt.plot(x, y)
plt.plot(path[0][0], path[0][1], 'o', c='red')
plt.show()