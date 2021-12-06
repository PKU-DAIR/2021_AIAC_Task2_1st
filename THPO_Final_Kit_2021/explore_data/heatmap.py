import sys
sys.path.insert(0, '.')
from thpo.data_utils import get_evaluator, get_all_parameters, get_value
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

path = './input/data-30'
#path = './input/data-2'
evaluator = get_evaluator(path)

p = plt.figure(figsize=(8,6))

name_list = evaluator.dims  # all parameter names
parameters_config = evaluator.parameters_config

for day in range(14):
    print('read day', day)
    data = []
    for parameter in get_all_parameters(evaluator):
        value_name = 'm'
        result = get_value(evaluator, parameter, day, value_name)
        data.append(result)
    data = np.array(data).reshape(-1, int(np.sqrt(len(data))))

    print('plot day', day)
    p.add_subplot(2,7,day+1)
    sns.heatmap(data, cmap='rainbow').invert_yaxis()

plt.show()
