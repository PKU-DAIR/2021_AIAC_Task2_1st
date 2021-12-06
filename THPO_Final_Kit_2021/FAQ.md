# 常见问题

## 评测环境environments.txt内容很多，安装过程中出很多错误，怎么处理？

`environments.txt` 只是说明裁判后台的评测环境中已安装包的版本信息，如果程序没有用到不用进行安装，选手测试环境只要安装工具包中的`requirements.txt`即可。

## environments.txt中的包版本太低了，希望更新/降级包版本怎么办？

将需要的包信息写到选手算法目录下的`requirements.txt`即可，打包程序会下载相应版本的包并打包好；系统限制只能上传的zip包不能超过300MB，如果最后打包结果超出，请到QQ群联系工作人员处理。

## 实现的优化类文件名必须为 searcher.py，类名必须为Searcher吗？算法不能个性命名吗？

是的，文件名和类型必须按照要求命名；建议使用文件夹名字对算法进行自定义命名。

## 若程序代码超时，在结果中是否能体现？

结果中会返回超时次数，以及如果代码运行错误会提示错误原因，超时会影响最终得分，具体如何影响参见:

* 参赛手册：[自动超参数优化参赛手册](https://docs.qq.com/doc/p/681e40251e75740c654289ddfb827b7571107693?dver=2.1.27141849)  *[3.评估方法] 章节*

## 为什么同一份代码提交，分数差异比较大？

自动化参数优化算法在面对未知的参数空间时，始终会有一定的探索成分，因而引入了随机性。当重复(Repeat)评估次数不够大时，算法会有一定的波动，这都是合理的，所以同一个算法多次提交可能会有不同的分数。

## 那为什么不设置足够大的重复Repeat次数呢？

的确，设置了足够大的Repeat次数选手得分的分数就能稳定下来，但代价就是得到评估结果非常慢！因此为了平衡等待时间和稳定性，我们设计了`训练阶段`和`竞技阶段`。

其中，`训练阶段`Repeat=10，可以较快的反馈给选手算法得分，方便选手调试算法，选手在这个阶段目的是找出足够优秀的算法来竞技；而在`竞技阶段`，Repeat次数足够大，此时的得分可以确保是稳定的，我们以此阶段的得分作为**最终得分**进行排名。

因此我们补充说明下，在`训练阶段`的排名和`竞技阶段`的排名可能会有所出入。

## 比赛官方是否有联系方式，如何联系工作人员？

更多信息，请加入QQ群：**`789171326`**，工作人员会在群内进行解答。

---

# Frequently Asked Questions

## The environment.txt has a lot of packages in the evaluation environment, and there are many errors during the installation process. How to deal with it?

The environments.txt only describes the version information of the installed packages in the evaluation environment of the judge server. If the packages are not used, you don’t need to install them. The players’ test environment only needs to install the `requirements.txt` in the toolkit.

## The package version in environments.txt is too low, what should I do if I want to update the package?

Just write the required package information to `requirements.txt` in the player algorithm directory. The packaging program will download the corresponding version of the package and package it; or you can go to the QQ group to contact the staff to see if you can directly upgrade the package.

## Must the file name of searcher class be searcher.py? And must the class name be Searcher?

Yes, you must follow the requirements; it is recommended to use the folder name to  customized the name of algorithm.

## If the program code times out, can it be reflected in the result?

The result will return the number of timeouts, and if the code runs incorrectly, it will prompt the cause of the error. The timeout will affect the final score. For details, please refer to

* Contest manual：[Automated Hyperparameter Optimization Contest manual](https://docs.qq.com/doc/p/9b3e04cecb9631e393e4316d4b10eaa781b5fd61?dver=2.1.27141849)  *[3. Evaluation Method]  chapter*

## Why the scores for submitting the same code vary widely？

When the automated hyperparameter optimization algorithm faces an unknown parameter space, there will always be a certain amont of exploration, which introduces randomness. When the repeat times of evaluation is not large enough, the score of algorithm will vary widely, which is reasonable, so multiple submissions of the same algorithm may have different scores.

## Then why not set a large enough number of repeats?

Indeed, the player's score can be stabilized by setting a large enough Repeat number, but the price is that the evaluation process could be very slow!Therefore, in order to balance the waiting time and stability, we designed `training phase` and `competitive phase`.

Among them, Repeat=10 in `training phase` can provide quick feedback to the player's algorithm score, which is convenient for the player to debug the algorithm. The goal of the player at this stage is to find a sufficiently good algorithm to compete.and in `competitive phase`, the number of Repeats is large enough. The score can be guaranteed to be stable, and we rank the score at `competitive phase`as the **final score**.

Therefore, we added that there may be discrepancies between the ranking in `training phase` and the ranking in `competitive phase`.

## Does the competition organizer have contact information and how can I contact the staff?

For more information, please join the QQ group **`789171326`**, the staff will answer your question in the group

