import sys
import os
import re
import Qinit_func
import pandas as pd
from res import resource_rc
from abc import abstractmethod
from PyQt6 import uic
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QEasingCurve, QUrl
from PyQt6.QtWidgets import QApplication, QWidget, QFileDialog, QVBoxLayout
from qfluentwidgets import PushButton, FlowLayout, TogglePushButton, RoundMenu, PrimaryDropDownToolButton, ToolButton, ProgressRing, MessageBoxBase, SubtitleLabel, LineEdit
from qfluentwidgets import FluentIcon as FIF

class CustomMessageBox(MessageBoxBase):
    """ Custom message box """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel('邮件发送至', self)
        self.urlLineEdit = LineEdit(self)

        self.urlLineEdit.setPlaceholderText('请输入Email地址')
        self.urlLineEdit.setClearButtonEnabled(True)

        # add widget to view layout
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.urlLineEdit)

        # change the text of button
        self.yesButton.setText('发送')
        self.cancelButton.setText('取消')

        self.widget.setMinimumWidth(350)
        self.yesButton.setDisabled(True)
        self.urlLineEdit.textChanged.connect(self._validateUrl)

        # self.hideYesButton()

    def _validateUrl(self, text):
        self.yesButton.setEnabled(self.is_valid_email(text))

    def is_valid_email(self, email):
        # 使用正则表达式验证电子邮件格式
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None


class main_func():
    def __init__(self, parent_ui: QWidget, proc_path: str, logger=None):
        self.parent_ui = parent_ui
        self.logger = logger
        self.proc_path = proc_path
        self.stateTooltip = None
        
        # 加载窗体UI
        self.ui = uic.loadUi(proc_path + os.sep + 'view\main_view.ui')
        # 动态加载组件
        self.Dynamically_components()

        # 将窗口屏幕居中
        Qinit_func.Center_the_window(self.ui)
        # 窗体设置
        self.ui.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # 去除窗口边框
        # self.ui.setAttribute(
        #     Qt.WidgetAttribute.WA_TranslucentBackground)  # 设置背景透明
        # self.ui.setStyleSheet(
        #     "background-color: rgba(255, 255, 255, 180);")  # 设置背景颜色和透明度

        # 界面拖动功能实现
        self.ui._start_position = None  # 记录鼠标拖动的起始位置
        self.ui.mousePressEvent = Qinit_func.mousePressEvent.__get__(self)
        self.ui.mouseMoveEvent = Qinit_func.mouseMoveEvent.__get__(self)
        self.ui.mouseReleaseEvent = Qinit_func.mouseReleaseEvent.__get__(self)

        # 显示登录窗口
        self.ui.show()

    # 动态创建组件
    def Dynamically_components(self):
        # 创建一个垂直布局
        self.main_v_layout = QVBoxLayout()

        # 创建流动布局
        self.top_layout = FlowLayout(needAni=True)
        # 布局样式设置
        self.top_layout.setAnimation(250, QEasingCurve.Type.OutQuad)
        self.top_layout.setContentsMargins(30, 30, 30, 30)
        self.top_layout.setVerticalSpacing(10)
        self.top_layout.setHorizontalSpacing(10)

        # ----------------------添加需要的组件--------------------------#
        # 返回登录界面按钮
        self.btn_return = ToolButton(FIF.EMBED)
        self.top_layout.addWidget(self.btn_return)
        self.btn_return.clicked.connect(self.return_login)

        # 添加上传按钮
        self.upload_data = None
        self.btn_upload = PushButton(FIF.UP, '上传文件(7z)')
        self.btn_upload.setObjectName("btn_upload")
        self.top_layout.addWidget(self.btn_upload)
        self.btn_upload.clicked.connect(self.upload_file)

        # 添加执行按钮
        self.btn_exec = TogglePushButton(FIF.SEND, '执行任务')
        self.btn_exec.setObjectName("btn_exec")
        self.top_layout.addWidget(self.btn_exec)
        self.btn_exec.clicked.connect(self.task_exec)

        # 添加下载或邮件按钮
        self.menu = RoundMenu(parent=self.ui)
        self.menu.addAction(QAction(FIF.SEND_FILL.icon(), '发送'))
        self.menu.addAction(QAction(FIF.SAVE.icon(), '保存'))
        self.dropDownToolButton = PrimaryDropDownToolButton(FIF.MAIL, self.ui)
        self.dropDownToolButton.setMenu(self.menu)
        self.top_layout.addWidget(self.dropDownToolButton)
        self.menu.triggered.connect(self.on_menu_action_triggered)
        # self.dropDownToolButton.setEnabled(False)

        # 创建流动布局，将流动布局添加到主布局
        self.middle_layout = FlowLayout(needAni=True)
        # 布局样式设置
        self.middle_layout.setAnimation(250, QEasingCurve.Type.OutQuad)
        self.middle_layout.setContentsMargins(30, 30, 30, 30)
        self.middle_layout.setVerticalSpacing(10)
        self.middle_layout.setHorizontalSpacing(10)

        # 将流动布局添加到垂直布局中
        self.main_v_layout.addLayout(self.top_layout)
        self.main_v_layout.addLayout(self.middle_layout)

        self.ui.centralwidget.setLayout(self.main_v_layout)
        self.ui.setStyleSheet(
            'Demo{background: white} QPushButton{padding: 5px 10px; font:12px "Microsoft YaHei"}')

    # -------------------------组件功能实现-------------------------#
    # 任务进度环
    def service_progress_ring(self):
        #任务执行进度环
        self.progressRing = ProgressRing()
        self.progressRing.setValue(0)
        self.progressRing.setTextVisible(True)
        self.progressRing.setFixedSize(120, 120)
        self.middle_layout.addWidget(self.progressRing)

    # 下载发送功能
    def on_menu_action_triggered(self, action):
        if action.text() == "保存":
            self.task_save()
        if action.text() == "发送":
            self.task_send()

    def task_save(self):
        # 创建一个示例 DataFrame
        df = pd.DataFrame({
            '列1': [1, 2, 3],
            '列2': ['A', 'B', 'C']
        })
        # 打开文件对话框，让用户选择保存的位置
        file_dialog = QFileDialog(self.ui)
        file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        file_dialog.setNameFilter('Excel工作薄(*.xlsx)')
        file_dialog.setWindowTitle('保存文件')
        # 在 PyQt6 中，使用 AcceptMode 进行设置
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)

        if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            download_path = file_dialog.selectedFiles()[0]
            # 将 DataFrame 保存为 excel文件
            df.to_excel(download_path, index=False)
            Qinit_func.createInfoBar(self, '保存完毕', f'文件保存至：{download_path}')

    def task_send(self):
        w = CustomMessageBox(self.ui)
        if w.exec():
            print(w.urlLineEdit.text())


    # 上传7z附件功能
    def upload_file(self):
        file_dialog = QFileDialog(self.ui)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)  # 单个文件模式
        file_dialog.setNameFilter("文本文件 (*.txt)")  # 文件类型过滤器
        file_dialog.setViewMode(QFileDialog.ViewMode.List)  # 视图模式

        if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            file = file_dialog.selectedFiles()[0]
            Qinit_func.createInfoBar(self, '上传完毕:', f'{file}')

    # 执行程序功能
    @abstractmethod
    def task_exec(self):
        '''
        服务器验证登录信息
        子类必须实现该方法
        '''
        pass
        
    # 返回登录界面
    def return_login(self):
        self.ui.close()
        self.parent_ui.show()


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
    main_func = main_func(None, proc_path)
    sys.exit(app.exec())
