import json
import requests
import os

class Link:
    def __init__(self, server_config_path):
        self.server_config_path = server_config_path

    def load_server_config(self):
        try:
            with open(self.server_config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('server_ip', 'localhost')
        except Exception as e:
            print(f"读取服务器设置文件错误: {e}")
            return 'localhost'

    def load_schedule(self):
        try:
            server_ip = self.load_server_config()
            response = requests.get(f'http://{server_ip}/api/schedule')
            if response.status_code == 200:
                return response.json()
            else:
                print(f"服务器错误: {response.status_code}")
                return None
        except Exception as e:
            print(f"网络请求错误: {e}")
            return None