import sys
import os
import ctypes
import tkinter as tk

# Point to bundled VLC
base_path = os.path.dirname(__file__)
vlc_dir = os.path.join(base_path, "vlc")
dll_path = os.path.join(vlc_dir, "libvlc.dll")
plugin_path = os.path.join(vlc_dir, "plugins")

# Set VLC plugin environment
os.environ["VLC_PLUGIN_PATH"] = plugin_path

# Load libvlc.dll manually before importing python-vlc
ctypes.CDLL(dll_path)  # This line solves your error

import vlc  # safe to import after DLL is loaded

# GUI setup
root = tk.Tk()
root.title("Embedded VLC Player")
root.geometry("800x600")

video_frame = tk.Frame(root)
video_frame.pack(fill=tk.BOTH, expand=1)
root.update()

instance = vlc.Instance()
player = instance.media_player_new()

player.set_hwnd(video_frame.winfo_id())  # Windows only
media = instance.media_new("sample.mp4")
player.set_media(media)
player.play()

root.mainloop()