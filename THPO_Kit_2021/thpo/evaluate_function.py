# coding=utf-8
import json
import xarray as xr
import numpy as np


class EvaluateFunction():
    """ Evaluation function class
    All evaluation functions are to find the maximum value.

    Attributes:
        da: xarray type, contains all information of the data set
        dims: list type, list of the parameter name, eg:["p1", "p2", "p3"]
        parameters_config: parameters configuration, dict type:
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

        baseline: dict type, baseline of evaluation function to calculate reward
            "iters": maximum number of supported iterations
            "median": list of median scores of every iteration
            "mean": list of mean scores of every iteration
            "clip": clip reward
            "best": best reward
            "worst": worst reward
    """
    def __init__(self, path, iters):
        """ initialization of evaluation function

        Args:
            path: file path of evaluation function
            iters: number of iterations
        """
        with open(path, "r") as f:
            ds_json = json.load(f)
        self.da = xr.DataArray.from_dict(ds_json)
        self.dims = self.da.dims
        self.parameters_config = {}
        for dim in self.dims:
            assert dim in self.da.attrs, "dim not in attrs"
            self.parameters_config[dim] = self.da.attrs[dim]
        self.name = self.da.name
        self.baseline = self.da.attrs["baseline"]
        assert iters <= self.baseline["iters"], "iters is more than setting"
        self.baseline["median"] = np.array(self.baseline["median"][0:iters])
        self.baseline["mean"] = np.array(self.baseline["mean"][0:iters])

    def evaluate(self, params):
        """ evaluate reward for a suggestion point

        Args:
            params: a suggestion point, a dict in this form: {parameter_name: parameter_value, ... }.

        Returns:
            score: reward of the suggestion point
        """
        for dim in self.dims:
            assert dim in params, "missing parameter " + dim

        def get_param_value(dim, value):
            idx = np.abs(np.array(self.parameters_config[dim]["coords"]) - value).argmin()
            return self.parameters_config[dim]["coords"][idx]
        # Convert parameters to coordinates in "coords"
        new_params = {dim: get_param_value(dim, params[dim]) for dim in self.dims}

        return float(self.da.loc[new_params].values)

    def get_param_config(self):
        """ Get parameter config of evaluation function

        Returns:
            parameters_config : a dict in this form: {dim, dict{str, object}}
                parameter config of evaluation function
        """
        assert self.parameters_config is not None, "parameters config is not set."
        return self.parameters_config

    def get_baseline(self):
        """ Get baseline of evaluation function

        Returns:
            median: baseline median
            mean: baseline mean
            best: best reward of evaluation function
            clip: clip reward of evaluation function
        """
        return self.baseline["median"], self.baseline["mean"], self.baseline["best"], self.baseline[
            "clip"]

    def get_init_score(self):
        """ Get init reward of evaluation function, the lower bound of the reward of the
            evaluation function, used for reward initialization

        Returns:
            worst: the lower bound of the reward of the evaluation function
        """
        return self.baseline["worst"]

    def get_name(self):
        return self.name
