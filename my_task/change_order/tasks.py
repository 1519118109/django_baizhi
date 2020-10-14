from datetime import datetime

from my_task.main import app
from order.models import Order

# celery的任务必须写在tasks文件中  别的文件不识别
@app.task(name="check_order")  # name 可以指定当前的任务名称，如果不写，则使用默认的函数名作为任务名
def check_order():
    orders = Order.objects.filter(is_delete=False,is_show=True).all()
    for order in orders:
        if order.order_status==0:
            order.order_status = 3
            order.save()
    return