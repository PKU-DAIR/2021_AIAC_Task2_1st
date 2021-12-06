"""
总共10000个，最好的50个之间，偏序对关系[0.51843137 0.57254902 0.55372549 0.56705882 0.61882353 0.64235294
 0.61803922 0.62823529 0.65568627 0.6745098  0.68078431 0.68941176
 0.67686275 1.        ]

总共10000个，最好的100个之间，偏序对关系[0.54882547 0.5468841  0.59270045 0.57658707 0.61696758 0.64511745
 0.6443409  0.65695981 0.66919045 0.6788973  0.69229276 0.71287129
 0.71461852 1.        ]

总共10000个，最好的500个之间，偏序对关系[0.5991371  0.6162487  0.64608806 0.66918602 0.6859047  0.70064332
 0.71175315 0.72505104 0.72931161 0.73992064 0.74687777 0.75279479
 0.76108479 1.        ]
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

para_reward = []
para_cnt = 0
for para in get_all_parameters(evaluator):
    reward = get_value(evaluator, para, 13, 'm')
    para_reward.append((para, reward))
    para_cnt += 1
para_reward.sort(key=lambda x: -x[1])   # maximize

top_percent = 0.005
top_para = [para for para, reward in para_reward][:int(para_cnt*top_percent)]
print('para_cnt:', para_cnt)

mean_order = np.array([0] * 14, dtype=float)
n = 0
for para1 in top_para:
    for para2 in top_para:
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
