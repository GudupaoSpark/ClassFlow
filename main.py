import tkinter as tk


class SidePanelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("侧边栏")
        screen_width = self.root.winfo_screenwidth()  # 获取屏幕宽度
        self.panel_width_expanded = 300  # 展开宽度
        self.panel_width_collapsed = 50  # 收缩宽度
        self.panel_height = 600  # 面板高度
        self.y_position = 100  # 垂直位置
        self.is_expanded = False  # 初始状态为收缩

        # 初始化窗口位置到屏幕右侧边缘
        self.root.geometry(
            f"{self.panel_width_collapsed}x{self.panel_height}+{screen_width - self.panel_width_collapsed}+{self.y_position}"
        )
        self.root.overrideredirect(True)  # 去掉窗口装饰
        self.root.resizable(False, False)

        # 主面板
        self.panel = tk.Frame(self.root, bg="white", borderwidth=2, relief="solid")
        # 收缩时完全隐藏面板内容
        self.panel.place_forget()

        # 缩放按钮（独立于主面板）
        self.toggle_button = tk.Button(
            self.root,
            text=">>",
            font=("Arial", 12, "bold"),
            bg="yellow",
            command=self.toggle_panel,
        )
        self.update_button_position()

        # 科目标签
        self.subject_labels = []
        subjects = ["语文", "数学", "英语"]
        for i, subject in enumerate(subjects):
            label = tk.Label(
                self.panel,
                text=subject,
                font=("Arial", 16, "bold"),
                bg="white",
                fg="black",
            )
            self.subject_labels.append(label)

        # 添加水平分割线
        self.lines = []
        for i in range(len(subjects) + 1):
            line = tk.Frame(self.panel, bg="black", height=2)
            self.lines.append(line)

    def toggle_panel(self):
        """实现面板的伸缩功能"""
        screen_width = self.root.winfo_screenwidth()
        if self.is_expanded:
            # 收缩到右侧
            self.root.geometry(
                f"{self.panel_width_collapsed}x{self.panel_height}+{screen_width - self.panel_width_collapsed}+{self.y_position}"
            )
            self.toggle_button.config(text=">>")
            self.panel.place_forget()  # 隐藏主面板
        else:
            # 展开面板
            self.root.geometry(
                f"{self.panel_width_expanded}x{self.panel_height}+{screen_width - self.panel_width_expanded}+{self.y_position}"
            )
            self.toggle_button.config(text="<<")
            self.panel.place(x=0, y=0, width=self.panel_width_expanded, height=self.panel_height)  # 显示主面板

            # 重新显示标签和分割线
            for i, label in enumerate(self.subject_labels):
                label.place(x=20, y=50 + i * 100)
            for i, line in enumerate(self.lines):
                line.place(x=10, y=90 + i * 100, width=260)

        self.is_expanded = not self.is_expanded
        self.update_button_position()

    def update_button_position(self):
        """更新按钮位置，使其始终贴在窗口右侧边缘"""
        if self.is_expanded:
            # 按钮贴在面板右侧
            self.toggle_button.place(
                x=self.panel_width_expanded - 40,
                y=10,
                width=30,
                height=40,
            )
        else:
            # 按钮贴在屏幕右侧边缘
            self.toggle_button.place(
                x=10,
                y=10,
                width=30,
                height=40,
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = SidePanelApp(root)
    root.mainloop()
