# coding=utf-8
import argparse
import os
import time

from enum import IntEnum, auto

# Python3 is used by default
PYTHONX = "python3"

SEARCH_SUCCESS = 0
ERROR_START = 200
SEARCHER_NOT_EXIST = ERROR_START + 1
SEARCHER_INIT_ERROR = ERROR_START + 2
SUGGEST_RUN_ERROR = ERROR_START + 3
SUGGEST_RESULT_ERROR = ERROR_START + 4
SUGGEST_EVALUATE_ERROR = ERROR_START + 5
RUN_TIMEOUT = ERROR_START + 6
INSTALL_PACKAGE_ERROR = ERROR_START + 7
OTHER_ERROR = ERROR_START + 8
OUT_OF_MEMORY_ERROR = ERROR_START + 9
RUNTIME_ERROR = ERROR_START + 10


class CmdArgs(IntEnum):
    uuid = auto()
    searcher_root = auto()
    data_root = auto()
    data = auto()
    result_root = auto()
    n_iteration = auto()
    n_suggestions = auto()
    n_repeat = auto()
    verbose = auto()
    timeout = auto()
    worker = auto()
    all_iters = auto()
    repear_num = auto()


CMD_STR = {
    CmdArgs.uuid: ("-u", "--uid", "uid"),
    CmdArgs.searcher_root: ("-o", "--searcher-root", "searcher file directory"),
    CmdArgs.data_root: ("-dr", "--data-root", "data set directory"),
    CmdArgs.data: ("-d", "--data", "data set file name"),
    CmdArgs.result_root: ("-rd", "--result-dir", "output directory for temporary result"),
    CmdArgs.n_iteration: ("-i", "--iteration", "number of function iterations"),
    CmdArgs.n_suggestions: ("-s", "--suggestions", "number of suggestions to provide in parallel"),
    CmdArgs.n_repeat: ("-r", "--repeat", "number of repetitions of each study"),
    CmdArgs.verbose: ("-v", "--verbose", "with verbose log"),
    CmdArgs.timeout: ("-t", "--timeout", "Timeout per experiment (0 = no timeout)"),
    CmdArgs.worker: ("-w", "--worker", "number of problem run in parallel"),
    CmdArgs.all_iters: ("-a", "--all_iter", "all iterations in one run search"),
    CmdArgs.repear_num: ("-n", "--repeat_number", "repetition number in one function"),
}


def positive_int(val_str):
    val = int(val_str)
    if val <= 0:
        msg = "expected positive, got %s" % val_str
        raise argparse.ArgumentTypeError(msg)
    return val


def add_argument(parser, arg, **kwargs):
    short_name, long_name, help = CMD_STR[arg]
    dest = arg_to_str(arg)
    parser.add_argument(short_name, long_name, dest=dest, help=help, **kwargs)


def base_parser():
    parser = argparse.ArgumentParser(add_help=False)
    return parser


def experiment_parser(description):
    parser = argparse.ArgumentParser(description=description, parents=[base_parser()])

    add_argument(parser, CmdArgs.uuid, type=str, default="test_user")
    add_argument(parser, CmdArgs.searcher_root, type=str)
    add_argument(parser, CmdArgs.data_root, type=str, default="./input/")
    add_argument(parser, CmdArgs.data, required=True, type=str, nargs="+")
    add_argument(parser, CmdArgs.result_root, type=str)
    add_argument(parser, CmdArgs.worker, default=1, type=positive_int)

    # Iteration counts used in experiments
    add_argument(parser, CmdArgs.n_iteration, default=20, type=positive_int)
    add_argument(parser, CmdArgs.n_suggestions, default=5, type=positive_int)
    add_argument(parser, CmdArgs.n_repeat, default=10, type=positive_int)
    add_argument(parser, CmdArgs.timeout, default=600, type=int)
    add_argument(parser, CmdArgs.all_iters, default=100, type=positive_int)
    add_argument(parser, CmdArgs.repear_num, default=1, type=positive_int)

    return parser


def arg_to_str(arg):
    _, dest = str(arg).split(".")
    return dest


def namespace_to_dict(args_ns):
    args = vars(args_ns)
    args = {kk: args[arg_to_str(kk)] for kk in CMD_STR if (arg_to_str(kk) in args)}
    return args


def parse_args(parser, argv=None):
    args = parser.parse_args(argv)
    args = namespace_to_dict(args)
    args[CmdArgs.all_iters] = args[CmdArgs.n_iteration]*args[CmdArgs.n_suggestions]
    if args[CmdArgs.result_root] is None:
        result_dir = "output_" + time.strftime("%Y%m%d%H%M%S", time.localtime()) + "/"
        make_dir(result_dir)
        args[CmdArgs.result_root] = result_dir
    return args


def make_dir(path):
    is_exists = os.path.exists(path)
    if not is_exists:
        os.makedirs(path)


def args_to_str(args):
    args_str = []
    for arg, value in args.items():
        short_name, *_ = CMD_STR[arg]
        args_str.append(short_name)
        args_str.append(str(value))
    return ' '.join(args_str)
