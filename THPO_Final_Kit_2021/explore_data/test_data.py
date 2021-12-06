import sys
sys.path.insert(0, '.')
from thpo.data_utils import get_evaluator, get_all_parameters, get_value

path = './input/data-30'
#path = './input/data-2'
evaluator = get_evaluator(path)

for parameter in get_all_parameters(evaluator):
    day = None
    value_name = 'm'
    result = get_value(evaluator, parameter, day, value_name)
    print(result)
    break
