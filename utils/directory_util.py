import sys
import os

def get_config_path() -> str:
    if getattr(sys, 'frozen', False):
        path = os.path.dirname(sys.executable)
    else:
        path = os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.join(path, "config.json")

def get_resource_directory() -> str:
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        path = sys._MEIPASS
    else:
        path = os.path.abspath(".")
    return path
