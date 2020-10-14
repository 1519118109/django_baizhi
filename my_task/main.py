import os

import django
from celery import Celery

# 主程序

# 创建celery实例对象  需要指定每个celery实例的名称
app = Celery('edu')

# 把celery与django进行结合 加载django的配置文件
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_baizhi.settings.develop")
django.setup()

# 通过celery的实例对象加载配置
app.config_from_object("my_task.config")

# 添加任务到实例对象中  自动找到该路径下的tasks文件中的任务
app.autodiscover_tasks(['my_task.sms','my_task.upload_file','my_task.change_order'])

# 启动celery  在项目的根目录下执行命令
# celery -A my_task.main worker --loglevel=info