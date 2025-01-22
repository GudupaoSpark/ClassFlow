import json
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QWidget, 
                             QLabel, QVBoxLayout, QHBoxLayout, QFrame, QMessageBox)
from PySide6.QtCore import Qt, QRect, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QColor, QIcon
import sys
import requests
from datetime import datetime

class SubjectButton(QPushButton):
    def __init__(self, subject_data, parent=None):
        text = subject_data['name']
        super().__init__(text, parent)
        self.setFixedHeight(50)  # 进一步增加按钮高度
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: #F1C40F;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 5px 15px;
                text-align: center;
                margin: 8px 5px;  /* 增加上下间距 */
                font-size: 16px;  /* 增加字体大小 */
                font-weight: bold;
                letter-spacing: 2px;
            }
            QPushButton:hover {
                background-color: #F4D03F;
            }
        """)

    def set_current(self, is_current):
        """设置当前课程高亮"""
        if is_current:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #E67E22;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 5px 15px;
                    text-align: center;
                    margin: 8px 5px;  /* 增加上下间距 */
                    font-size: 16px;  /* 增加字体大小 */
                    font-weight: bold;
                    letter-spacing: 2px;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #F1C40F;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 5px 15px;
                    text-align: center;
                    margin: 8px 5px;  /* 增加上下间距 */
                    font-size: 16px;  /* 增加字体大小 */
                    font-weight: bold;
                    letter-spacing: 2px;
                }
                QPushButton:hover {
                    background-color: #F4D03F;
                }
            """)

class TimeSlotFrame(QFrame):
    def __init__(self, time_text, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(5)  # 增加框架内部间距
        
        # 简化时间标签
        time_label = QLabel(time_text)
        time_label.setStyleSheet("""
            QLabel {
                color: #3498DB;
                font-size: 13px;  /* 增加时间标签字体大小 */
                padding: 2px 8px;
                font-weight: bold;
                background: white;
                border-radius: 4px;
            }
        """)
        layout.addWidget(time_label)

class SidePanelApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.panel_width_expanded = 280  # 稍微缩小面板宽度
        self.button_width = 30
        self.button_height = 40
        self.panel_height = 600
        self.y_position = 100
        self.is_expanded = False
        self.json_path = os.path.join(os.path.dirname(__file__), 'schedule.json')

        # 设置主窗口，初始只显示按钮大小
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(
            screen.width() - self.button_width,
            self.y_position,
            self.button_width,
            self.button_height  # 改为只显示按钮高度
        )
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint | 
            Qt.MSWindowsFixedSizeDialogHint  # 添加固定大小标志
        )
        
        # 禁止调整大小
        self.setFixedSize(self.button_width, self.button_height)

        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
                border-radius: 20px;
            }
        """)

        # 主面板样式优化
        self.panel = QWidget(self)
        self.panel.setObjectName("mainPanel")
        layout = QVBoxLayout(self.panel)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)  # 增加时间段之间的间距
        self.panel.setLayout(layout)  # 确保设置布局

        # 标题区域
        title = QLabel("课程表")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            color: #2C3E50;
            font-size: 16px;  /* 增加标题字体大小 */
            font-weight: bold;
            padding: 8px;
            margin-bottom: 5px;
            background-color: white;
            border-bottom: 1px solid #E0E0E0;
        """)
        layout.addWidget(title)

        # 在创建时间段之前先设置面板大小
        self.panel.setFixedSize(self.panel_width_expanded, self.panel_height)
        
        # 读取课表数据
        self.schedule_data = self.load_schedule()
        if not self.schedule_data:
            QMessageBox.warning(self, "错误", "无法加载课表数据，使用默认数据")
            self.schedule_data = self.get_default_schedule()
        
        # 创建时间段和课程
        for time_slot, subjects in self.schedule_data.items():
            time_frame = TimeSlotFrame(time_slot, self.panel)
            time_frame.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-radius: 8px;
                    margin: 2px 5px;
                    padding: 5px;
                    border: 1px solid #F0F0F0;
                }
            """)
            
            # 使用JSON数据创建课程按钮
            for subject in subjects:
                btn = SubjectButton(subject, time_frame)
                time_frame.layout().addWidget(btn)
            
            layout.addWidget(time_frame)

        layout.addStretch()

        self.panel.setStyleSheet("""
            QWidget#mainPanel {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #E0E0E0;
            }
        """)
        self.panel.hide()  # 初始时隐藏面板

        # 收缩按钮样式
        self.toggle_button = QPushButton(">>", self)
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        self.toggle_button.clicked.connect(self.toggle_panel)
        self.update_button_position()

    def toggle_panel(self):
        screen = QApplication.primaryScreen().geometry()
        if self.is_expanded:
            # 收缩时
            new_x = screen.width() - self.button_width
            new_width = self.button_width
            new_height = self.button_height
            self.setFixedSize(new_width, new_height)
            self.toggle_button.setText(">>")
        else:
            # 展开时
            new_x = screen.width() - self.panel_width_expanded
            new_width = self.panel_width_expanded
            new_height = self.panel_height
            self.setFixedSize(new_width, new_height)
            self.toggle_button.setText("<<")
            self.panel.show()  # 确保面板显示

        # 动画
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(200)
        self.anim.setEndValue(QRect(new_x, self.y_position, new_width, new_height))
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        
        if self.is_expanded:
            self.anim.finished.connect(lambda: self.panel.hide())
        
        self.anim.start()
        self.is_expanded = not self.is_expanded
        self.update_button_position()

    def update_button_position(self):
        # 按钮永远保持相同大小和位置
        self.toggle_button.setGeometry(
            0,
            0,
            self.button_width,
            self.button_height
        )

    def load_schedule(self):
        """从服务器加载课表数据并保存到本地"""
        try:
            # 尝试从服务器获取数据
            response = requests.get('http://{server_ip}/api/schedule')
            if response.status_code == 200:
                schedule_data = response.json()
                # 保存到本地 JSON 文件
                self.save_schedule_to_json(schedule_data)
                return schedule_data
            else:
                print(f"服务器错误: {response.status_code}")
                # 尝试从本地 JSON 读取
                return self.load_schedule_from_json()
        except Exception as e:
            print(f"网络请求错误: {e}")
            return self.load_schedule_from_json()

    def save_schedule_to_json(self, data):
        """保存课表数据到 JSON 文件"""
        try:
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print("课表数据已保存到本地")
        except Exception as e:
            print(f"保存 JSON 文件错误: {e}")

    def load_schedule_from_json(self):
        """从本地 JSON 文件加载课表"""
        try:
            if os.path.exists(self.json_path):
                with open(self.json_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"读取 JSON 文件错误: {e}")
        return self.get_default_schedule()

    def get_default_schedule(self):
        """返回默认课表数据"""
        return {
            "上午": [
                {
                    "name": "未知课程"
                }
            ]
        }

    def refresh_schedule(self):
        """刷新课表数据"""
        new_data = self.load_schedule()
        if (new_data):
            self.schedule_data = new_data
            self.update_ui_with_schedule()
            return True
        return False

    def update_ui_with_schedule(self):
        """更新界面显示的课表"""
        # 清除现有课表
        for i in reversed(range(self.panel.layout().count()-1)):  # 保留标题
            widget = self.panel.layout().itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # 重新创建课表UI
        current_time = datetime.now().strftime("%H:%M")
        
        for time_slot, subjects in self.schedule_data.items():
            time_frame = TimeSlotFrame(time_slot, self.panel)
            time_frame.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-radius: 8px;
                    margin: 2px 5px;
                    padding: 5px;
                    border: 1px solid #F0F0F0;
                }
            """)

            for subject in subjects:
                btn = SubjectButton(subject, time_frame)
                # 简单检查是否为当前时段
                btn.set_current(time_slot == self.get_current_time_slot())
                time_frame.layout().addWidget(btn)
            
            self.panel.layout().addWidget(time_frame)
        
        self.panel.layout().addStretch()

    def get_current_time_slot(self):
        """获取当前时间段"""
        hour = datetime.now().hour
        if 6 <= hour < 12:
            return "上午"
        elif 12 <= hour < 18:
            return "下午"
        else:
            return "晚自习"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SidePanelApp()
    window.show()
    sys.exit(app.exec())
