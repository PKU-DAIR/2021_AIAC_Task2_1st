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


confidence_iteration_count = 14

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

def suggest_new(searcher, iteration_number, running_suggestions, suggestions_history, need_suggestions_count):
    try:
        next_suggestions = searcher.suggest(iteration_number, running_suggestions, suggestions_history, need_suggestions_count)
    except Exception as e:
        print(traceback.format_exc())
        err_code, err_msg = common.SUGGEST_RUN_ERROR, "SuggestException " + repr(e)
        return running_suggestions, err_code, err_msg

    if next_suggestions is None:
        err_code, err_msg = common.SUGGEST_RESULT_ERROR, "Suggest result is None"
        return running_suggestions, err_code, err_msg
    if isinstance(next_suggestions, Iterable) is not True:
        err_code, err_msg = common.SUGGEST_RESULT_ERROR, "Suggest result must Iterable"
        return running_suggestions, err_code, err_msg
    if len(next_suggestions) > need_suggestions_count:
        next_suggestions = next_suggestions[0:need_suggestions_count]
    # Add the new suggestions to the running suggestions
    for next_suggestion in next_suggestions:
        running_suggestions.append({"parameter": next_suggestion, "reward": []})
        print(iteration_number, "get new suggest ", next_suggestion, " into running, cur running:", len(running_suggestions), " cur hist:", len(suggestions_history))
    return running_suggestions, common.SEARCH_SUCCESS, ""

def run_search_one_time(args, search_class, eva_data_name, repeat_num):
    """ Evaluate searcher for one repeat

    Args:
        args: arguments for running search job
        search_class: searcher class
        eva_data_name: name of evaluation function
        repeat_num: number of repetitions
    """
    n_iteration = args[common.CmdArgs.n_iteration]
    n_suggestions = args[common.CmdArgs.n_suggestions]
    path = args[common.CmdArgs.data_root] + str(eva_data_name)
    eva = EvaluateFunction(path, 100)
    try:
        searcher = search_class(eva.parameters_config, n_iteration, n_suggestions)
    except Exception as e:
        print(traceback.format_exc())
        err_msg = "SuggestException search_class " + repr(e)
        return common.SEARCHER_INIT_ERROR, err_msg

    running_suggestions, suggestions_history = [], []
    suggest_time = 0
    result_file_name = args[common.CmdArgs.result_root] + eva_data_name
    result_file = open(result_file_name, 'a')
    err_code, err_msg = common.SEARCH_SUCCESS, ""
    for iteration_number in range(1, n_iteration+1):
        begin_time = time.time()
        # Step 1. Judge need new suggestions or not
        need_suggestions_count = n_suggestions - len(running_suggestions)
        if need_suggestions_count > 0:
            # Step 2 Suggest new suggestions
            running_suggestions, err_code, err_msg = suggest_new(searcher, iteration_number, 
                running_suggestions, suggestions_history, need_suggestions_count)
        suggest_time = suggest_time + time.time() - begin_time
        if suggest_time > args[common.CmdArgs.timeout]:
            err_code = common.RUN_TIMEOUT
            # timeout to break out the loop
            break

        # Step 3. Get the suggestions reward of the running suggestions on the iteration
        try:
            running_suggestions = eva.evaluate_final(running_suggestions)
        except Exception as e:
            print(traceback.format_exc())
            err_code, err_msg = common.SUGGEST_EVALUATE_ERROR, "EvaluateException " + repr(e)

        # Step 4. Judge running suggestions need early stop or not
        need_stops = [False] * n_suggestions
        begin_time = time.time()
        try:
            ret_need_stops = searcher.is_early_stop(iteration_number, running_suggestions, suggestions_history)
            for i, need_stop in enumerate(ret_need_stops):
                if need_stop and i < len(need_stops):
                    need_stops[i] = True
        except Exception as e:
            print(traceback.format_exc())
            err_code, err_msg = common.SUGGEST_EVALUATE_ERROR, "EvaluateException " + repr(e)
        suggest_time = suggest_time + time.time() - begin_time
        if suggest_time > args[common.CmdArgs.timeout]:
            err_code = common.RUN_TIMEOUT
            # timeout to break out the loop
            break

        # Step 5. Add suggestions that have run 14 iters into the suggestions history
        for i, suggest in enumerate(running_suggestions):
            if len(suggest['reward']) >= confidence_iteration_count:
                need_stops[i] = True

        # Step 6. Stop running suggestions and put then into the suggestions history
        for i in range(len(need_stops)-1, -1, -1):
            if need_stops[i]:
                is_early = len(running_suggestions[i]['reward']) >= confidence_iteration_count
                print(iteration_number, "14 iteration stop:", is_early, running_suggestions[i],
                    " put into history, cur hist:", len(suggestions_history))
                suggestions_history.append(running_suggestions[i])
                running_suggestions.remove(running_suggestions[i])

    print("\n\nrun_search_one_time", eva_data_name, "repeat:", repeat_num, "result:")
    save_idx = 1
    for idx, suggestion in enumerate(suggestions_history):
        print("fun:%7s, run:%2d, iter:%2d, suggest:%s" % (eva.get_name(), repeat_num, idx, str(suggestion)))
        if len(suggestion['reward']) >= confidence_iteration_count:
            reward = suggestion['reward'][-1]['value']
            save_to_result_file(result_file, eva_data_name, repeat_num, save_idx, suggestion['parameter'], reward)
            save_idx = save_idx + 1

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
