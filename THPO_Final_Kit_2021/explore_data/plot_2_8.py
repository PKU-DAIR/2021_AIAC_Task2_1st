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

idx_list = [0, 1000, 3000, 2000, 500,
       1, 6000, 5000, 2500, 3200]
sorted_parameters = get_sorted_parameters(evaluator)
# for parameter in sorted_parameters:
#     values = get_value(evaluator, parameter, None, None)
#     print(values)

p = plt.figure(figsize=(8.0, 4.5))
for i, idx in enumerate(idx_list):
    parameter = sorted_parameters[idx]
    print(i, idx, get_value(evaluator, parameter, 13, 'm'))
    us = get_value(evaluator, parameter, None, 'u')
    ms = get_value(evaluator, parameter, None, 'm')
    ls = get_value(evaluator, parameter, None, 'l')

    ax = p.add_subplot(2, 5, i + 1)
    ax.set_ylim(-6, 4)
    plt.plot(us, color='b')
    plt.plot(ms, color='r')
    plt.plot(ls, color='g')
    print('finish', i)
plt.tight_layout(pad=0.5)
plt.show()
#plt.savefig('./plot.pdf')
