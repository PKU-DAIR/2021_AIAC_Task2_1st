# QQ浏览器2021AI算法大赛 - 自动超参数优化竞赛

### ACM CIKM 2021 AnalyticCup

在信息流推荐业务场景中普遍存在模型或策略效果依赖于“超参数”的问题，而“超参数"的设定往往依赖人工经验调参，不仅效率低下维护成本高，而且难以实现更优效果。因此，本次赛题以超参数优化为主题，从真实业务场景问题出发，并基于脱敏后的数据集来评测各个参赛队伍的超参数优化算法。本赛题为超参数优化问题或黑盒优化问题：给定超参数的取值空间，每一轮可以获取一组超参数对应的Reward，要求超参数优化算法在限定的迭代轮次内找到Reward尽可能大的一组超参数，最终按照找到的最大Reward来计算排名。

## 1. 重要资源

* 比赛官网：[QQ浏览器2021AI算法大赛](https://algo.browser.qq.com/)
* 参赛手册：[自动超参数优化参赛手册](https://docs.qq.com/doc/p/681e40251e75740c654289ddfb827b7571107693?dver=2.1.27141849)
* 代码仓库：[THPO-Kit Github](https://github.com/QQ-Browser-AI-Algorithm-Competition/THPO_Kit_2021)
* 实现和评分参考：[THPO-Kit 介绍文档](https://docs.qq.com/doc/p/ab5c751cdc66a2f7abde4a3701ce375dd56ea713?dver=2.1.27141849)
* 代码提交：[比赛代码提交入口](https://algo.browser.qq.com/profile.html)
* 比赛FAQ：[比赛常问问题](https://github.com/QQ-Browser-AI-Algorithm-Competition/THPO_Kit_2021/blob/main/FAQ.md#%E5%B8%B8%E8%A7%81%E9%97%AE%E9%A2%98)

## 2.代码结构

```
|--example_random_searcher  随机算法代码提交示例
|  `--searcher.py
|
|--example_bayesian_optimization 贝叶斯优化算法提交示例
|  |--requirements.txt     提交附加程序包示例
|  `--searcher.py
|
|--input                   测试评估函数数据
|  |--data-2
|  `--data-30
|
|--thpo                    thpo比赛工具包
|  |--__init__.py
|  |--abstract_searcher.py
|  |--common.py
|  |--evaluate_function.py
|  |--reward_calculation.py
|  |--run_search_one_time.py
|  `--run_search.py
|
|--main.py                 测试主程序文件
|--local_test.sh           本地测试脚本
|--prepare_submission.sh   提交代码前打包脚本
|--environments.txt        评测环境已经安装的包
`--requirements.txt        demo程序依赖的包环境
```

## 3. 快速入门

### 3.1 环境搭建

THPO-Kit程序工具包使用python3编写，程序依赖包在requirements.txt中，需要安装依赖包才能执行，使用pip3安装依赖包：

```shell
pip3 install -r requirements.txt
```

### 3.2 算法创建

1. 参照 **example_randon_searcher**，新建一个自己算法的目录**my_algo**
2. 在**my_algo**目录下新建**searcher.py**文件
3. 在**searcher.py**文件里实现自己的**Searcher**类（文件名和类名不允许自定义）
4. 实现 **\_\_init\_\_** 和 **suggest** 函数
5. 修改 **local_test.sh**，将**SEARCHER**修改为**my_algo**
6. 执行 **local_test.sh** 脚本，将得到算法的执行结果

*Step 1 - Step 2:[root folder]*

```
|--my_algo
|  |--requirements.txt
|  `--searcher.py 
|--local_test.sh
```

*Step 3 - Step 4:[searcher.py]*

```python
# 必须引入searcher抽象类，必不可少
from thpo.abstract_searcher import AbstractSearcher
from random import randint

class Searcher(AbstractSearcher):
    searcher_name = "RandomSearcher"

    def __init__(self, parameters_config, n_iter, n_suggestion):
        AbstractSearcher.__init__(self, 
                                  parameters_config, 
                                  n_iter,
                                  n_suggestion)

    def suggest(self, suggestion_history, n_suggestions=1):
        next_suggestions = []
        for i in range(n_suggestions):
            next_suggest = {
                name: 
                conf["coords"][randint(0,len(conf["coords"])-1)]
                for name, conf in self.parameters_config.items()
            }
            next_suggestions.append(next_suggest)
        return next_suggestions
```

*Step 5:[local_test.sh]*

```
SEARCHER="my_algo"
```

### 3.3 本地运行

执行脚本local_test.sh进行本地评测

```shell
./local_test.sh
```

执行结果：

```
====================== run search result ========================
 err_code:  0  err_msg:  
========================= iters means ===========================
func: data-2 iteration best: [25.24271821 26.36435157 12.77928619 10.19180929 11.3147711  10.17430656
 12.77928619 27.79752169 26.36793589 11.12007615]
func: data-30 iteration best: [-0.95264345 -0.27725879 -0.36873091 -0.68088963 -0.28840479 -0.50006427
 -0.32088949 -0.78627201 -0.53204227 -0.98427191]
========================= fianl score ============================
example_bayesian_optimization final score:  0.47173337831255463
==================================================================
```

### 3.4 提交比赛代码

使用prepare_submission.sh 脚本打包，提交打包后的searcher程序包到[比赛代码提交入口](https://algo.browser.qq.com/profile.html)。

```shell
./prepare_submission.sh example_random_searcher
```

执行结果：

```
upload_example_random_searcher_08131917
  adding: requirements.txt (stored 0%)
  adding: searcher.py (deflated 66%)
----------------------------------------------------------------
Built achive for upload
Archive:  ./upload_example_random_searcher_08131917.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
        0  08-13-2021 19:17   requirements.txt
     3767  08-13-2021 19:17   searcher.py
---------                     -------
     3767                     2 files
For scoring, upload upload_example_random_searcher_08131917.zip at address:
https://algo.browser.qq.com/
```

---

---

# QQ Browser 2021 AI Algorithm Competiton - Automated Hyperparameter Optimization Contest

### ACM CIKM 2021 AnalyticCup

The choices of hyperparameters have critical effects on models or strategies in recommendation systems. But the hyperparameters are mostly chosen based on experience, which brings high maintenance costs and sub-optimal results. Thus, this track aims at automated hyperparameters optimization based on anonymized realistic industrial tasks and datasets. Given the space of all possible hyperparameters' values, a reward could be achieved with a set of hyperparameters in each iteration. The participants are asked to maximize the reward within a given limit of iterations with a hyperparameters optimization algorithm. The final rank of the participants will be the rank of their maximum reward.

## 1.Resource

* Official website：[QQ Browser 2021 AI Algorithm Competiton](https://algo.browser.qq.com/#en)
* Contest manual：[Automated Hyperparameter Optimization Contest manual](https://docs.qq.com/doc/p/9b3e04cecb9631e393e4316d4b10eaa781b5fd61?dver=2.1.27141849)
* Code repository：[THPO-Kit Github](https://github.com/QQ-Browser-AI-Algorithm-Competition/THPO_Kit_2021)
* API reference & ranking rules：[Introduction to THPO-Kit](https://docs.qq.com/doc/p/f274d4d7a1e666b652048b72fb6d3a946ed18c7f?dver=2.1.27141849)
* Code submission：[Code submission entry](https://algo.browser.qq.com/profile.html#en)
* Competition FAQ：[Frequently asked questions](https://github.com/QQ-Browser-AI-Algorithm-Competition/THPO_Kit_2021/blob/main/FAQ.md#frequently-asked-questions)

## 2.Repo structure

```
|--example_random_searcher   	    # example of random search
|  `--searcher.py
|
|--example_bayesian_optimization    # example of bayesian optimization
|  |--requirements.txt              # extra paackge requirement
|  `--searcher.py
|
|--input                            # testcases
|  |--data-2
|  `--data-30
|
|--thpo                             # thpo-kit
|  |--__init__.py
|  |--abstract_searcher.py
|  |--common.py
|  |--evaluate_function.py
|  |--reward_calculation.py
|  |--run_search_one_time.py
|  `--run_search.py
|
|--main.py                          # main
|--local_test.sh                    # script for local test
|--prepare_submission.sh            # script for submission
|--environments.txt                 # packages installed in remote envrionment
`--requirements.txt                 # demo requirements
```

## 3. Quick start

### 3.1 Environment setup

The THPO-Kit program toolkit is written in python3. The program dependency packages are in requirements.txt, and the dependency packages needs to be installed to execute scripts. Use pip3 to install the dependency package:

```shell
pip3 install -r requirements.txt
```

### 3.2 Create a searcher

1. Refer to **example_randon_searcher**, create a new directory **my_algo** for your algorithm
2. Create a new **searcher.py** file in the **my_algo** directory
3. Implement your own **Searcher** class in the **searcher.py** file (the file name and class name are not allowed to be customized)
4. Implement **\_\_init\_\_** and **suggest** functions
5. Modify **local_test.sh** and change **SEARCHER** to **my_algo**
6. Execute the **local_test.sh** script to get the results of the algorithm

*Step 1 - Step 2:[root folder]*

```
|--my_algo
|  |--requirements.txt
|  `--searcher.py 
|--local_test.sh
```

*Step 3 - Step 4:[searcher.py]*

```python
# MUST import AbstractSearcher from thpo.abstract_searcher
from thpo.abstract_searcher import AbstractSearcher
from random import randint

class Searcher(AbstractSearcher):
    searcher_name = "RandomSearcher"

    def __init__(self, parameters_config, n_iter, n_suggestion):
        AbstractSearcher.__init__(self, 
                                  parameters_config, 
                                  n_iter,
                                  n_suggestion)

    def suggest(self, suggestion_history, n_suggestions=1):
        next_suggestions = []
        for i in range(n_suggestions):
            next_suggest = {
                name: 
                conf["coords"][randint(0,len(conf["coords"])-1)]
                for name, conf in self.parameters_config.items()
            }
            next_suggestions.append(next_suggest)
        return next_suggestions
```

*Step 5:[local_test.sh]*

```
SEARCHER="my_algo"
```

### 3.3 Local test

Execute the script local_test.sh for local evaluation

```shell
./local_test.sh
```

Execution output：

```
====================== run search result ========================
 err_code:  0  err_msg:  
========================= iters means ===========================
func: data-2 iteration best: [25.24271821 26.36435157 12.77928619 10.19180929 11.3147711  10.17430656
 12.77928619 27.79752169 26.36793589 11.12007615]
func: data-30 iteration best: [-0.95264345 -0.27725879 -0.36873091 -0.68088963 -0.28840479 -0.50006427
 -0.32088949 -0.78627201 -0.53204227 -0.98427191]
========================= fianl score ============================
example_bayesian_optimization final score:  0.47173337831255463
==================================================================
```

### 3.4 Submission

Use  **prepare_submission.sh** script to create a zip file, and submit the zip file to competition website [Code submission entry](https://algo.browser.qq.com/profile.html#en).

```shell
./prepare_submission.sh example_random_searcher
```

Execution output:

```shell
upload_example_random_searcher_08131917
  adding: requirements.txt (stored 0%)
  adding: searcher.py (deflated 66%)
----------------------------------------------------------------
Built achive for upload
Archive:  ./upload_example_random_searcher_08131917.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
        0  08-13-2021 19:17   requirements.txt
     3767  08-13-2021 19:17   searcher.py
---------                     -------
     3767                     2 files
For scoring, upload upload_example_random_searcher_08131917.zip at address:
https://algo.browser.qq.com/
```


