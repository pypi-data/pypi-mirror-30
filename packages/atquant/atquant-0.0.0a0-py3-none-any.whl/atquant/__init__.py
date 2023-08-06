# -*- coding: utf-8 -*-

'''
# # 更多辅助函数查看 atquant.utils 模块.

# # matlab 浮点型时间转换函数，查看帮助 
.. code-block:: python
    :linenos:
    
    import atquant
    import atquant.utils.datetime_func as dtfunc
    help(dtfunc)
..

# # format_atquant_log 查看帮助.
.. code-block:: python
    :linenos:
    
    import atquant
    help(atquant.format_atquant_log)
..

# 使用demo
.. code-block:: python
    :linenos:
    
    import os
    from atquant.utils.internal_util import format_atquant_log
    from atquant.data.global_variable import root_sub_dir
    
    py_log_path = os.path.join(root_sub_dir('Log'), 'sys_atquant.log')
    format_py_log_path = os.path.join(root_sub_dir('Log'), 'Fake.m')
    with open(py_log_path, 'r') as fr:
        with open(format_py_log_path, 'w+') as fw:
            format_atquant_log(fr, fw.write) # 默认使用print函数
        if os.path.exists(format_py_log_path):
            try:
                os.system('notepad "%s"' % format_py_log_path)
            except Exception as e:
                print(e)
..

# #  写入用户日志,查看帮助
.. code-block:: python
    :linenos:
    
    import atquant
    help(atquant.write_userlog)
..


# 使用demo
.. code-block:: python
    :linenos:

    from atquant.utils.logger import write_userlog
    write_userlog('this is test msg', level='info', console='this will show on console')
..    

'''



import sys
from os.path import abspath, join, dirname
sys.path.insert(0, join(abspath(dirname(__file__))))

import pandas as pd
import numpy as np
import datetime
from atquant.utils.logger import write_syslog, write_userlog
from atquant.utils.internal_util import format_atquant_log

pd.set_option('display.expand_frame_repr', False)
np.set_printoptions(threshold=np.nan)
np.seterr(all='ignore')

# 输出更多调试信息,比如跟踪函数性能,AT CMD通信，将会写入到日志文件中
# 注意：开启此开关会导致程序性能降低!!!
TRACE_DEBUG = False


