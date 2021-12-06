import sys
sys.path.insert(0, '.')
from thpo.data_utils import get_evaluator, get_all_parameters, get_value, get_sorted_parameters
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

path = './input/data-30'
#path = './input/data-2'
evaluator = get_evaluator(path)
print('get_evaluator!')

name_list = evaluator.dims  # all parameter names
parameters_config = evaluator.parameters_config

top_n = 10

sorted_parameters = get_sorted_parameters(evaluator)[:top_n]
for parameter in sorted_parameters:
    values = get_value(evaluator, parameter, None, None)
    print(values)

p = plt.figure()
for i, parameter in enumerate(sorted_parameters):
    us = get_value(evaluator, parameter, None, 'u')
    ms = get_value(evaluator, parameter, None, 'm')
    ls = get_value(evaluator, parameter, None, 'l')

    ax = p.add_subplot(2, 5, i + 1)
    plt.plot(us, color='b')
    plt.plot(ms, color='r')
    plt.plot(ls, color='g')
    print('finish', i)
plt.show()
