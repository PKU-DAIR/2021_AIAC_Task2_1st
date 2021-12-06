# coding=utf-8
import copy
import traceback

from concurrent.futures import ProcessPoolExecutor, wait, ALL_COMPLETED
from subprocess import run, PIPE, TimeoutExpired

import thpo.common as common


def run_search(args):
    """ Evaluate the searcher on all evaluation functions

    Args:
        args: arguments for running searching task

    Returns:
        err_code: error code of searching task
        err_msg: error message of searching task
    """
    print("run_search:", args)
    eva_func_list = args[common.CmdArgs.data]
    n_function = len(eva_func_list)
    n_repeat = args[common.CmdArgs.n_repeat]
    process_list = []
    workers = min(args[common.CmdArgs.worker], n_function)
    err_code, err_msg, timeout_count = common.SEARCH_SUCCESS, "", 0
    with ProcessPoolExecutor(max_workers=workers) as t:
        for func_idx in eva_func_list:
            task = t.submit(search_in_function, args, func_idx)
            process_list.append(task)
        wait(process_list, return_when=ALL_COMPLETED)
        for idx, task in enumerate(process_list):
            try:
                err_code, err_msg, t_count = task.result()
                if t_count > 0:
                    timeout_count = timeout_count + t_count
            except Exception as e:
                print(traceback.format_exc())
                err_code, err_msg = common.OTHER_ERROR, "other error "+repr(e)
                print("task timeout %s , %s", eva_func_list[idx], e)
    if err_code == common.RUN_TIMEOUT:
        err_msg = "timeout rate " + str(timeout_count/(n_repeat*n_function))
    return err_code, err_msg


def search_in_function(args, eva_func_name):
    """ Evaluate the searcher on one evaluation function

    Args:
        args: arguments for running searching task
        eva_func_name: Name of evaluation function

    Returns:
        err_code: error code of searching task
        err_msg: error message of searching task
        timeout_count: the number of timeouts
    """
    err_code, err_msg = common.SEARCH_SUCCESS, ""
    timeout_count = 0
    n_repeat = args[common.CmdArgs.n_repeat]

    timeout = args[common.CmdArgs.timeout] + 10
    for repear_num in range(1, n_repeat+1):
        cur_args = copy.deepcopy(args)
        cur_args[common.CmdArgs.data] = str(eva_func_name)
        cur_args[common.CmdArgs.repear_num] = repear_num
        run_cmd = common.PYTHONX + " ./thpo/run_search_one_time.py " + common.args_to_str(cur_args)
        print("search_in_function run_cmd:", run_cmd)
        try:
            status = run(run_cmd, stderr=PIPE, shell=True, timeout=timeout)
            if status.returncode != 0:
                print("status:", str(status.stderr))
                err_code, err_msg = status.returncode, str(status.stderr)
                if err_code == common.RUN_TIMEOUT:
                    timeout_count = timeout_count + 1
                continue
        except TimeoutExpired:
            err_code, err_msg = common.RUN_TIMEOUT, "Run timeout"
            timeout_count = timeout_count + 1
            print("run search fun:", str(eva_func_name), "repeat:", str(repear_num),
                "timeout limit", str(timeout), "seconds.")

    return err_code, err_msg, timeout_count
