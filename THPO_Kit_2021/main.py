# coding=utf-8
import sys
import os
import importlib
import traceback
import numpy as np

from thpo.abstract_searcher import AbstractSearcher
from thpo.run_search import run_search
from thpo.reward_calculation import calculate_reward
import thpo.common as common


def is_implement_searcher(searcher_root):
    """ Test whether searcher is implemented

    Args:
        searcher_root: directory of searcher

    Return:
        True/False: whether searcher is implemented
    """
    if not os.path.exists(searcher_root):
        return False
    sys.path.append(searcher_root)
    try:
        ip_module = importlib.import_module('.searcher', searcher_root)
        ip_module_class = getattr(ip_module, "Searcher")
        return issubclass(ip_module_class, AbstractSearcher)
    except Exception:
        print(traceback.format_exc())
        return False


def experiment(args):
    """ Run experiment

    Args:
        args: arguments for running searching task

    Return:
        err_code: error code of searching task
        err_msg: error message of searching task
        final_score: final score of this searcher
    """

    # Evaluate the searcher on all evaluation functions, save result to output_* folder
    err_code, err_msg = run_search(args)
    course_result, final_score = calculate_reward(args)

    print("\n\n======================= run search result =========================\n")
    print(" err_code: ", err_code, " err_msg: ", err_msg)
    print("\n================ evaluation function baseline info ==================\n")
    eva_func_list = args[common.CmdArgs.data]
    for i, func_name in enumerate(eva_func_list):
        print("func:", func_name, "best:", course_result["best"][i],
              "rand-perf:", course_result["rand_perf"][i])

    with np.printoptions(precision=2, suppress=True):
        print("\n=================== function repetition best reward ==================\n")
        for i, func_name in enumerate(eva_func_list):
            print("func:", func_name, course_result["best_reward"][i])
        print("\n=============== function repetition normalized reward ================\n")
        for i, func_name in enumerate(eva_func_list):
            print("func:", func_name, course_result["best_reward_normed"][i])

    print("\n============================ function mean ===========================\n")
    for i, func_name in enumerate(eva_func_list):
        print("func:", func_name, "mean:", course_result["mean_reward"][i],
              "normed mean:", course_result["normed_mean"][i])
    print("\n============================ fianl score ============================\n")
    print(args[common.CmdArgs.searcher_root], "final score: ", final_score)
    print("\n=====================================================================\n")
    return err_code, err_msg, final_score


if __name__ == "__main__":
    args = common.parse_args(common.experiment_parser("description"))
    searcher_root = args[common.CmdArgs.searcher_root]
    if not is_implement_searcher(searcher_root):
        print("please implemente class Searcher(subclass of AbstractSearcher) in ", searcher_root)
        exit(0)
    experiment(args)
    exit(0)
