import sys
import os
import Qinit_func
from abc import abstractmethod
from PyQt6 import uic
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import QApplication, QFileDialog, QDialog, QProgressBar, QVBoxLayout, QLineEdit
from res import resource_rc

'''
界面登录模块基类
实现用户登录功能控件
'''
class login_func():
    def __init__(self, proc_path: str, logger=None):
        self.logger = logger
        self.proc_path = proc_path

        # 加载窗体UI
        self.ui = uic.loadUi(proc_path + os.sep + 'view/login_view.ui')
        # 设置窗口标志，仅保留标题栏，不显示最大化、最小化、关闭按钮，确保窗口总是位于其他窗口之上
        # self.ui.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.ui.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        # 设置固定窗口大小
        self.ui.setFixedSize(538, 332)
        # 设置窗口背景颜色为透明
        self.ui.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        # 将登录窗口屏幕居中
        Qinit_func.Center_the_window(self.ui)

        # 应用阴影效果到按钮
        self.ui.btn_cert.setGraphicsEffect(Qinit_func.shadow())
        self.ui.btn_login.setGraphicsEffect(Qinit_func.shadow())

        # 登录晃动功能
        self.shake_animation = Qinit_func.shake_window(self)

        # -------------------按键功能绑定方法---------------------#
        self.ui.btn_close.clicked.connect(self.closeEvent)
        self.ui.btn_login.clicked.connect(self.login_btn)
        self.ui.btn_cert.clicked.connect(self.open_cert)
        self.ui.btn_login_view.clicked.connect(self.switch_view)
        self.ui.btn_cfg_view.clicked.connect(self.switch_view)

        # 输入框功能(清空，密码显示隐藏)
        self.icon_show = QIcon()
        self.icon_show.addPixmap(
            QPixmap(":/icons/icons/密码显示.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.icon_hide = QIcon()
        self.icon_hide.addPixmap(
            QPixmap(":/icons/icons/密码隐藏.png"), QIcon.Mode.Normal, QIcon.State.Off)
        # self.ui.let_uname.focusInEvent = self.on_focus_in
        self.ui.btn_clear.clicked.connect(self.uname_clear)
        self.ui.btn_show.pressed.connect(self.on_button_pressed)
        self.ui.btn_show.released.connect(self.on_button_released)

        # 替换实例方法，使用 __get__ 方法绑定方法到实例
        # 界面拖动功能替换
        self.ui._start_position = None  # 记录鼠标拖动的起始位置
        self.ui.mousePressEvent = Qinit_func.mousePressEvent.__get__(self)
        self.ui.mouseMoveEvent = Qinit_func.mouseMoveEvent.__get__(self)
        self.ui.mouseReleaseEvent = Qinit_func.mouseReleaseEvent.__get__(self)
        # closeEvent功能替换
        self.ui.closeEvent = self.closeEvent.__get__(self.ui)

        # 显示登录窗口
        self.ui.show()

    # --------------------------登录验证晃动功能------------------------#
    def start_shaking(self):
        self.shake_animation.stop()
        self.shake_animation.setStartValue(self.ui.pos())
        self.shake_animation.setEndValue(
            QPoint(self.ui.pos().x() + 10, self.ui.pos().y()))
        self.shake_animation.start()

    def stop_shaking(self):
        self.shake_animation.stop()
        self.ui.move(self.ui.pos().x(), self.ui.pos().y())  # 确保回到原位置

    # --------------------------登录输入框功能---------------------------#
    def uname_clear(self):
        # 用户名置空
        self.ui.let_uname.clear()

    # 密码显示功能
    def on_button_pressed(self):
        # 鼠标按下
        self.ui.let_pwd.setEchoMode(QLineEdit.EchoMode.Normal)
        self.ui.btn_show.setIcon(self.icon_hide)

    def on_button_released(self):
        # 鼠标释放
        self.ui.let_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        self.ui.btn_show.setIcon(self.icon_show)

    def on_focus_in(self, event):
        # 处理 QLineEdit 获得焦点事件
        super(QLineEdit, self.ui.let_uname).focusInEvent(event)
        print("用户名登录框 进入编辑模式")

    # ---------------------------加载进度条------------------------#
    def service_progress(self):
        # 显示模态对话框
        self.dialog = QDialog(self.ui)
        self.dialog.setWindowTitle("登录验证中...")
        self.dialog.setModal(True)  # 设置为模态对话框
        # 去掉关闭按钮
        self.dialog.setWindowFlags(
            self.dialog.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)
        self.progress_bar = QProgressBar(self.dialog)
        self.progress_bar.setRange(0, 0)  # 不显示进度条，只是一个转圈的效果
        layout = QVBoxLayout()
        layout.addWidget(self.progress_bar)
        self.dialog.setLayout(layout)
        self.dialog.show()

    # --------------------------登录按钮功能----------------------------#
    def login_btn(self):
        '''
        实现登录按钮验证方法
        '''
        uname = self.ui.let_uname.text()
        pwd = self.ui.let_pwd.text()
        if uname == '' or pwd == '':
            self.ui.lab_info.setText('用户名或密码不能为空！')
            self.start_shaking()
        else:
            self.login_btn_verify()

    @abstractmethod
    def login_btn_verify(self):
        '''
        服务器验证登录信息
        子类必须实现该方法
        '''
        # self.ui.hide()
        # # 实例化窗体功能
        # self.main_func = main_func(self.ui,proc_path)

    # --------------------------数字证书按钮功能-------------------------#
    def open_cert(self):
        file_dialog = QFileDialog(self.ui)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)  # 单个文件模式
        file_dialog.setNameFilter("证书文件(*.cer)")  # 文件类型过滤器
        file_dialog.setViewMode(QFileDialog.ViewMode.List)  # 视图模式

        if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            file = file_dialog.selectedFiles()[0]
            self.ui.lab_cert.setText(file)

    # --------------------------登录配置视图切换功能----------------------#
    def switch_view(self):
        '''
        实现登录配置视图切换
        '''
        sender = QApplication.instance().sender()
        if sender.text() == '登录':
            self.ui.widget_login.show()
            self.ui.widget_login.raise_()
            self.ui.widget_cfg.hide()
        if sender.text() == '配置':
            self.ui.widget_cfg.show()
            self.ui.widget_cfg.raise_()
            self.ui.widget_login.hide()

    # --------------------------关闭按钮功能----------------------------#
    def closeEvent(self, event):
        # 关闭实现减隐藏功能
        Qinit_func.fadeOut(self, self.ui.close)


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
    login_func = login_func(proc_path)
    sys.exit(app.exec())
