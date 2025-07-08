#version 3.2.0

import os
import platform
import ctypes
import threading
import tkinter
import mss
import mss.tools
import pynput

from typing import Optional, Any
from pynput import keyboard
from datetime import datetime
from tkinter import filedialog

from utils.directory_util import get_resource_directory
from utils.key_normalize_util import normalize_hotkey
from utils.config_util import Config

class QuickRegionSS:
    def __init__(self, root) -> None:
        # GUIパラメータ
        self.root = root
        self.root.geometry("450x450+0+0")
        self.root.resizable(0, 0)
        self.root.title("QuickRegionSS")
        self.root.iconbitmap(os.path.join(get_resource_directory(), "icon.ico"))

        self.config: Config = Config()
        self.listener_thread: Optional[threading.Thread] = None
        self.listener_controller: Optional[keyboard.GlobalHotKeys] = None

        self.log_after: Optional[int] = None

        self.build_gui()
        self.initialize_listener()

        self.update_all_rabel()

# -------------------------------GUI構築-------------------------------
    def build_gui(self) -> None:

        tkinter.Frame(root).pack(pady=5)

        button_frame = tkinter.Frame(root)
        button_frame.pack(pady=5)

        self.pos_button = tkinter.Button(button_frame, text="範囲設定", command=self.set_pos)
        self.pos_button.pack(side="left", expand=True, padx=5)

        folder_button = tkinter.Button(button_frame, text="フォルダ選択", command=self.set_folder)
        folder_button.pack(side="left", expand=True, padx=5)

        keyconf_frame = tkinter.Frame(root)
        keyconf_frame.pack(pady=5)

        self.key_input = tkinter.Entry(keyconf_frame, width=15)
        self.key_input.pack(side="left", expand=True, padx=5)

        key_button = tkinter.Button(keyconf_frame, text="キー変更", command=self.set_key)
        key_button.pack(side="left", expand=True, padx=5)
        
        tkinter.Frame(root).pack(pady=20)

        poslabel_frame = tkinter.Frame(root)
        poslabel_frame.pack(pady=3)

        self.label_pos1 = tkinter.Label(poslabel_frame)
        self.label_pos1.pack(side="left", expand=True, padx=5)

        self.label_pos2 = tkinter.Label(poslabel_frame)
        self.label_pos2.pack(side="left", expand=True, padx=5)

        self.current_key_label = tkinter.Label(root)
        self.current_key_label.pack(pady=3)

        self.label_folder = tkinter.Label(root)
        self.label_folder.pack(pady=3)

        self.log = tkinter.Label(root, text="")
        self.log.pack(pady=30)

        if not self.config.debug_mode:
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
    def debug_fun(self) -> Any:
        self.config.save_config()

# -------------------------------ユーティリティ-------------------------------
    def update_all_rabel(self) -> None:
        self.label_pos1.config(text=f"pos1: {self.config.pos1}")
        self.label_pos2.config(text=f"pos2: {self.config.pos2}")
        self.current_key_label.config(text=f"key: {self.config.key}")
        self.label_folder.config(text=f"folder: {self.ellipsis_folder_name(self.config.save_folder)}")

    def ellipsis_folder_name(self, string: str, length: int = 20) -> str:
        if len(string) > length:
            string = "..." + string[-length:]
        return string
    
    def update_log_message(self, message: str, color: str) -> None:
        self.log.config(text=message)
        self.log.config(bg=color)
        if self.log_after:
            self.root.after_cancel(self.log_after)
        self.log_after = self.root.after(1000, lambda: self.log.config(bg=self.root.cget("bg")))

    def update_log_message_success(self, message: str) -> None:
        self.update_log_message(message, "lightgreen")
    def update_log_message_warn(self, message: str) -> None:
        self.update_log_message(message, "yellow") 
    def update_log_message_error(self, message:str) -> None:
        self.update_log_message(message, "indianred")  
# -------------------------------保存フォルダ設定-------------------------------
    def set_folder(self) -> None:
        try:
            old_folder = self.config.save_folder
            folder = filedialog.askdirectory()
            if folder:
                self.config.set_save_folder(folder)
                self.update_log_message_success("フォルダ設定完了")
        except Exception:
            self.update_log_message_error("キー変更中にエラーが発生しました。")
            self.config.set_save_folder(old_folder)
        finally:
            self.update_all_rabel()

# -------------------------------ホットキー設定-------------------------------
    def update_key_info(self) -> None:
        self.key_input.delete(0, tkinter.END)
        self.key_input.insert(0, self.config.key)
        self.update_all_rabel()

    def get_input_key_and_normalize(self) -> None | str:
        return normalize_hotkey(self.key_input.get())

    def initialize_listener(self) -> None:
        init_key = normalize_hotkey(self.config.key)
        if not init_key:
            init_key = "<ctrl>+s"
        self.start_hotkey_listener(init_key)
        self.update_key_info()

    def start_hotkey_listener(self, key: str) -> None:
        if self.listener_controller:
            self.listener_controller.stop()

        self.listener_controller = keyboard.GlobalHotKeys({
            key: self.on_shortcut_pressed
        })

        self.listener_thread = threading.Thread(target=self.listener_controller.start, daemon=True)
        self.listener_thread.start()

    def set_key(self) -> None:
        try:
            old_key = self.config.key
            new_key = self.get_input_key_and_normalize()

            if not new_key:
                self.update_log_message_warn("キーが正しくありません")
                return

            self.start_hotkey_listener(new_key)
            self.config.set_key(new_key)
            self.update_log_message_success(f"{new_key} キー登録完了")
        except Exception as e:
            self.update_log_message_error("キー変更中にエラーが発生しました。")
            self.start_hotkey_listener(old_key)
            self.config.set_key(old_key)
        finally:
            self.update_key_info()

# -------------------------------座標設定-------------------------------
    def reset_pos(self) -> None:
        self.config.pos1 = None
        self.config.pos2 = None
        self.update_all_rabel()

    def set_pos(self) -> None:
        self.reset_pos()
        self.pos_button.config(state="disabled")

        # マウスクリック待機スレッド
        def listen_mouse_clicks():
            try:
                with pynput.mouse.Listener(on_click=self.on_click) as listener:
                    listener.join()
            except Exception:
                self.update_log_message_error("座標設定でエラーが発生しました。")
            finally:
                self.pos_button.config(state="active")
        threading.Thread(target=listen_mouse_clicks, daemon=True).start()

    # pos設定処理
    def on_click(self, x: int, y: int, _: Any, pressed: bool) -> bool:
        if pressed:
            if self.config.pos1 is None:
                self.config.pos1 = (x, y)
                self.update_all_rabel()
            else:
                self.config.pos2 = (x, y)
                self.update_all_rabel()
                self.update_log_message_success("座標設定完了")
                return False
        return True

# -------------------------------撮影処理-------------------------------
    def on_shortcut_pressed(self) -> None:
        try:
            if self.config.pos1 and self.config.pos2:
                x1, y1 = self.config.pos1
                x2, y2 = self.config.pos2
                left, top = min(x1, x2), min(y1, y2)
                width, height = abs(x2 - x1), abs(y2 - y1)

                with mss.mss() as sct:
                    monitor = {"left": left, "top": top, "width": width, "height": height}
                    sct_img = sct.grab(monitor)

                    os.makedirs(self.config.save_folder, exist_ok=True)
                    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                    filename = f"screenshot_{timestamp}.png"
                    filepath = os.path.join(self.config.save_folder, filename)

                    mss.tools.to_png(sct_img.rgb, sct_img.size, output=filepath)
                    self.update_log_message_success(f"{filename}を保存しました")
            else:
                self.update_log_message_warn(f"座標を指定してください")
        except Exception as e:
            self.update_log_message_error("撮影時にエラーが発生しました")
            print(e)

# -------------------------------アプリ終了処理-------------------------------
    def exit_app(self) -> None:
        self.config.save_config()
        if self.listener_controller:
            self.listener_controller.stop()
        self.root.destroy()

# --------------------------------------------------------------

if __name__ == "__main__":
    if platform.system() == "Windows":
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            ctypes.windll.user32.SetProcessDPIAware()
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