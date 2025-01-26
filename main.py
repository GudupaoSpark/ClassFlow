import sys
import os
from PySide6.QtWidgets import QApplication
from ui import SidePanelApp
from link import Link
from datetime import datetime
import json



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
    app = QApplication(sys.argv)
    
    server_config_path = os.path.join(os.path.dirname(__file__), 'server_config.json')
    json_path = os.path.join(os.path.dirname(__file__), 'schedule.json')

    link = Link(server_config_path)
    schedule_data = link.load_schedule()
    if not schedule_data:
        schedule_data = load_schedule_from_json(json_path)

    window = SidePanelApp(link, schedule_data)
    window.show()
    sys.exit(app.exec())
