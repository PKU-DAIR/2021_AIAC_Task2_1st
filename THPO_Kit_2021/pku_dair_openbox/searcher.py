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

from openbox import space as sp
from openbox import Observation
from openbox import SyncBatchAdvisor
from openbox.utils.config_space.space_utils import get_config_from_dict
from openbox.utils.history_container import HistoryContainer


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

        self.config_space = self.get_config_space(parameters_config)
        self.advisor = SyncBatchAdvisor(
            config_space=self.config_space,
            batch_size=5,
            batch_strategy='default',   # reoptimization
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

    def parse_suggestion_history(self, suggestion_history):
        history_container = HistoryContainer('thpo')
        for para, reward in suggestion_history:
            config = self.convert_parameter_to_config(para)
            perf = -reward  # maximize reward -> minimize perf
            observation = Observation(config=config, objs=[perf])
            history_container.update_observation(observation)
        return history_container

    def suggest(self, suggestion_history, n_suggestions=1):
        """ Suggest next n_suggestion parameters.

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
        history_container = self.parse_suggestion_history(suggestion_history)
        next_configs = self.advisor.get_suggestions(n_suggestions, history_container)
        next_suggestions = [self.convert_config_to_parameter(conf) for conf in next_configs]
        return next_suggestions
