#!/bin/bash

# Dataset name
DATASET="data-2 data-30"

# Default experimental parameters in competition
# Number of iterations
# To run faster, you can set N_ITERATION smaller in local test
N_ITERATION=20
# number of suggestions
N_SUGGESTION=5
# number of repeats
N_REPEAT=10

# check if python3 is installed
command -v python3 >/dev/null 2>&1 || (echo err:python3 is not found, please install python3 or replace PYTHONX in thpo/common.py && exit 1)

# Test random search
# Directory of searcher.py
SEARCHER="example_random_searcher"

# Run searcher in all dataset
python3 main.py -o $SEARCHER -d $DATASET -i $N_ITERATION -s $N_SUGGESTION -r $N_REPEAT

# Test bayesian optimization
# This searcher costs about 10 minutes.
# SEARCHER="example_bayesian_optimization"
# python3 main.py -o $SEARCHER -d $DATASET -i $N_ITERATION -s $N_SUGGESTION -r $N_REPEAT


# Run searcher in one dataset for one repeat
# ONE_DATASET="data-2"
# python3 ./thpo/run_search_one_time.py -o $SEARCHER -d $ONE_DATASET -i $N_ITERATION -s $N_SUGGESTION -n 1
