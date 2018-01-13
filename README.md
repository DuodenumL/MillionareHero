# MillionareHero
百万英雄辅助程序，可以自动给出建议选项，并且微信发送到指定好友。
## 简介
西瓜视频百万英雄的答题辅助程序。使用Python3开发。

主要原理是对手机运行界面进行截图，使用百度的文字识别API获取问题和选项，爬取搜索引擎结果后通过算法进行打分，并利用`itchat`将结果自动发送给指定的好友。运行一次大概4秒钟左右，答案不保证完全准确，尽量用作参考。
## 如何使用
代码分为两部分，服务器端代码`MillionareHero.py`和客户端代码`AutoAnswer.py`。两部分代码不要求一定在同一台电脑上运行。需要安装的依赖在`reqirements.txt`中。

+ 首先运行`MillionareHero.py`，注意其中搜索引擎可以在百度和Google之间切换。Server会监听8995端口（可修改）。

+ 将Android手机打开USB调试，连接电脑，确保电脑可以使用adb连接手机。

+ 将`AutoAnswer.py`中的`APP_KEY`, `APP_ID`, `SECRET_KEY`换为自己的百度文字识别API应用信息对应字段，将`users`内添加想要向其发送微信的好友昵称/微信号/备注。

+ 运行`AutoAnswer.py`，扫描出现的二维码。

+ 好了。