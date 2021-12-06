import sys
sys.path.insert(0, '.')
from thpo.data_utils import get_evaluator, get_all_parameters, get_value
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

path = './input/data-30'
#path = './input/data-2'
evaluator = get_evaluator(path)

name_list = evaluator.dims  # all parameter names
parameters_config = evaluator.parameters_config

last_in_range = np.array([0] * 14, dtype=float)
both_in_range = np.array([0] * 14, dtype=float)
n = 0
for parameter in get_all_parameters(evaluator):
    n += 1
    ls = get_value(evaluator, parameter, None, 'l')
    us = get_value(evaluator, parameter, None, 'u')

    last_m = get_value(evaluator, parameter, 13, 'm')
    last_l = get_value(evaluator, parameter, 13, 'l')
    last_u = get_value(evaluator, parameter, 13, 'u')

    v = np.array([l<=last_m<=u for l, u in zip(ls, us)], dtype=float)
    last_in_range += v

    v1 = np.array([l<=last_u<=u for l, u in zip(ls, us)], dtype=float)
    v2 = np.array([l <= last_l <= u for l, u in zip(ls, us)], dtype=float)
    v3 = ((v1+v2) == 2).astype(float)
    both_in_range += v3

    if n % 1000 == 0:
        print(n)
last_in_range /= n
print(last_in_range)

both_in_range /= n
print(both_in_range)
