from my_task.main import app


# celery的任务必须写在tasks文件中  别的文件不识别
@app.task(name="upload_file")  # name 可以指定当前的任务名称，如果不写，则使用默认的函数名作为任务名
def upload_file():
    print('上传文件')
    return "hello"
