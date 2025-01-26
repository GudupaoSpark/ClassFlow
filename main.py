import sys
import os
import subprocess
import ctypes
from PySide6.QtWidgets import QApplication
from ui import SidePanelApp
from link import Link
from datetime import datetime
import json
import pathlib


python_exe = os.path.abspath(sys.executable.replace('python.exe', 'python.exe'))


def ch_dir(*p):
    if len(p) == 0:
        p=(os.path.dirname(sys.executable),os.path.dirname(os.path.abspath(__file__)))
    for i in p:
        print(os.path.join(i,"data"))
        if os.path.isdir(os.path.join(i,"data")):
            return i
    return "."

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def create_startup_task():
    # 获取绝对路径
    script_path = os.path.abspath(__file__)
    
    
    task_name = "ClassFlowAutoStart"
    task_command = f'schtasks /create /tn "{task_name}" /tr "\"{python_exe}\" \"{script_path}\"" /sc onlogon /rl highest'
    
    try:
        subprocess.run(task_command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"创建任务计划失败: {e}")
        return False

def check_startup_task():
    task_name = "ClassFlowAutoStart"
    check_command = f'schtasks /query /tn "{task_name}"'
    
    try:
        subprocess.run(check_command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def get_default_schedule():
    return {
        "上午": [
            {
                "name": "未知课程"
            }
        ]
    }

def load_schedule_from_json(json_path):
    try:
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"读取 JSON 文件错误: {e}")
    return get_default_schedule()


if __name__ == "__main__":
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", python_exe, __file__, None, 1)
        sys.exit()
    
    if not check_startup_task():
        if create_startup_task():
            print("已成功创建开机启动任务")
        else:
            print("创建开机启动任务失败")
    
    app = QApplication(sys.argv)

    server_config_path = os.path.join(ch_dir(),'data', 'server_config.json')
    json_path = os.path.join(ch_dir(), 'data', 'schedule.json')
    print("DIR"+ch_dir())

    link = Link(server_config_path)
    schedule_data = link.load_schedule()
    if not schedule_data:
        schedule_data = load_schedule_from_json(json_path)

    window = SidePanelApp(link, schedule_data)
    window.show()
    sys.exit(app.exec())
