#version 2.0.0

import os
import json
import threading
import tkinter
from datetime import datetime

import pyautogui
import pynput
import keyboard

from tkinter import filedialog


class ContinuousScreenShot:
    def __init__(self, root):
        # GUIパラメータ
        self.root = root
        self.root.geometry("450x450+0+0")
        self.root.resizable(0, 0)
        self.root.title("連続スクショ")

        # 機能パラメータ
        self.load_config()

        # キーバインド
        keyboard.add_hotkey('ctrl+s', lambda: self.on_shortcut_pressed())

        # GUIレイアウト
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
            end_frame = tkinter.Frame(root)
            end_frame.pack(pady=10)

            self.exit_button = tkinter.Button(root, text="終了", command=self.exit_app)
            self.exit_button.pack(side="left", expand=True, padx=5)

            self.debug_button = tkinter.Button(root, text="debug", command=self.debug_fun)
            self.debug_button.pack(side="left", expand=True, padx=5)

    def debug_fun(self):
        self.save_config()
        print("現在のホットキー:", keyboard._hotkeys)

    def load_config(self):
        if os.path.exists("config.json"):
            try:
                with open("config.json", "r") as f:
                    config = json.load(f)
                self.debug_mode = config.get("debug_mode", False)
                self.save_folder = config.get("save_folder", "./")
                self.key = config.get("shortcut_key", "ctrl+s")
                self.pos1 = tuple(config.get("pos1")) if config.get("pos1") else None
                self.pos2 = tuple(config.get("pos2")) if config.get("pos2") else None
            except Exception as e:
                self.log.config(text=f"設定ファイルが読み込めませんでした")
        else:
            self.save_folder = "./"
            self.key = "ctrl+s"
            self.pos1 = None
            self.pos2 = None
            self.debug_mode = False

    def save_config(self):
        config = {
            "debug_mode": self.debug_mode,
            "save_folder": self.save_folder,
            "shortcut_key": self.key,
            "pos1": self.pos1,
            "pos2": self.pos2
        }
        try:
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"設定ファイルの保存に失敗しました: {e}")

    # フォルダ設定処理
    def set_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.save_folder = folder
            self.label_folder.config(text=f"folder: {self.save_folder}")
            self.save_config()
            self.log.config(text="フォルダ設定完了")

    def set_key(self):
        old_key = self.key
        new_key = self.key_input.get()
        try:
            keyboard.unhook_all_hotkeys()
            self.key = new_key
            keyboard.add_hotkey(new_key, lambda: self.on_shortcut_pressed())
            self.log.config(text="キー設定完了")
            self.save_config()
        except ValueError:
            self.log.config(text=f"エラー： キーが間違っています")
            self.key = old_key
            keyboard.add_hotkey(old_key, lambda: self.on_shortcut_pressed())
        finally:
            self.current_key_label.config(text=f"key: {self.key}")
            self.key_input.delete(0, tkinter.END)
            self.key_input.insert(0, self.key) 

    # pos設定ハンドラ（マウスクリックをスレッドで処理）
    def set_pos(self):
        self.pos1 = None
        self.pos2 = None
        self.pos_button.config(state="disabled")
        threading.Thread(target=self.listen_mouse_clicks, daemon=True).start()

    # マウスクリック待機スレッド
    def listen_mouse_clicks(self):
        with pynput.mouse.Listener(on_click=self.on_click) as listener:
            listener.join()

    # pos設定処理
    def on_click(self, x, y, button, pressed):
        if pressed:
            if self.pos1 is None:
                self.pos1 = (x, y)
                self.label_pos1.config(text=f"pos1: {self.pos1}")
            else:
                self.pos2 = (x, y)
                self.label_pos2.config(text=f"pos2: {self.pos2}")
                self.pos_button.config(state="active")
                self.log.config(text="座標設定完了")
                self.save_config()
                return False

    # スクリーンショット撮影処理
    def on_shortcut_pressed(self):
        print("現在のホットキー:", keyboard._hotkeys)
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
                self.log.config(text=f"{filename}を保存しました")
            else:
                self.log.config(text=f"エラー: 座標を指定してください")
        except AttributeError as e:
            self.log.config(text=f"エラー: {e}")

    # アプリ終了処理
    def exit_app(self):
        self.save_config()
        keyboard.unhook_all_hotkeys()
        self.root.destroy()

if __name__ == "__main__":
    root = tkinter.Tk()
    app = ContinuousScreenShot(root)
    root.mainloop()

# import time
# import traceback
    # try:
    #     root = tkinter.Tk()
    #     app = ContinuousScreenShot(root)
    #     root.mainloop()
    # except Exception as e:
    #     print(traceback.format_exc())
    # finally:
    #     time.sleep(3)
