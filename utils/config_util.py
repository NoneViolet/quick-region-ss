import json
import os

from utils.directory_util import get_config_path
from typing import Optional, Tuple

class Config:
    def __init__(self) -> None:
        self.config_path: str = get_config_path()
        self.debug_mode: bool = False
        self.save_folder: str = "./"
        self.key: str = "<ctrl>+s"
        self.pos1: Optional[Tuple[int, int]] = None
        self.pos2: Optional[Tuple[int, int]] = None

        self.load_config()

    def set_pos(self, pos1:Tuple[int, int], pos2:Tuple[int, int]) -> None:
        self.pos1 = pos1
        self.pos2 = pos2
        self.save_config()
    
    def set_key(self, key:str) -> None:
        self.key = key
        self.save_config()

    def set_save_folder(self, folder:str) -> None:
        self.save_folder = folder
        self.save_config()

    def reset_config(self) -> None:
        self.debug_mode = False
        self.save_folder = "./"
        self.key = "<ctrl>+s"
        self.pos1 = None
        self.pos2 = None

    def load_config(self) -> None:
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                self.debug_mode = config.get("debug_mode", False)
                self.save_folder = config.get("save_folder", "./")
                self.key = config.get("shortcut_key", "<ctrl>+s")
                self.pos1 = tuple(config.get("pos1")) if config.get("pos1") else None
                self.pos2 = tuple(config.get("pos2")) if config.get("pos2") else None
            except Exception as e:
                self.reset_config()
                self.save_config()
        else:
            self.reset_config()
            self.save_config()

    def save_config(self) -> None:
        config = {
            "debug_mode": self.debug_mode,
            "save_folder": self.save_folder,
            "shortcut_key": self.key,
            "pos1": self.pos1,
            "pos2": self.pos2
        }
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"設定ファイルの保存に失敗しました: {e}")