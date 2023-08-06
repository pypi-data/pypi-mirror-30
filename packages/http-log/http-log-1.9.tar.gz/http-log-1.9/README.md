## HTTP LOG

*urllib2 httplib2 requests日志小工具*

### 安装方法
1. pip install httplog

### 全局替换

在python 的 sitecustomize.py文件末尾，添加下面代码

文件路径：`python -m site --user-site`

```python
from httplog import patcher
patcher.monkey_patch()
```

### 项目替换
单个项目替换，如django项目开发默认下，在manage.py中添加下面代码

```python
from httplog import patcher
patcher.monkey_patch()
```