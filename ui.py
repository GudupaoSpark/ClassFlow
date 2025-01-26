from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QWidget,
                             QLabel, QVBoxLayout, QHBoxLayout, QFrame, QMessageBox)
from PySide6.QtCore import Qt, QRect, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QColor, QIcon
from datetime import datetime


class SubjectButton(QPushButton):
    def __init__(self, subject_data, parent=None):
        super().__init__(subject_data['name'], parent)
        self.setFixedHeight(50)
        self.setCursor(Qt.ArrowCursor)
        self.setEnabled(False)
        self._init_style()

    def _init_style(self):
        self.setStyleSheet("""
            QPushButton {
                background-color: #F1C40F;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 5px 15px;
                text-align: center;
                margin: 8px 5px;
                font-size: 16px;
                font-weight: bold;
                letter-spacing: 2px;
            }
            QPushButton:disabled {
                background-color: #F1C40F;
                color: white;
            }
        """)

    def set_current(self, is_current):
        self.setStyleSheet("""
            QPushButton {
                background-color: """ + ('#E67E22' if is_current else '#F1C40F') + """;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 5px 15px;
                text-align: center;
                margin: 8px 5px;
                font-size: 16px;
                font-weight: bold;
                letter-spacing: 2px;
            }
            QPushButton:hover {
                background-color: """ + ('#F5A563' if is_current else '#F4D03F') + """;
            }
        """)


class TimeSlotFrame(QFrame):
    def __init__(self, time_text, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(5)

        time_label = QLabel(time_text)
        time_label.setStyleSheet("""
            QLabel {
                color: #3498DB;
                font-size: 13px;
                padding: 2px 8px;
                font-weight: bold;
                background: white;
                border-radius: 4px;
            }
        """)
        layout.addWidget(time_label)


class SidePanelApp(QMainWindow):
    def __init__(self, link, schedule_data):
        super().__init__()
        self.link = link
        self.schedule_data = schedule_data
        self.panel_width_expanded = 280
        self.button_width = 30
        self.button_height = 40
        self.panel_height = 600
        self.y_position = 100
        self.is_expanded = False

        self._init_ui()
        self.update_ui_with_schedule()


    def _init_ui(self):
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(
            screen.width() - self.button_width,
            self.y_position,
            self.button_width,
            self.button_height
        )
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.MSWindowsFixedSizeDialogHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setFixedSize(self.button_width, self.button_height)

        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
                border-radius: 25px;
                border: 2px solid #3498DB;
                padding: 1px;
            }

            QMainWindow::separator {
                background: transparent;
            }
        """)

        self.panel = QWidget(self)
        self.panel.setObjectName("mainPanel")
        layout = QVBoxLayout(self.panel)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        self.panel.setLayout(layout)

        title = QLabel("课程表")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            color: #2C3E50;
            font-size: 16px;
            font-weight: bold;
            padding: 8px;
            margin-bottom: 5px;
            background-color: white;
            border-bottom: 1px solid #E0E0E0;
        """)
        layout.addWidget(title)

        self.panel.setFixedSize(self.panel_width_expanded, self.panel_height)

        self.panel.setStyleSheet("""
            QWidget#mainPanel {
                background-color: white;
                border-radius: 5px;
                border: 1px solid #E0E0E0;
            }
        """)
        self.panel.hide()

        self.toggle_button = QPushButton("<<", self)
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
            new_x = screen.width() - self.button_width
            new_width = self.button_width
            new_height = self.button_height
            self.setFixedSize(new_width, new_height)
            self.toggle_button.setText("<<")
        else:
            new_x = screen.width() - self.panel_width_expanded
            new_width = self.panel_width_expanded
            new_height = self.panel_height
            self.setFixedSize(new_width, new_height)
            self.toggle_button.setText(">>")
            self.panel.show()

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
        self.toggle_button.setGeometry(
            0,
            0,
            self.button_width,
            self.button_height
        )


    def refresh_schedule(self):
        new_data = self.link.load_schedule()
        if (new_data):
            self.schedule_data = new_data
            self.update_ui_with_schedule()
            return True
        return False

    def update_ui_with_schedule(self):
        for i in reversed(range(self.panel.layout().count()-1)):
            widget = self.panel.layout().itemAt(i).widget()
            if widget:
                widget.deleteLater()

        current_time = datetime.now().strftime("%H:%M")

        for time_slot, subjects in self.schedule_data.items():
            time_frame = TimeSlotFrame(time_slot, self.panel)
            time_frame.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-radius: 15px;
                    margin: 2px 5px;
                    padding: 5px;
                    border: 1px solid #F0F0F0;
                }
            """)

            for subject in subjects:
                btn = SubjectButton(subject, time_frame)
                btn.set_current(time_slot == self.get_current_time_slot())
                time_frame.layout().addWidget(btn)

            self.panel.layout().addWidget(time_frame)

        self.panel.layout().addStretch()

    def get_current_time_slot(self):
        hour = datetime.now().hour
        if 6 <= hour < 12:
            return "上午"
        elif 12 <= hour < 18:
            return "下午"
        else:
            return "晚自习"