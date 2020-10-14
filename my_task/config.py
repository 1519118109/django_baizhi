# 任务队列的链接地址
from celery.schedules import crontab

broker_url = "redis://192.168.21.134:7000/5"
# 结果队列的链接地址
result_backend = "redis://192.168.21.134:7000/6"

# 任务队列的链接地址
from my_task.main import app


# 定时任务的调度
app.conf.beat_schedule = {
    'check_order_out_time': {
        # 本次定时任务要调度的任务
        'task': 'check_order',
        # 定时任务调度的周期
        'schedule': 30.0,#crontab(minute='*/30',)
        # 'args': (16, 16)    # 是一个函数  有参数可以通过此函数传递  没参数无需传递
    },
}
