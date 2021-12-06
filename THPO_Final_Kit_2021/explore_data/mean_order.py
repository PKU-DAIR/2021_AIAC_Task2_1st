"""
[0.92651877 0.97393174 0.99200683 0.99489761 0.99669625 0.99748805
 0.99746758 0.99759044 0.99791468 0.99811263 0.99826621 0.99827986
 0.99829352 1.        ]

"""
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

def compare(d1, d2):
    for name in name_list:
        if d1[name] < d2[name]:
            return -1
        elif d1[name] > d2[name]:
            return 1
    return 0

mean_order = np.array([0] * 14, dtype=float)
n = 0
for para1 in get_all_parameters(evaluator):
    for para2 in get_all_parameters(evaluator):
        if compare(para1, para2) >= 0:     # skip
            continue
        n += 1

        para1_ms = get_value(evaluator, para1, None, 'm')
        para2_ms = get_value(evaluator, para2, None, 'm')

        last_order = (para1_ms[-1] <= para2_ms[-1])

        v = ((np.array(para1_ms) <= np.array(para2_ms))==last_order).astype(float)
        mean_order += v

        if n % 1000 == 0:
            print(n)
            print(mean_order/n)
print(n)
print(mean_order/n)
