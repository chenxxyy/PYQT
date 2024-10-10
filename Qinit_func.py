import os
import sys
import traceback
import logging
from datetime import datetime
from random import randint
from PyQt6.QtGui import QGuiApplication,QColor
from PyQt6.QtWidgets import QWidget,QMessageBox,QGraphicsDropShadowEffect,QPushButton
from PyQt6.QtCore import Qt,QPropertyAnimation,QRect,QEasingCurve
from qfluentwidgets import InfoBar, InfoBarPosition

# 遇到系统错误不崩溃通过错误弹框处理
def error_handler(exc_type, exc_value, exc_tb):
    error_message = "".join(
        traceback.format_exception(exc_type, exc_value, exc_tb))
    print(error_message)
    reply = QMessageBox.critical(
        None, '错误信息:', error_message,
        QMessageBox.StandardButton.Abort | QMessageBox.StandardButton.Retry,
        QMessageBox.StandardButton.Abort)
    if reply == QMessageBox.StandardButton.Abort:
        sys.exit(1)

# 资源文件目录访问(打包exe时资源文件的路径判断)
def source_path() -> str:
    # 是否Bundle Resource
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return base_path

# 程序日志记录
def logger_record():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - [%(filename)s][line:%(lineno)d][%(levelname)s]  %(message)s')

    # 日志文件保存到本地
    log_file_name = os.path.join(os.path.dirname(__file__), 'Log_Folder', 'log_{time}_{randomn}'.format(
        time=datetime.now().strftime('%Y_%m%d_%H%M%S'), randomn=randint(0, 9)))
    os.makedirs(os.path.dirname(log_file_name), exist_ok=True)
    file_handler = logging.FileHandler(log_file_name)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

# 创建阴影效果
def shadow():
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(20)  # 阴影模糊半径
    shadow.setOffset(5, 5)  # 阴影偏移量
    shadow.setColor(QColor(0, 0, 0, 160))  # 阴影颜色（黑色，透明度 160）
    return shadow

# 将窗口屏幕居中
def Center_the_window(ui):
    qr = ui.frameGeometry()
    cp = QGuiApplication.primaryScreen().availableGeometry().center()
    qr.moveCenter(cp)
    ui.move(qr.topLeft())

# 晃动功能
def shake_window(self):
    shake_animation = QPropertyAnimation(self.ui, b"pos")
    shake_animation.setDuration(100)  # 动画时长
    shake_animation.setLoopCount(3)  # 重复5次
    shake_animation.setEasingCurve(QEasingCurve.Type.OutBounce)
    return shake_animation

# -----------------------鼠标拖动功能实现--------------------#
def mousePressEvent(self, event):
    if event.button() == Qt.MouseButton.LeftButton:
        # 记录鼠标点击的初始位置
        self.ui._start_position = event.globalPosition().toPoint()

def mouseMoveEvent(self, event):
    if self.ui._start_position:
        # 计算窗口的新位置
        current_position = event.globalPosition().toPoint()
        delta = current_position - self.ui._start_position
        self.ui.move(self.ui.pos() + delta)
        # 更新起始位置
        self.ui._start_position = current_position

def mouseReleaseEvent(self, event):
    if event.button() == Qt.MouseButton.LeftButton:
        # 释放鼠标后，重置起始位置
        self.ui._start_position = None

# -----------------------消息展示窗口------------------------#
def createInfoBar(self,title, content):
    # convenient class mothod
    InfoBar.success(
        title=title,
        content=content,
        orient=Qt.Orientation.Horizontal,
        isClosable=True,
        position=InfoBarPosition.BOTTOM,
        # position='Custom',   # NOTE: use custom info bar manager
        duration=3000,
        parent=self.ui
    )

def createWarningInfoBar(self, title, content):
    InfoBar.warning(
        title=title,
        content=content,
        orient=Qt.Orientation.Horizontal,
        isClosable=False,   # disable close button
        position=InfoBarPosition.TOP_LEFT,
        duration=2000,
        parent=self.ui
    )

def createErrorInfoBar(self, title, content):
    InfoBar.error(
        title=title,
        content=content,
        orient=Qt.Orientation.Horizontal,
        isClosable=True,
        position=InfoBarPosition.BOTTOM_RIGHT,
        duration=-1,    # won't disappear automatically
        parent=self.ui
    )

# -----------------------遍历所有控件，启用,禁用按钮---------------#
def disable_all_buttons(widget):
    set_all_buttons_enabled(widget,False)

def enable_all_buttons(widget):
    set_all_buttons_enabled(widget,True)

def set_all_buttons_enabled(widget,enabled):
    def set_enabled_recursively(widget, enabled):
        if isinstance(widget, QPushButton):
            widget.setEnabled(enabled)
        for child in widget.findChildren(QWidget):
            set_enabled_recursively(child, enabled)
    set_enabled_recursively(widget,enabled)

# ------------------------渐显渐隐功能----------------------------#
def fadeIn(self, event = None):
    self.ui.animation = QPropertyAnimation(self.ui, b"windowOpacity")
    self.ui.animation.setStartValue(0.0)
    self.ui.animation.setEndValue(1.0)
    self.ui.animation.setDuration(1000)
    self.ui.animation.start()

def fadeOut(self, event = None):
    self.ui.animation = QPropertyAnimation(self.ui, b"windowOpacity")
    self.ui.animation.setStartValue(1.0)
    self.ui.animation.setEndValue(0.0)
    self.ui.animation.setDuration(1000)
    self.ui.animation.finished.connect(event)
    self.ui.animation.start()

# ------------------------变大变小功能-----------------------------#
def scaleIn(self, event =None):
    cp = QGuiApplication.primaryScreen().availableGeometry().center()
    qr = center()
    self.ui.animation = QPropertyAnimation(self.ui, b"geometry")
    self.ui.animation.setStartValue(QRect(cp.x(), cp.y(), 0, 0))
    self.ui.animation.setEndValue(qr)
    self.ui.animation.setDuration(3000)
    self.ui.animation.setEasingCurve(QEasingCurve.Type.Linear)
    # self.ui.animation.setEasingCurve(QEasingCurve.Type.OutQuint)
    # self.ui.animation.setEasingCurve(QEasingCurve.Type.OutBack)
    # self.ui.animation.setEasingCurve(QEasingCurve.Type.OutElastic)
    self.ui.animation.finished.connect(event)
    self.ui.animation.start()

def center():
    qr = QRect(0, 0, 500, 500)
    cp = QGuiApplication.primaryScreen().availableGeometry().center()
    qr.moveCenter(cp)
    return qr