import tkinter as tk
import math

# 创建主窗口
root = tk.Tk()
root.title("课表列表")
root.geometry("400x600+1890+200")  # 调整窗口位置到可视区域，屏幕1080p的贴边，这里可以自行调整
root.overrideredirect(True)  # 隐藏窗口标题栏
root.attributes('-topmost', True)  # 窗口置顶

# 定义状态
hidden = True
animation_running = False

def animate_slide(show):
    """窗口滑动动画"""
    global animation_running
    if animation_running:
        return  # 如果动画正在运行，禁止重复点击

    animation_running = True
    start_x = root.winfo_x()
    target_x = 1500 if show else 1920

    steps = 50
    delta_x = (target_x - start_x) / steps

    def ease_in_out(t):
        """缓动函数"""
        return -0.4 * (math.cos(math.pi * t) - 1)

    def slide(step=0):
        nonlocal start_x
        if step > steps:
            root.geometry(f"400x600+{target_x}+100")
            global hidden
            hidden = not show
            animation_running = False
            return

        progress = ease_in_out(step / steps)
        current_x = start_x + progress * (target_x - start_x)
        root.geometry(f"400x600+{int(current_x)}+100")
        root.after(30, slide, step + 1)

    slide()

# 创建自定义边框和圆角背景
background_canvas = tk.Canvas(root, width=400, height=600, bg="#f9d342", highlightthickness=0)
background_canvas.place(x=0, y=0)

# 绘制圆角外边框
def draw_rounded_rectangle(canvas, x1, y1, x2, y2, radius, **kwargs):
    canvas.create_arc(x1, y1, x1 + 2 * radius, y1 + 2 * radius, start=90, extent=90, **kwargs)
    canvas.create_arc(x2 - 2 * radius, y1, x2, y1 + 2 * radius, start=0, extent=90, **kwargs)
    canvas.create_arc(x1, y2 - 2 * radius, x1 + 2 * radius, y2, start=180, extent=90, **kwargs)
    canvas.create_arc(x2 - 2 * radius, y2 - 2 * radius, x2, y2, start=270, extent=90, **kwargs)
    canvas.create_rectangle(x1 + radius, y1, x2 - radius, y2, **kwargs)
    canvas.create_rectangle(x1, y1 + radius, x2, y2 - radius, **kwargs)

draw_rounded_rectangle(background_canvas, 5, 5, 400 - 5, 600 - 5, radius=22, fill="#f9d342", outline="black")

# 创建交互按钮
button_radius = 50
button_canvas = tk.Canvas(root, width=2 * button_radius, height=2 * button_radius, bg="#f9d342", highlightthickness=10)
button_canvas.place(x=-30, y=250)

# 绘制箭头按钮
def draw_rounded_arrow(canvas, x, y, radius, direction):
    arrow_color = "black"
    canvas.create_oval(x, y, x + 2 * radius, y + 2 * radius, fill="#f9d342", outline="black")
    offset = 10
    if direction == "left":
        canvas.create_polygon(
            x + radius + offset, y + radius - offset,
            x + radius - offset, y + radius,
            x + radius + offset, y + radius + offset,
            fill=arrow_color, outline=arrow_color
        )
    elif direction == "right":
        canvas.create_polygon(
            x + radius - offset, y + radius - offset,
            x + radius + offset, y + radius,
            x + radius - offset, y + radius + offset,
            fill=arrow_color, outline=arrow_color
        )

arrow_direction = "left"
draw_rounded_arrow(button_canvas, 0, 0, button_radius, arrow_direction)
# 添加课表内容
frame = tk.Frame(root, bg="#f9d342")
frame.place(x=20, y=20, width=360, height=550)

# 课表数据（示例）
schedule = [
    "8:00 - 9:00  数学",
    "9:10 - 10:10 英语",
    "10:20 - 11:20 物理",
    "11:30 - 12:30 化学",
    "14:00 - 15:00 生物",
    "15:10 - 16:10 历史",
    "16:20 - 17:20 地理",
]

# 创建每一行课表项
for i, item in enumerate(schedule):
    row = tk.Frame(frame, bg="#f9d342")
    row.pack(fill="x", pady=(0, 1))  # 每行之间有一条黑线

    label = tk.Label(row, text=item, bg="#f9d342", font=("Arial", 14), anchor="w")
    label.pack(fill="x", padx=10, pady=5)

    # 添加底部黑线
    if i < len(schedule) :  # 最后一行不需要黑线
        tk.Frame(row, height=1, bg="black").pack(fill="x", pady=0)

# 按钮点击事件
def toggle_window(event):
    global arrow_direction, hidden
    if animation_running:
        return  # 如果动画正在运行，禁止重复点击

    animate_slide(hidden)  # 执行动画
    button_canvas.delete("all")
    arrow_direction = "right" if hidden else "left"
    draw_rounded_arrow(button_canvas, 0, 0, button_radius, arrow_direction)
    hidden = not hidden  # 更新隐藏状态

button_canvas.bind("<Button-1>", toggle_window)

# 启动主循环
root.mainloop()
