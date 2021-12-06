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

last_larger = np.array([0] * 14, dtype=float)
n = 0
for parameter in get_all_parameters(evaluator):
    n += 1
    # ls = get_value(evaluator, parameter, None, 'l')
    # us = get_value(evaluator, parameter, None, 'u')
    ms = get_value(evaluator, parameter, None, 'm')

    last_m = get_value(evaluator, parameter, 13, 'm')

    v = np.array([last_m >= m for m in ms], dtype=float)
    last_larger += v

    if n % 1000 == 0:
        print(n)
last_larger /= n
print(last_larger)

