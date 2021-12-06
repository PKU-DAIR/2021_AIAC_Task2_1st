# coding=utf-8
"""
an example to read data
"""
import numpy as np
import itertools
try:
    from evaluate_function import EvaluateFunction
except ModuleNotFoundError:
    from .evaluate_function import EvaluateFunction


def get_evaluator(path):
    return EvaluateFunction(path, None)


def get_all_parameter_pairs(evaluator, return_list=False):
    name_list = evaluator.dims  # all parameter names
    parameters_config = evaluator.parameters_config

    all_coords = [parameters_config[name]['coords'] for name in name_list]
    all_parameter_pairs = itertools.product(*all_coords)
    if return_list:
        all_parameter_pairs = list(all_parameter_pairs)
    return all_parameter_pairs


def get_all_parameters(evaluator, return_list=False):
    def _generator(evaluator):
        name_list = evaluator.dims  # all parameter names
        for pair in get_all_parameter_pairs(evaluator, return_list=False):
            para_dict = {name: value for name, value in zip(name_list, pair)}
            yield para_dict
    gen = _generator(evaluator)
    if return_list:
        gen = list(gen)
    return gen


N_ITERS = 14
value_name_dict = dict(v='value', m='value', l='lower_bound', u='upper_bound')


def get_value(evaluator, para_dict, day=None, value_name=None):
    """
    :param para_dict:
        dict type parameter
    :param day:
        0 <= day < N_ITERS or None (return data in all days)
    :param value_name:
        'value', 'v', 'm'
        'lower_bound', 'l'
        'upper_bound', 'u'
    """
    result = evaluator.get_paramter_score(para_dict)    # list of dicts. dict keys: value, lower_bound, upper_bound
    if day is not None:
        assert 0 <= day < N_ITERS
        result = result[day]
    if value_name is not None:
        value_name = value_name_dict.get(value_name, value_name)
        assert value_name in ['value', 'lower_bound', 'upper_bound']

        if day is not None:
            result = result[value_name]
        else:
            result = [result[d][value_name] for d in range(N_ITERS)]
    return result


def get_sorted_parameters(evaluator):
    para_reward = []
    for para in get_all_parameters(evaluator):
        reward = get_value(evaluator, para, 13, 'm')
        para_reward.append((para, reward))
    para_reward.sort(key=lambda x: -x[1])  # maximize
    sorted_para = [para for para, reward in para_reward]
    return sorted_para


if __name__ == '__main__':

    path = './input/data-30'
    #path = './input/data-2'
    evaluator = get_evaluator(path)

    for parameter in get_all_parameters(evaluator):
        result = get_value(evaluator, parameter, None, 'm')
        print(result)
        break

