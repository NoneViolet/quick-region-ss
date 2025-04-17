#version 2.0.5

import os
import json
import threading
import tkinter
import pyautogui
import pynput
import keyboard

from typing import Optional, Tuple
from datetime import datetime
from tkinter import filedialog

class QuickRegionSS:
    def __init__(self, root):
        # GUIパラメータ
        self.root = root
        self.root.geometry("450x450+0+0")
        self.root.resizable(0, 0)
        self.root.title("QuickRegionSS")

        # 機能パラメータ
        self.load_config()

        # キーバインド
        keyboard.add_hotkey(self.key, lambda: self.on_shortcut_pressed())

        self.build_gui()

# -------------------------------GUI構築-------------------------------
    def build_gui(self):
        button_frame = tkinter.Frame(root)
        button_frame.pack(pady=10)

        self.pos_button = tkinter.Button(button_frame, text="範囲設定", command=self.set_pos)
        self.pos_button.pack(side="left", expand=True, padx=5)

        self.folder_button = tkinter.Button(button_frame, text="フォルダ選択", command=self.set_folder)
        self.folder_button.pack(side="left", expand=True, padx=5)

        keyconf_frame = tkinter.Frame(root)
        keyconf_frame.pack(pady=10)

        self.key_input = tkinter.Entry(keyconf_frame, width=10)
        self.key_input.insert(0, self.key) 
        self.key_input.pack(side="left", expand=True, padx=5)

        self.key_button = tkinter.Button(keyconf_frame, text="キー変更", command=self.set_key)
        self.key_button.pack(side="left", expand=True, padx=5)

        poslabel_frame = tkinter.Frame(root)
        poslabel_frame.pack(pady=10)

        self.label_pos1 = tkinter.Label(poslabel_frame, text=f"pos1: {self.pos1}")
        self.label_pos1.pack(side="left", expand=True, padx=5)

        self.label_pos2 = tkinter.Label(poslabel_frame, text=f"pos2: {self.pos2}")
        self.label_pos2.pack(side="left", expand=True, padx=5)

        self.current_key_label = tkinter.Label(root, text=f"key: {self.key}")
        self.current_key_label.pack(pady=10)

        self.label_folder = tkinter.Label(root, text=f"folder: {self.save_folder}")
        self.label_folder.pack(pady=10)

        self.log = tkinter.Label(root, text="")
        self.log.pack(pady=10)

        if not self.debug_mode:
            self.exit_button = tkinter.Button(root, text="終了", command=self.exit_app)
            self.exit_button.pack(pady=10)
        else:
            footer_frame = tkinter.Frame(root)
            footer_frame.pack(pady=10)

            self.exit_button = tkinter.Button(footer_frame, text="終了", command=self.exit_app)
            self.exit_button.pack(side="left", expand=True, padx=5)

            self.debug_button = tkinter.Button(footer_frame, text="debug", command=self.debug_fun)
            self.debug_button.pack(side="left", expand=True, padx=5)

# -------------------------------デバッグ用-------------------------------
    def debug_fun(self):
        self.save_config()
        print("現在のホットキー:", keyboard._hotkeys)


# -------------------------------ユーティリティ-------------------------------
    def update_all_rabel(self):
        self.label_pos1.config(text=f"pos1: {self.pos1}")
        self.label_pos2.config(text=f"pos2: {self.pos2}")
        self.current_key_label.config(text=f"key: {self.key}")
        self.label_folder.config(text=f"folder: {self.save_folder}")

    def get_config_path(self):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")



# -------------------------------コンフィグ関連-------------------------------
    def reset_config(self):
        self.debug_mode: bool = False
        self.save_folder: str = "./"
        self.key: str = "ctrl+s"
        self.pos1: Optional[Tuple[int, int]] = None
        self.pos2: Optional[Tuple[int, int]] = None

    def load_config(self):
        if os.path.exists(self.get_config_path()):
            try:
                with open(self.get_config_path(), "r", encoding="utf-8") as f:
                    config = json.load(f)
                self.debug_mode = config.get("debug_mode", False)
                self.save_folder = config.get("save_folder", "./")
                self.key = config.get("shortcut_key", "ctrl+s")
                self.pos1 = tuple(config.get("pos1")) if config.get("pos1") else None
                self.pos2 = tuple(config.get("pos2")) if config.get("pos2") else None
            except Exception as e:
                self.reset_config()
                self.save_config()
        else:
            self.reset_config()
            self.save_config()

    def save_config(self):
        config = {
            "debug_mode": self.debug_mode,
            "save_folder": self.save_folder,
            "shortcut_key": self.key,
            "pos1": self.pos1,
            "pos2": self.pos2
        }
        try:
            with open(self.get_config_path(), "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"設定ファイルの保存に失敗しました: {e}")

# -------------------------------保存フォルダ設定-------------------------------
    def set_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.save_folder = folder
            self.update_all_rabel()
            self.save_config()
            self.update_log_message("フォルダ設定完了")

# -------------------------------ホットキー設定-------------------------------
    def set_key(self):
        old_key = self.key
        new_key = self.key_input.get()
        try:
            keyboard.unhook_all_hotkeys()
            self.key = new_key
            keyboard.add_hotkey(new_key, lambda: self.on_shortcut_pressed())
            self.update_log_message("キー設定完了")
            self.save_config()
        except ValueError:
            self.update_log_message("エラー： キーが間違っています")
            self.key = old_key
            keyboard.add_hotkey(old_key, lambda: self.on_shortcut_pressed())
        finally:
            self.update_all_rabel()
            self.key_input.delete(0, tkinter.END)
            self.key_input.insert(0, self.key) 

# -------------------------------座標設定-------------------------------
    def set_pos(self):
        self.pos1 = None
        self.pos2 = None
        self.update_all_rabel()
        self.pos_button.config(state="disabled")

        # マウスクリック待機スレッド
        def listen_mouse_clicks():
            with pynput.mouse.Listener(on_click=self.on_click) as listener:
                listener.join()
        threading.Thread(target=listen_mouse_clicks, daemon=True).start()

    # pos設定処理
    def on_click(self, x, y, button, pressed):
        if pressed:
            if self.pos1 is None:
                self.pos1 = (x, y)
                self.update_all_rabel()
            else:
                self.pos2 = (x, y)
                self.update_all_rabel()
                self.pos_button.config(state="active")
                self.update_log_message("座標設定完了")
                self.save_config()
                return False

# -------------------------------撮影処理-------------------------------
    def on_shortcut_pressed(self):
        try:
            if self.pos1 and self.pos2:
                x1, y1 = self.pos1
                x2, y2 = self.pos2
                left, top = min(x1, x2), min(y1, y2)
                width, height = abs(x2 - x1), abs(y2 - y1)

                screenshot = pyautogui.screenshot(region=(left, top, width, height))
                os.makedirs(self.save_folder, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                filename = f"screenshot_{timestamp}.png"
                screenshot.save(os.path.join(self.save_folder, filename))
                self.update_log_message(f"{filename}を保存しました")
            else:
                self.update_log_message(f"エラー: 座標を指定してください")
        except AttributeError as e:
            self.update_log_message(f"エラー: {e}")

# -------------------------------アプリ終了処理-------------------------------
    def exit_app(self):
        self.save_config()
        keyboard.unhook_all_hotkeys()
        self.root.destroy()

# --------------------------------------------------------------

if __name__ == "__main__":
    root = tkinter.Tk()
    app = QuickRegionSS(root)
    root.mainloop()

# import time
# import traceback
    # try:
    #     root = tkinter.Tk()
    #     app = QuickRegionSS(root)
    #     root.mainloop()
    # except Exception as e:
    #     print(traceback.format_exc())
    # finally:
    #     time.sleep(3)