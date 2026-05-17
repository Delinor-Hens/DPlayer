import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import os
import DPlayer_Core as core
from PIL import Image, ImageTk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ACCENT = "#6C63FF"
ACCENT_HOVER = "#5A52D5"
PROGRESS_COLOR = "#E94560"
BG_MAIN = "#121212"
BG_SURFACE = "#1E1E1E"
BG_SCROLL = "#252525"
TEXT_COLOR = "#FFFFFF"
TEXT_SECONDARY = "#B3B3B3"

def build_list_ctk():
    for widget in core.lst_cont.winfo_children():
        widget.destroy()
    core.all_items.clear()

    for item in core.music:
        item_frame = ctk.CTkFrame(
            core.lst_cont,
            fg_color=BG_SCROLL,
            corner_radius=6,
            cursor="hand2"
        )
        item_frame.pack(fill="x", ipady=8, anchor="w", padx=5, pady=2)

        label = ctk.CTkLabel(
            item_frame,
            text=os.path.basename(item),
            fg_color="transparent",
            text_color=TEXT_COLOR,
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
            padx=10
        )
        label.pack(fill="both", expand=True)

        def on_enter(event, f=item_frame, l=label):
            f.configure(fg_color=ACCENT)
            l.configure(text_color=TEXT_COLOR)
        def on_leave(event, f=item_frame, l=label):
            f.configure(fg_color=BG_SCROLL)
            l.configure(text_color=TEXT_COLOR)

        item_frame.bind("<Enter>", on_enter)
        item_frame.bind("<Leave>", on_leave)
        label.bind("<Enter>", on_enter)
        label.bind("<Leave>", on_leave)

        click_action = lambda event, name=item: core.clc(name)
        item_frame.bind("<Button-1>", click_action)
        label.bind("<Button-1>", click_action)

        core.all_items.append((item.lower(), item_frame))

    core.canvas.configure(scrollregion=core.canvas.bbox("all"))
    core.song_label.configure(text="Трек не выбран")
    core.root.update_idletasks()

core.build_list = build_list_ctk

def build_ui(root):
    core.root = root
    root.title("DPlayer")
    window_width = 850
    window_height = 900
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width / 2 - window_width / 2)
    center_y = int(screen_height / 2 - window_height / 2)
    root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
    root.resizable(True, True)
    try:
        root.iconbitmap("DPlayer.ico")
    except Exception:
        root.withdraw()
        messagebox.showerror("Ошибка системы", "Не найден файл DPlayer.ico. Пожалуйста, верните файл в папку DPlayer")
        os._exit(0)

    root.configure(fg_color=BG_MAIN)

    title_label = ctk.CTkLabel(
        root,
        text="DPlayer",
        font=ctk.CTkFont(size=28, weight="bold"),
        text_color=ACCENT
    )
    title_label.pack(pady=20)

    main_frame = ctk.CTkFrame(
        root,
        corner_radius=16,
        fg_color=BG_SURFACE,
        width=700,
        height=750
    )
    main_frame.pack_propagate(False)
    main_frame.pack(pady=10, padx=20)

    core.song_label = ctk.CTkLabel(
        main_frame,
        text="Загрузка треков...",
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color=TEXT_COLOR
    )
    core.song_label.pack(pady=20)

    controls_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    controls_frame.pack(pady=30, side=tk.BOTTOM)

    prev_btn = ctk.CTkButton(
        controls_frame,
        text="⏮",
        font=ctk.CTkFont(size=22),
        fg_color=ACCENT,
        hover_color=ACCENT_HOVER,
        width=50,
        corner_radius=10,
        command=core.play_prev
    )
    prev_btn.pack(side=tk.LEFT, padx=10)

    core.btn = ctk.CTkButton(
        controls_frame,
        text="▶",
        font=ctk.CTkFont(size=24),
        fg_color=ACCENT,
        hover_color=ACCENT_HOVER,
        width=70,
        corner_radius=10,
        command=core.listen
    )
    core.btn.pack(side=tk.LEFT, padx=10)

    next_btn = ctk.CTkButton(
        controls_frame,
        text="⏭",
        font=ctk.CTkFont(size=22),
        fg_color=ACCENT,
        hover_color=ACCENT_HOVER,
        width=50,
        corner_radius=10,
        command=core.play_next
    )
    next_btn.pack(side=tk.LEFT, padx=10)

    core.search_var = tk.StringVar()
    search_entry = ctk.CTkEntry(
        main_frame,
        textvariable=core.search_var,
        font=ctk.CTkFont(size=12),
        fg_color=BG_SCROLL,
        text_color=TEXT_COLOR,
        border_color=ACCENT,
        corner_radius=8
    )
    search_entry.pack(fill="x", padx=20, pady=(10, 0))

    scroll_wrapper = ctk.CTkFrame(
        main_frame,
        corner_radius=10,
        fg_color=BG_SCROLL,
        border_width=1,
        border_color=ACCENT
    )
    scroll_wrapper.pack(padx=20, pady=20, fill="both", expand=True)

    core.canvas = tk.Canvas(
        scroll_wrapper,
        bg=BG_SCROLL,
        highlightthickness=0,
        bd=0
    )
    v_scrollbar = tk.Scrollbar(
        scroll_wrapper,
        orient="vertical",
        command=core.canvas.yview,
        bg=BG_SCROLL,
        troughcolor=BG_SURFACE,
        activebackground=ACCENT
    )
    h_scrollbar = tk.Scrollbar(
        scroll_wrapper,
        orient="horizontal",
        command=core.canvas.xview,
        bg=BG_SCROLL,
        troughcolor=BG_SURFACE,
        activebackground=ACCENT
    )

    core.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
    core.canvas.grid(row=0, column=0, sticky="nsew")
    v_scrollbar.grid(row=0, column=1, sticky="ns")
    h_scrollbar.grid(row=1, column=0, sticky="ew")

    scroll_wrapper.grid_rowconfigure(0, weight=1)
    scroll_wrapper.grid_columnconfigure(0, weight=1)

    core.lst_cont = tk.Frame(core.canvas, bg=BG_SCROLL)
    canvas_window = core.canvas.create_window((0, 0), window=core.lst_cont, anchor="nw")

    def update_scroll_region(event):
        core.canvas.configure(scrollregion=core.canvas.bbox("all"))

    core.lst_cont.bind("<Configure>", update_scroll_region)

    def _on_mousewheel(event):
        core.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    core.canvas.bind_all("<MouseWheel>", _on_mousewheel)

    core.search_var.trace_add("write", core.filter_list)

    time_frame = ctk.CTkFrame(
        main_frame,
        corner_radius=10,
        fg_color=BG_SCROLL,
        height=60
    )
    time_frame.pack_propagate(False)
    time_frame.pack(pady=20, padx=20, fill="x")

    core.now_lbl = ctk.CTkLabel(
        time_frame,
        text="00:00",
        font=ctk.CTkFont(size=16),
        text_color=TEXT_SECONDARY
    )
    core.now_lbl.pack(side=tk.LEFT, padx=10)

    core.all_lbl = ctk.CTkLabel(
        time_frame,
        text="00:00",
        font=ctk.CTkFont(size=16),
        text_color=TEXT_SECONDARY
    )
    core.all_lbl.pack(side=tk.RIGHT, padx=10)

    core.progress_canvas = tk.Canvas(
        time_frame,
        width=core.slider_width,
        height=20,
        bg=BG_SCROLL,
        highlightthickness=0,
        bd=0,
        cursor="hand2"
    )
    core.progress_canvas.pack(side=tk.LEFT, padx=10, fill="x", expand=True)

    core.progress_canvas.create_rectangle(
        0, 8, core.slider_width, 12,
        fill=BG_SURFACE, outline="", tags="bg_line"
    )
    core.progress_canvas.create_rectangle(
        0, 8, 0, 12,
        fill=PROGRESS_COLOR, outline="", tags="fill_line"
    )
    core.progress_canvas.create_rectangle(
        0, 2, 10, 18,
        fill=PROGRESS_COLOR, outline="", tags="thumb"
    )

    core.progress_canvas.bind("<Button-1>", core.click_slider)
    core.progress_canvas.bind("<B1-Motion>", core.drag_slider)
    core.progress_canvas.bind("<ButtonRelease-1>", core.release_slider)

    root.protocol("WM_DELETE_WINDOW", core.force_close)