# main.py
import DPlayer_Core as core
import DPlayer_Gui as gui
import customtkinter as ctk
import os
import threading


root = ctk.CTk()
gui.build_ui(root)
root.protocol("WM_DELETE_WINDOW", core.force_close)
threading.Thread(target=core.fetch_music, daemon=True).start()
root.mainloop()