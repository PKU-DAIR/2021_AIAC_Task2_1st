# coding=utf-8
import os
NUM_THREADS = "2"
os.environ["OMP_NUM_THREADS"] = NUM_THREADS         # export OMP_NUM_THREADS=1
os.environ["OPENBLAS_NUM_THREADS"] = NUM_THREADS    # export OPENBLAS_NUM_THREADS=1
os.environ["MKL_NUM_THREADS"] = NUM_THREADS         # export MKL_NUM_THREADS=1
os.environ["VECLIB_MAXIMUM_THREADS"] = NUM_THREADS  # export VECLIB_MAXIMUM_THREADS=1
os.environ["NUMEXPR_NUM_THREADS"] = NUM_THREADS     # export NUMEXPR_NUM_THREADS=1

# Need to import the searcher abstract class, the following are essential
from thpo.abstract_searcher import AbstractSearcher

import time
import numpy as np

from openbox import space as sp
from openbox import Observation
from openbox import SyncBatchAdvisor
from openbox.utils.config_space.space_utils import get_config_from_dict
from openbox.utils.history_container import HistoryContainer

N_ITERATION = 140
CONFIDENCE_N_ITERATION = 14


class Searcher(AbstractSearcher):
    searcher_name = "OpenBoxSearcher"

    def __init__(self, parameters_config, n_iter, n_suggestion):
        """ Init searcher

        Args:
            parameters_config: parameters configuration, consistent with the definition of parameters_config of EvaluateFunction. dict type:
                    dict key: parameters name, string type
                    dict value: parameters configuration, dict type:
                        "parameter_name": parameter name
                        "parameter_type": parameter type, 1 for double type, and only double type is valid
                        "double_max_value": max value of this parameter
                        "double_min_value": min value of this parameter
                        "double_step": step size
                        "coords": list type, all valid values of this parameter.
                            If the parameter value is not in coords,
                            the closest valid value will be used by the judge program.

                    parameter configuration example, eg:
                    {
                        "p1": {
                            "parameter_name": "p1",
                            "parameter_type": 1
                            "double_max_value": 2.5,
                            "double_min_value": 0.0,
                            "double_step": 1.0,
                            "coords": [0.0, 1.0, 2.0, 2.5]
                        },
                        "p2": {
                            "parameter_name": "p2",
                            "parameter_type": 1,
                            "double_max_value": 2.0,
                            "double_min_value": 0.0,
                            "double_step": 1.0,
                            "coords": [0.0, 1.0, 2.0]
                        }
                    }
                    In this example, "2.5" is the upper bound of parameter "p1", and it's also a valid value.

        n_iteration: number of iterations
        n_suggestion: number of suggestions to return
        """
        AbstractSearcher.__init__(self, parameters_config, n_iter, n_suggestion)

        self.all_configs = set()

        # hyper-parameters of Searcher
        self.hps = dict(
            prune_start_n_configs=40,
            prune_method='mean_rank',  # 'upper_bound', 'mean_rank'
            prune_iters=[7],
            # for 'mean_rank'
            prune_eta=2,
            # for 'upper_bound'
            prune_top_n=10,      # prune if upper bound worse than top N config's mean

            impute_method='init_median',   # None, 'trend', 'mean', 'init_mean', 'init_median'
            impute_threshold=1,
        )
        self.prune_start_iter = self.hps['prune_start_n_configs'] / 5 * 14 + 1

        self.impute_value = None

        self.config_space = self.get_config_space(parameters_config)
        self.advisor = SyncBatchAdvisor(
            config_space=self.config_space,
            batch_size=5,
            batch_strategy='reoptimization',
            initial_trials=10,
            init_strategy='random_explore_first',
            rand_prob=0.1,
            surrogate_type='gp',
            acq_type='ei',
            acq_optimizer_type='random_scipy',
            task_id='thpo',
            random_state=47,
        )

    @staticmethod
    def get_config_space(parameters_config: dict):
        config_space = sp.Space()
        for name, v in parameters_config.items():
            hp = sp.Int(name, 0, len(v['coords']) - 1)
            config_space.add_variable(hp)
        return config_space

    def convert_parameter_to_config(self, parameter: dict):
        """
        Parameter: a dict in the form of {name:value, name:value, ...}. for example:
                            {'p1': 0, 'p2': 0, 'p3': 0}
        """
        para_dict = dict()
        for name, v in parameter.items():
            para_dict[name] = self.parameters_config[name]['coords'].index(v)
        config = get_config_from_dict(para_dict, self.config_space)
        return config

    def convert_config_to_parameter(self, config: sp.Configuration):
        para_dict = config.get_dictionary()
        parameter = dict()
        for name, v in para_dict.items():
            parameter[name] = self.parameters_config[name]['coords'][v]
        return parameter

    def parse_suggestion_history_old(self, suggestion_history):
        history_container = HistoryContainer('thpo')
        for para, reward in suggestion_history:
            config = self.convert_parameter_to_config(para)
            perf = -reward  # maximize reward -> minimize perf
            observation = Observation(config=config, objs=[perf])
            history_container.update_observation(observation)
        return history_container

    def suggest_old(self, suggestion_history, n_suggestions=1):
        """ Suggest next n_suggestion parameters, old implementation of preliminary competition.

        Args:
            suggestion_history: a list of historical suggestion parameters and rewards, in the form of
                    [[Parameter, Reward], [Parameter, Reward] ... ]
                        Parameter: a dict in the form of {name:value, name:value, ...}. for example:
                            {'p1': 0, 'p2': 0, 'p3': 0}
                        Reward: a float type value

                    The parameters and rewards of each iteration are placed in suggestions_history in the order of iteration.
                        len(suggestions_history) = n_suggestion * iteration(current number of iteration)

                    For example:
                        when iteration = 2, n_suggestion = 2, then
                        [[{'p1': 0, 'p2': 0, 'p3': 0}, -222.90621774147272],
                         [{'p1': 0, 'p2': 1, 'p3': 3}, -65.26678723205647],
                         [{'p1': 2, 'p2': 2, 'p3': 2}, 0.0],
                         [{'p1': 0, 'p2': 0, 'p3': 4}, -105.8151893979122]]

            n_suggestions: int, number of suggestions to return

        Returns:
            next_suggestions: list of Parameter, in the form of
                    [Parameter, Parameter, Parameter ...]
                        Parameter: a dict in the form of {name:value, name:value, ...}. for example:
                            {'p1': 0, 'p2': 0, 'p3': 0}

                    For example:
                        when n_suggestion = 3, then
                        [{'p1': 0, 'p2': 0, 'p3': 0},
                         {'p1': 0, 'p2': 1, 'p3': 3},
                         {'p1': 2, 'p2': 2, 'p3': 2}]
        """
        history_container = self.parse_suggestion_history_old(suggestion_history)
        next_configs = self.advisor.get_suggestions(n_suggestions, history_container)
        next_suggestions = [self.convert_config_to_parameter(conf) for conf in next_configs]
        return next_suggestions

    def set_impute_value(self, running_suggestions: list, suggestion_history: list):
        if self.hps['impute_method'] not in ['init_mean', 'init_median']:
            return
        # only set once
        if self.impute_value is not None:
            return

        value_list = []
        for suggestion in running_suggestions + suggestion_history:
            n_history = len(suggestion['reward'])
            if n_history != CONFIDENCE_N_ITERATION:
                continue
            value_list.append(suggestion['reward'][-1]['value'])

        if self.hps['impute_method'] == 'init_mean':
            self.impute_value = np.mean(value_list).item()
        elif self.hps['impute_method'] == 'init_median':
            self.impute_value = np.median(value_list).item()
        else:
            raise ValueError(self.hps['impute_method'])

    def get_impute_value(self, suggestion: dict):
        n_history = len(suggestion['reward'])
        if n_history == CONFIDENCE_N_ITERATION:
            return suggestion['reward'][-1]['value']
        if self.hps['impute_method'] is None or n_history < self.hps['impute_threshold']:
            return None

        if self.hps['impute_method'] in ['init_mean', 'init_median']:
            return self.impute_value
        elif self.hps['impute_method'] == 'mean':
            last_m = suggestion['reward'][-1]['value']
            return last_m
        elif self.hps['impute_method'] == 'trend':
            # parse mean trend
            means = [v['value'] for v in suggestion['reward']]
            increase_cnt, decrease_cnt = 0, 0
            for i in range(1, len(means)):
                if means[i] > means[i - 1]:
                    increase_cnt += 1
                elif means[i] < means[i - 1]:
                    decrease_cnt += 1

            # get impute value
            last_m = suggestion['reward'][-1]['value']
            last_u = suggestion['reward'][-1]['upper_bound']
            last_l = suggestion['reward'][-1]['lower_bound']
            if increase_cnt > decrease_cnt:
                impute_value = 0.5 * (last_m + last_u)
            elif increase_cnt < decrease_cnt:
                impute_value = 0.5 * (last_m + last_l)
            else:
                impute_value = last_m
            return impute_value
        else:
            raise ValueError(self.hps['impute_method'])

    def suggest(self, iteration_number, running_suggestions, suggestion_history, n_suggestions=1):
        """ Suggest next n_suggestion parameters. new implementation of final competition

        Args:
            iteration_number: int ,the iteration number of experiment, range in [1, 140]

            running_suggestions: a list of historical suggestion parameters and rewards, in the form of
                    [{"parameter": Parameter, "reward": Reward}, {"parameter": Parameter, "reward": Reward} ... ]
                Parameter: a dict in the form of {name:value, name:value, ...}. for example:
                    {'p1': 0, 'p2': 0, 'p3': 0}
                Reward: a list of dict, each dict of the list corresponds to an iteration,
                    the dict is in the form of {'value':value,  'upper_bound':upper_bound, 'lower_bound':lower_bound} 
                    Reward example:
                        [{'value':1, 'upper_bound':2,   'lower_bound':0},   # iter 1
                         {'value':1, 'upper_bound':1.5, 'lower_bound':0.5}  # iter 2
                        ]

            suggestion_history: a list of historical suggestion parameters and rewards, in the same form of running_suggestions

            n_suggestions: int, number of suggestions to return

        Returns:
            next_suggestions: list of Parameter, in the form of
                    [Parameter, Parameter, Parameter ...]
                        Parameter: a dict in the form of {name:value, name:value, ...}. for example:
                            {'p1': 0, 'p2': 0, 'p3': 0}
                    For example:
                        when n_suggestion = 3, then
                        [{'p1': 0, 'p2': 0, 'p3': 0},
                         {'p1': 0, 'p2': 1, 'p3': 3},
                         {'p1': 2, 'p2': 2, 'p3': 2}]
        """
        print('===== ITER %d: get suggestions =====' % iteration_number)

        remain_evaluation_iteration = N_ITERATION - iteration_number + 1
        if remain_evaluation_iteration < CONFIDENCE_N_ITERATION:
            print('iteration_number=%d. remain=%d. no suggest.' % (iteration_number, remain_evaluation_iteration))
            return []

        new_suggestions_history = []
        self.all_configs = set()
        for suggestion in suggestion_history:
            value = self.get_impute_value(suggestion)
            if value is not None:
                new_suggestions_history.append([suggestion["parameter"], value])
            self.all_configs.add(self.convert_parameter_to_config(suggestion["parameter"]))

        for suggestion in running_suggestions:
            self.all_configs.add(self.convert_parameter_to_config(suggestion["parameter"]))

        return self.suggest_old(new_suggestions_history, n_suggestions)

    def is_early_stop(self, iteration_number, running_suggestions, suggestion_history):
        """ Decide whether to stop the running suggested parameter experiment.

        Args:
            iteration_number: int, the iteration number of experiment, range in [1, 140]

            running_suggestions: a list of historical suggestion parameters and rewards, in the form of
                    [{"parameter": Parameter, "reward": Reward}, {"parameter": Parameter, "reward": Reward} ... ]
                Parameter: a dict in the form of {name:value, name:value, ...}. for example:
                    {'p1': 0, 'p2': 0, 'p3': 0}
                Reward: a list of dict, each dict of the list corresponds to an iteration,
                    the dict is in the form of {'value':value,  'upper_bound':upper_bound, 'lower_bound':lower_bound} 
                    Reward example:
                        [{'value':1, 'upper_bound':2,   'lower_bound':0},   # iter 1
                         {'value':1, 'upper_bound':1.5, 'lower_bound':0.5}  # iter 2
                        ]

            suggestion_history: a list of historical suggestion parameters and rewards, in the same form of running_suggestions

        Returns:
            stop_list: list of bool, indicate whether to stop the running suggestions.
                    len(stop_list) must be the same as len(running_suggestions), for example:
                        len(running_suggestions) = 3, stop_list could be : 
                            [True, True, True] , which means to stop all the three running suggestions
        """
        print('===== ITER %d: update and stop =====' % iteration_number)

        if iteration_number < self.prune_start_iter:
            print('iteration_number=%d. prune_start_iter=%d. no early stop.'
                  % (iteration_number, self.prune_start_iter))
            return [False] * len(running_suggestions)

        remain_evaluation_iteration = N_ITERATION - iteration_number
        if remain_evaluation_iteration < CONFIDENCE_N_ITERATION:
            print('iteration_number=%d. remain=%d. no early stop.' % (iteration_number, remain_evaluation_iteration))
            return [False] * len(running_suggestions)

        self.set_impute_value(running_suggestions, suggestion_history)

        if self.hps['prune_method'] == 'mean_rank':
            return self.prune_mean_rank(iteration_number, running_suggestions, suggestion_history)
        elif self.hps['prune_method'] == 'upper_bound':
            return self.prune_upper_bound(iteration_number, running_suggestions, suggestion_history)
        else:
            raise ValueError(self.hps['prune_method'])

    def prune_mean_rank(self, iteration_number, running_suggestions, suggestion_history):
        # get candidates value
        bracket = dict()
        for n_iteration in self.hps['prune_iters']:
            bracket[n_iteration] = list()
        for suggestion in running_suggestions + suggestion_history:
            n_history = len(suggestion['reward'])
            for n_iteration in self.hps['prune_iters']:
                if n_history >= n_iteration:
                    bracket[n_iteration].append(suggestion['reward'][n_iteration - 1]['value'])
        for n_iteration in self.hps['prune_iters']:
            bracket[n_iteration].sort(reverse=True)  # maximize

        stop_list = [False] * len(running_suggestions)
        for i, suggestion in enumerate(running_suggestions):
            n_history = len(suggestion['reward'])
            if n_history == CONFIDENCE_N_ITERATION:
                print('full observation. pass', i)
                continue
            if n_history not in self.hps['prune_iters']:
                print('n_history: %d not in prune_iters: %s. pass %d.'
                      % (n_history, self.hps['prune_iters'], i))
                continue

            rank = bracket[n_history].index(suggestion['reward'][-1]['value'])
            total_cnt = len(bracket[n_history])
            if rank / total_cnt >= 1 / self.hps['prune_eta']:
                print('n_history: %d, rank: %d/%d, eta: 1/%s. PRUNE %d!'
                      % (n_history, rank, total_cnt, self.hps['prune_eta'], i))
                stop_list[i] = True
            else:
                print('n_history: %d, rank: %d/%d, eta: 1/%s. continue %d.'
                      % (n_history, rank, total_cnt, self.hps['prune_eta'], i))
        return stop_list

    def prune_upper_bound(self, iteration_number, running_suggestions, suggestion_history):
        # get top n full evaluated results
        value_list = []
        for suggestion in suggestion_history + running_suggestions:
            if len(suggestion['reward']) == CONFIDENCE_N_ITERATION:
                value_list.append(suggestion['reward'][-1]['value'])
        value_list.sort(reverse=True)  # maximize value
        target_value = value_list[:self.hps['prune_top_n']][-1]
        print('prune_top_n:', self.hps['prune_top_n'], 'prune target value:', target_value)

        stop_list = [False] * len(running_suggestions)
        for i, suggestion in enumerate(running_suggestions):
            n_history = len(suggestion['reward'])
            if n_history == CONFIDENCE_N_ITERATION:
                print('full observation. pass', i)
                continue
            if n_history not in self.hps['prune_iters']:
                print('n_history: %d not in prune_iters: %s. pass %d.'
                      % (n_history, self.hps['prune_iters'], i))
                continue

            upper_bound = suggestion['reward'][-1]['upper_bound']
            if upper_bound < target_value:
                print('upper_bound: %s. PRUNE %d!' % (upper_bound, i))
                stop_list[i] = True
            else:
                print('upper_bound: %s. no prune %d.' % (upper_bound, i))
        return stop_list
