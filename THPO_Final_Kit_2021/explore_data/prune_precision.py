"""
用top50对top1000剪枝
49950 [ 7162. 11609. 16203. 21277. 25559. 29091. 31633. 33475. 34908. 36431.
 37433. 38214. 39080. 40756.]
[0.9913432  0.99776036 0.99870394 0.99868403 0.99917837 0.99927813
 1.         1.         0.99959895 0.99947847 0.99930543 0.99952897
 0.99953941 1.        ]

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
sorted_para = [para for para, reward in para_reward]

top_cnt = 50
candidate_cnt = 1000

prune_precision = np.array([0] * 14, dtype=float)
valid_cnt = np.array([0] * 14, dtype=float)
n = 0
for running_para in sorted_para[:candidate_cnt]:
    for target_para in sorted_para[:top_cnt]:
        if running_para == target_para:     # skip
            continue
        n += 1

        running_us = get_value(evaluator, running_para, None, 'u')
        running_last_m = get_value(evaluator, running_para, 13, 'm')
        target_last_m = get_value(evaluator, target_para, 13, 'm')

        running_us = np.array(running_us)
        valid_cnt += (running_us < target_last_m).astype(float)
        prune_precision += ((running_us < target_last_m) & (running_last_m < target_last_m)).astype(float)

        if n % 1000 == 0:
            print(n, valid_cnt)
            print(prune_precision/valid_cnt)
print(n, valid_cnt)
print(prune_precision/valid_cnt)
