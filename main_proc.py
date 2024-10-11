import os
import sys
import time
import Qinit_func
from main_func import main_func
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import QThread, pyqtSignal, QMutexLocker, QWaitCondition, QMutex
from qfluentwidgets import StateToolTip


# 工作流进程组件
class WorkerThread(QThread):
    # 自定义信号，用于发射进度更新
    finished = pyqtSignal(str)  # 用于通知任务完成

    def __init__(self, condition, mutex, main_proc, login_obj):
        super().__init__()
        self.condition = condition
        self.mutex = mutex
        self.main_proc = main_proc   # 主界面对象
        self.login_obj = login_obj   # 登录对象

    def run(self):
        total_steps = 120  # 总步骤数
        for i in range(total_steps):
            time.sleep(0.1)  # 模拟处理任务的时间
        #自动锁管理通知完成
        with QMutexLocker(self.mutex):self.condition.wakeAll()
        self.finished.emit('执行完毕')  # 任务完成后发射完成信号

# 工作进度圆圈方式
class ProgressThread(QThread):
    # 自定义信号，用于发射进度更新
    progress = pyqtSignal(int)

    def __init__(self, condition, mutex):
        super().__init__()
        self.condition = condition
        self.mutex = mutex

    def run(self):
        total_steps = 99  # 总步骤数
        for i in range(total_steps):
            time.sleep(0.1)  # 模拟处理任务的时间
            self.progress.emit(i + 1)  # 发射进度信号
        
        #自动锁管理等待任务完成
        with QMutexLocker(self.mutex):self.condition.wait(self.mutex)
        self.progress.emit(100) #发送100%完成信号

'''
继承主界面基类，与后端flow流程数据交互，界面相关的流程
工作流交互组件
'''
class main_proc(main_func):
    def __init__(self, obj, parent_ui: QWidget, proc_path: str, logger=None):
        super().__init__(parent_ui, proc_path, logger)
        # 登录对象
        self.login_obj = obj 

    def task_exec(self):
        # 禁用所有按钮控件
        Qinit_func.disable_all_buttons(self.ui)
        self.dropDownToolButton.setEnabled(False)
        # 展示进度栏
        self.service_progress_ring()
        # 展示提示栏
        self.stateTooltip = StateToolTip('正在执行任务', '请耐心等待哦~~', self.ui)
        # 移动按钮到右下角
        size = self.ui.size()
        self.stateTooltip.move(size.width(
        ) - self.stateTooltip.width() - 20, size.height() - self.stateTooltip.height() - 20)
        self.stateTooltip.show()

        # 自动管理锁，实现进程同步完成
        condition = QWaitCondition()
        mutex = QMutex()

        # 启动工作流进程(组件参数传递)
        self.worker_thread = WorkerThread(condition, mutex, self, self.login_obj)
        self.worker_thread.finished.connect(self.on_data_received)
        self.worker_thread.start()
        # 工作流进程监督进度条
        self.progress_thread = ProgressThread(condition, mutex)
        self.progress_thread.progress.connect(self.on_data_progress)
        self.progress_thread.start()

    # 接收工作流进程信号与UI界面交互
    def on_data_progress(self, value):
        self.progressRing.setValue(value)

    def on_data_received(self, msg):
        if self.stateTooltip:
            self.stateTooltip.setContent('任务完成啦 😆')
            self.stateTooltip.setState(True)
            self.stateTooltip = None
            # 隐藏进度框
            self.progressRing.close()
            # 启用所有按钮控件
            Qinit_func.enable_all_buttons(self.ui)
            # 启用保存按钮
            self.dropDownToolButton.setEnabled(True)


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
    main_proc = main_proc(None, None, proc_path)
    sys.exit(app.exec())
