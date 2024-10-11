import os
import sys
import time
import Qinit_func
from login_func import login_func
from main_proc import main_proc
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread,pyqtSignal

# 工作流进程组件
class WorkerThread(QThread):
    # 自定义信号，用于发射进度更新
    finished = pyqtSignal(str, object)  # 用于通知任务完成

    def __init__(self, login_proc):
        super().__init__()
        self.login_proc = login_proc # 登录界面对象

    def run(self):
        total_steps = 100  # 总步骤数
        for i in range(total_steps):
            time.sleep(0.1)  # 模拟处理任务的时间
            # self.progress.emit(i + 1)  # 发射进度信号
        self.finished.emit('登录成功', None)  # 任务完成后发射完成信号

'''
继承登录基类，与后端flow流程数据交互，界面相关的流程
工作流交互组件
'''
class login_proc(login_func):
    def __init__(self, proc_path: str, logger=None):
        super().__init__(proc_path, logger)

    def login_btn_verify(self):
        # 展示进度条
        self.service_progress()
        # 启动工作流进程(组件参数传递)
        self.worker_thread = WorkerThread(self)
        self.worker_thread.finished.connect(self.on_data_received)
        self.worker_thread.start()
    
    # 接收进程信号与界面交互
    def on_data_received(self,msg):
        self.dialog.accept()
        if '成功' in msg:
            self.ui.hide()
            # 实例化窗体功能
            self.main_proc = main_proc(None, self.ui, proc_path)
        else:
            self.ui.lab_info.setText(msg)
            self.start_shaking()


if __name__ == '__main__':
    # 遇到系统错误不崩溃通过错误弹框处理
    sys.excepthook = Qinit_func.error_handler
    # 资源文件目录访问(打包exe时资源文件的路径判断)
    proc_path = os.path.join(Qinit_func.source_path())
    # 实例化日志对象
    # logger = Qinit_func.logger_record()

    # 加载界面
    app = QApplication(sys.argv)
    # 实例化窗体功能
    login_proc = login_proc(proc_path)
    sys.exit(app.exec())