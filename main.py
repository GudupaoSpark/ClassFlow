import json
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QWidget, 
                             QLabel, QVBoxLayout, QHBoxLayout, QFrame, QMessageBox)
from PySide6.QtCore import Qt, QRect, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QColor, QIcon
import sys
import requests

class SubjectButton(QPushButton):
    def __init__(self, subject_data, parent=None):
        # 修改按鈕初始化，接收完整的科目數據
        text = f"{subject_data['icon']} {subject_data['name']} {subject_data['time']}"
        super().__init__(text, parent)
        self.setFixedHeight(50)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: #2C3E50;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px;
                text-align: left;
                margin: 5px 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #34495E;
                border-left: 4px solid #3498DB;
            }
        """)

class TimeSlotFrame(QFrame):
    def __init__(self, time_text, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)
        
        # 時間標籤
        time_label = QLabel(time_text)
        time_label.setStyleSheet("""
            QLabel {
                color: #3498DB;
                font-size: 12px;
                padding: 2px 5px;
                background: #1a2633;
                border-radius: 5px;
            }
        """)
        layout.addWidget(time_label)

class SidePanelApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.panel_width_expanded = 280  # 稍微縮小面板寬度
        self.button_width = 30
        self.button_height = 40
        self.panel_height = 600
        self.y_position = 100
        self.is_expanded = False
        self.json_path = os.path.join(os.path.dirname(__file__), 'schedule.json')

        # 設置主視窗，初始只顯示按鈕大小
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(
            screen.width() - self.button_width,
            self.y_position,
            self.button_width,
            self.button_height  # 改為只顯示按鈕高度
        )
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        # 設置窗口樣式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2C3E50;
                border-radius: 20px;
            }
        """)

        # 主面板樣式優化
        self.panel = QWidget(self)
        self.panel.setObjectName("mainPanel")
        layout = QVBoxLayout(self.panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        self.panel.setLayout(layout)  # 確保設置佈局

        # 標題區域
        title = QLabel("課程表")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: bold;
            padding: 12px;
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #3498DB, stop:1 #2980B9);
            border-radius: 15px;
            margin: 0 10px 10px 10px;
        """)
        layout.addWidget(title)

        # 在創建時間段之前先設置面板大小
        self.panel.setFixedSize(self.panel_width_expanded, self.panel_height)
        
        # 讀取課表數據
        self.schedule_data = self.load_schedule()
        if not self.schedule_data:
            QMessageBox.warning(self, "錯誤", "無法加載課表數據，使用默認數據")
            self.schedule_data = self.get_default_schedule()
        
        # 創建時間段和課程
        for time_slot, subjects in self.schedule_data.items():
            time_frame = TimeSlotFrame(time_slot, self.panel)
            time_frame.setStyleSheet("""
                QFrame {
                    background-color: #2C3E50;
                    border-radius: 15px;
                    margin: 5px 10px;
                    padding: 8px;
                    border: 1px solid #3498DB;
                }
            """)
            
            # 使用JSON數據創建課程按鈕
            for subject in subjects:
                btn = SubjectButton(subject, time_frame)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                            stop:0 {subject['color']}, stop:1 {subject['color']}DD);
                        color: white;
                        border: none;
                        border-radius: 12px;
                        padding: 8px;
                        text-align: left;
                        margin: 3px 5px;
                        font-size: 14px;
                    }}
                    QPushButton:hover {{
                        background-color: {subject['color']};
                        border: 2px solid white;
                    }}
                """)
                time_frame.layout().addWidget(btn)
            
            layout.addWidget(time_frame)

        layout.addStretch()

        self.panel.setStyleSheet("""
            QWidget#mainPanel {
                background-color: #1a2633;
                border-radius: 20px;
                border: 2px solid qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #3498DB, stop:1 #2980B9);
            }
        """)
        self.panel.hide()  # 初始時隱藏面板

        # 收縮按鈕樣式
        self.toggle_button = QPushButton(">>", self)
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #3498DB, stop:1 #2980B9);
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2980B9, stop:1 #2475A9);
                border: 2px solid #2ecc71;
            }
        """)
        self.toggle_button.clicked.connect(self.toggle_panel)
        self.update_button_position()

    def toggle_panel(self):
        screen = QApplication.primaryScreen().geometry()
        if self.is_expanded:
            # 收縮時
            new_x = screen.width() - self.button_width
            new_width = self.button_width
            new_height = self.button_height
            self.toggle_button.setText(">>")
        else:
            # 展開時
            new_x = screen.width() - self.panel_width_expanded
            new_width = self.panel_width_expanded
            new_height = self.panel_height
            self.toggle_button.setText("<<")
            self.panel.show()  # 確保面板顯示

        # 動畫
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
        # 按鈕永遠保持相同大小和位置
        self.toggle_button.setGeometry(
            0,
            0,
            self.button_width,
            self.button_height
        )

    def load_schedule(self):
        """從服務器加載課表數據並保存到本地"""
        try:
            # 嘗試從服務器獲取數據
            response = requests.get('http://your-server-url/api/schedule')
            if response.status_code == 200:
                schedule_data = response.json()
                # 保存到本地 JSON 文件
                self.save_schedule_to_json(schedule_data)
                return schedule_data
            else:
                print(f"服務器錯誤: {response.status_code}")
                # 嘗試從本地 JSON 讀取
                return self.load_schedule_from_json()
        except Exception as e:
            print(f"網絡請求錯誤: {e}")
            return self.load_schedule_from_json()

    def save_schedule_to_json(self, data):
        """保存課表數據到 JSON 文件"""
        try:
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print("課表數據已保存到本地")
        except Exception as e:
            print(f"保存 JSON 文件錯誤: {e}")

    def load_schedule_from_json(self):
        """從本地 JSON 文件加載課表"""
        try:
            if os.path.exists(self.json_path):
                with open(self.json_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"讀取 JSON 文件錯誤: {e}")
        return self.get_default_schedule()

    def get_default_schedule(self):
        """返回默認課表數據"""
        return {
            "上午": [
                {
                    "name": "未知課程",
                    "icon": "❓",
                    "color": "#95A5A6",
                    "time": "00:00-00:00"
                }
            ]
        }

    def refresh_schedule(self):
        """刷新課表數據"""
        new_data = self.load_schedule()
        if new_data:
            self.schedule_data = new_data
            self.update_ui_with_schedule()
            return True
        return False

    def update_ui_with_schedule(self):
        """更新界面顯示的課表"""
        # 清除現有課表
        for i in reversed(range(self.panel.layout().count()-1)):  # 保留標題
            widget = self.panel.layout().itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # 重新創建課表UI
        for time_slot, subjects in self.schedule_data.items():
            time_frame = TimeSlotFrame(time_slot, self.panel)
            time_frame.setStyleSheet("""
                QFrame {
                    background-color: #2C3E50;
                    border-radius: 15px;
                    margin: 5px 10px;
                    padding: 8px;
                    border: 1px solid #3498DB;
                }
            """)

            for subject in subjects:
                btn = SubjectButton(subject, time_frame)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                            stop:0 {subject['color']}, stop:1 {subject['color']}DD);
                        color: white;
                        border: none;
                        border-radius: 12px;
                        padding: 8px;
                        text-align: left;
                        margin: 3px 5px;
                        font-size: 14px;
                    }}
                    QPushButton:hover {{
                        background-color: {subject['color']};
                        border: 2px solid white;
                    }}
                """)
                time_frame.layout().addWidget(btn)
            
            self.panel.layout().addWidget(time_frame)
        
        self.panel.layout().addStretch()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SidePanelApp()
    window.show()
    sys.exit(app.exec())
