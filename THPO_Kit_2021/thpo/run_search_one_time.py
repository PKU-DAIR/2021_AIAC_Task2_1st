# coding=utf-8
import os
import sys
import importlib
import time
import json
import traceback

from collections import Iterable

sys.path.append(".")
import thpo.common as common
from thpo.evaluate_function import EvaluateFunction


def get_implement_searcher(searcher_root):
    """ Get the searcher implemented in the searcher_root directory

    Args:
        searcher_root: directory of searcher

    Returns:
        ip_module_class: the provided Searcher Class
    """
    if not os.path.exists(searcher_root):
        return False
    sys.path.append(searcher_root)
    ip_module = importlib.import_module('.searcher', searcher_root)
    ip_module_class = getattr(ip_module, "Searcher")
    return ip_module_class


def save_to_result_file(result_file, eva_data_name, repeat_num, iteration, suggestion, reward):
    item = {
        'fun': eva_data_name,
        "repeat": repeat_num,
        'iter': iteration,
        'param': suggestion,
        'reward': reward,
    }
    item_str = json.dumps(item)
    result_file.write(item_str + '\n')
    print("fun:%7s, run:%2d, iter:%2d, suggest:%s reward:%f" % (
        eva_data_name, repeat_num, iteration, str(suggestion), reward))


def run_search_one_time(args, search_class, eva_data_name, repeat_num):
    """ Evaluate searcher for one repeat

    Args:
        args: arguments for running search job
        search_class: searcher class
        eva_data_name: name of evaluation function
        repeat_num: number of repetitions
    """
    data_root = args[common.CmdArgs.data_root]
    n_iteration = args[common.CmdArgs.n_iteration]
    n_suggestionsion = args[common.CmdArgs.n_suggestions]
    all_iter = n_iteration * n_suggestionsion
    path = data_root + str(eva_data_name)
    eva = EvaluateFunction(path, all_iter)

    n_iteration = args[common.CmdArgs.n_iteration]
    n_suggestionsion = args[common.CmdArgs.n_suggestions]

    try:
        searcher = search_class(eva.parameters_config, n_iteration, n_suggestionsion)
    except Exception as e:
        print(traceback.format_exc())
        err_msg = "SuggestException search_class " + repr(e)
        return common.SEARCHER_INIT_ERROR, err_msg

    suggestions_history = []
    suggest_time = 0
    result_file_name = args[common.CmdArgs.result_root] + eva_data_name
    result_file = open(result_file_name, 'a')
    err_code, err_msg = common.SEARCH_SUCCESS, ""
    for __ in range(n_iteration):
        begin_time = time.time()
        next_suggestions = None
        try:
            next_suggestions = searcher.suggest(suggestions_history, n_suggestionsion)
        except Exception as e:
            print(traceback.format_exc())
            err_code, err_msg = common.SUGGEST_RUN_ERROR, "SuggestException " + repr(e)
            continue
        suggest_time = suggest_time + time.time() - begin_time
        if suggest_time > args[common.CmdArgs.timeout]:
            err_code = common.RUN_TIMEOUT
            # timeout to break out the loop
            break
        if next_suggestions is None:
            err_code, err_msg = common.SUGGEST_RESULT_ERROR, "Suggest result is None"
            continue
        if isinstance(next_suggestions, Iterable) is not True:
            err_code, err_msg = common.SUGGEST_RESULT_ERROR, "Suggest result must Iterable"
            continue
        if len(next_suggestions) > n_suggestionsion:
            next_suggestions = next_suggestions[0:n_suggestionsion]

        for suggestion in next_suggestions:
            try:
                reward = eva.evaluate(suggestion)
            except Exception as e:
                print(traceback.format_exc())
                err_code, err_msg = common.SUGGEST_EVALUATE_ERROR, "EvaluateException " + repr(e)
                continue
            suggestions_history.append([suggestion, reward])
            iteration = len(suggestions_history)
            save_to_result_file(result_file, eva_data_name, repeat_num, iteration, suggestion, reward)

    print("run_search_one_time", eva_data_name, "repeat:", repeat_num, "done")
    return err_code, err_msg


if __name__ == "__main__":
    args = common.parse_args(common.experiment_parser("description"))
    searcher_root = args[common.CmdArgs.searcher_root]
    searcher = get_implement_searcher(searcher_root)

    eva_func_list = args[common.CmdArgs.data]
    repeat_num = args[common.CmdArgs.repear_num]
    err_code, err_msg = run_search_one_time(args, searcher, eva_func_list[0], repeat_num)

    if err_code != common.SEARCH_SUCCESS:
        sys.stderr.write(err_msg)

    sys.exit(err_code)
