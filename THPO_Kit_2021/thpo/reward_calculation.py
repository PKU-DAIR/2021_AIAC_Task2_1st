# coding=utf-8
import os
import json
import numpy as np

import thpo.common as common
from thpo.evaluate_function import EvaluateFunction


def calculate_reward(args):
    """ Calculate rewards for the searcher

    Args:
        args: arguments for running searching task

    Return:
        course_result: dict type:
            best: best rewards of every evaluation function
            rand_perf: random searcher median rewards of every evaluation function
            best_reward: best rewards of every repeat on every evaluation function
            best_reward_normed: best normalized rewards of every repeat on every evaluation function
            mean_reward: mean rewards on every evaluation function
            normed_mean: normalized mean rewards on every evaluation function
        mean_normed_mean: final reward
    """
    best, rand_perf = get_baseline_perf(args)
    origin_reward = get_origin_reward(args)
    # Calculate rewards of every repeat on every evaluation function
    accumulate_reward = np.maximum.accumulate(origin_reward, axis=1)
    best_reward = accumulate_reward[:, -1, :]
    # Calculate best normalized rewards of every repeat on every evaluation function
    best_reward_normed = (best_reward.T - rand_perf) / (best - rand_perf)
    best_reward_normed = np.clip(best_reward_normed, 0.0, 1.0)
    best_reward_normed = best_reward_normed.T
    # Calculate the trim mean rewards on every evaluation function:
    #   1. Remove the highest and the lowest score 
    #   2. Calculate the mean of the rest scores
    sort_repeat = np.sort(best_reward, axis=1)
    if sort_repeat.shape[1] >= 3:
        mean_reward = np.mean(sort_repeat[:, 1:-1], axis=1)
    else:
        mean_reward = np.mean(sort_repeat, axis=1)
    # Calculate normalized mean rewards of every evaluation function
    normed_mean = (mean_reward - rand_perf) / (best - rand_perf)
    normed_mean = np.clip(normed_mean, 0.0, 1.0)
    # Calculate final reward which is the average of normalized mean rewards of every evaluation function
    mean_normed_mean = np.mean(normed_mean)

    course_result = {
        "best": best,
        "rand_perf": rand_perf,
        "best_reward": best_reward,
        "best_reward_normed": best_reward_normed,
        "mean_reward": mean_reward,
        "normed_mean": normed_mean,
    }
    return course_result, mean_normed_mean


def get_baseline_perf(args):
    """ Get baseline performance of every evaluation function

    Args:
        args: arguments for running searching task

    Return:
        best: best rewards of every evaluation function
        rand_perf: random searcher median rewards of every evaluation function
    """
    all_iter = args[common.CmdArgs.all_iters]
    eva_func_list = args[common.CmdArgs.data]
    n_function = len(eva_func_list)
    best = np.zeros([n_function])
    rand_perf = np.zeros([n_function])
    for idx, eva_func_name in enumerate(eva_func_list):
        eva_func_file = args[common.CmdArgs.data_root] + str(eva_func_name)
        eva = EvaluateFunction(eva_func_file, all_iter)
        rand_median_perf, _, best_opt, _ = eva.get_baseline()
        best[idx] = best_opt
        rand_perf[idx] = rand_median_perf[-1]
    return best, rand_perf


def get_origin_reward(args):
    """ Get oringal searcher rewards of every evaluation function

    Args:
        args: arguments for running searching task

    Return:
        origin_reward: oringal searcher rewards, 'numpy.ndarray' class, shape:
           [number of evaluation functions, number of iterations, number of repetitions]
    """
    n_repeat = args[common.CmdArgs.n_repeat]
    all_iter = args[common.CmdArgs.all_iters]
    eva_func_list = args[common.CmdArgs.data]
    n_function = len(eva_func_list)
    origin_reward = np.zeros([n_function, all_iter, n_repeat])
    for idx, eva_func_name in enumerate(eva_func_list):
        eva_func_file = args[common.CmdArgs.data_root] + str(eva_func_name)
        eva = EvaluateFunction(eva_func_file, all_iter)
        function_reward = np.full([all_iter, n_repeat], eva.get_init_score(), dtype=float)
        result_file_name = args[common.CmdArgs.result_root] + eva_func_name
        if os.path.exists(result_file_name):
            with open(result_file_name, "r") as result_file:
                for line in result_file:
                    p = json.loads(line)
                    function_reward[p["iter"] - 1, p["repeat"] - 1] = p["reward"]
        origin_reward[idx] = function_reward
    return origin_reward

