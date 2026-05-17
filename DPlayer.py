# Программа для прослушивания музыкиimport tkinter as tk
import tkinter as tk
from tkinter import font, messagebox
from just_playback import Playback
import win32com.client
import os
import threading
import pythoncom

playback = Playback()
current_track = None
timer_id = None
is_dragging = False
slider_width = 560
current_index = -1


# Фукнции
def play_next():
    global current_index
    if not music:
        return
    current_index = (current_index + 1) % len(music)
    clc(music[current_index])
    listen()


def play_prev():
    global current_index
    if not music:
        return
    current_index = (current_index - 1) % len(music)
    clc(music[current_index])
    listen()

def update_slider_visual(x_pos):
    progress_canvas.coords("fill_line", 0, 8, x_pos, 12)
    
    thumb_x = max(5, min(x_pos, slider_width - 5))
    progress_canvas.coords("thumb", thumb_x - 5, 2, thumb_x + 5, 18)



def get_seconds_from_event(event):
    if not playback.duration:
        return 0
    percentage = event.x / slider_width
    percentage = max(0.0, min(percentage, 1.0))
    return percentage * playback.duration


def click_slider(event):
    global is_dragging
    is_dragging = True
    target_seconds = get_seconds_from_event(event)
    playback.seek(target_seconds)
    update_slider_visual(event.x)
    now_lbl.configure(text=format_time(target_seconds))


def drag_slider(event):
    update_slider_visual(event.x)
    target_seconds = get_seconds_from_event(event)
    now_lbl.configure(text=format_time(target_seconds))


def release_slider(event):
    global is_dragging
    target_seconds = get_seconds_from_event(event)
    playback.seek(target_seconds)
    is_dragging = False

def force_close():
    try:
        playback.stop()  
    except Exception:
        pass
    os._exit(0)
def format_time(seconds):
    if seconds is None or seconds < 0:
        return "00:00"
    minutes = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{minutes:02d}:{secs:02d}"

def check_playback():
    global timer_id
    if is_dragging:
        timer_id = root.after(300, check_playback)
        return
        
    if playback.playing:
        now_lbl.configure(text=format_time(playback.curr_pos))
        
        if playback.duration and playback.duration > 0:
            percentage = playback.curr_pos / playback.duration
            current_x = percentage * slider_width
            update_slider_visual(current_x)
            
        if (playback.duration - playback.curr_pos) <= 0.3:
            play_next()
        else:
            timer_id = root.after(300, check_playback)
    else:
        if timer_id:
            root.after_cancel(timer_id)
            timer_id = None



def stop():
    global timer_id
    try:
        if timer_id:
            root.after_cancel(timer_id)
            timer_id = None
        playback.stop()
        btn.config(text="▶", command=listen)
        
        now_lbl.configure(text="00:00")
        all_lbl.config(text="00:00")
        update_slider_visual(0)
    except Exception as e:
        print(e)



def listen():
    if current_track:
        try:
            playback.load_file(current_track)
            playback.play()
            btn.config(text="⏸", command=stop)
            all_lbl.config(text=format_time(playback.duration))
            root.after(100, check_playback)
        except Exception as e:
            print(e)
    else:
        song_label.configure(text="Трек не выбран")

def clc(c):
    stop()
    global current_track, current_index
    current_track = c
    if c in music:
        current_index = music.index(c)
    song_label.configure(text=os.path.basename(c))

    try:
        playback.load_file(c)
        all_lbl.config(text=format_time(playback.duration))
    except Exception as e:
        print(f"Ошибка чтения длины: {e}")
        all_lbl.config(text="00:00")
    return c



music = []
all_items = []

def fetch_music():
    global music
    try:
        pythoncom.CoInitialize()
        connection = win32com.client.Dispatch("ADODB.Connection")
        recordset = win32com.client.Dispatch("ADODB.Recordset")
        connection.Open("Provider=Search.CollatorDSO;Extended Properties='Application=Windows';")
        query = "SELECT System.ItemPathDisplay FROM SystemIndex WHERE System.FileExtension = '.mp3'"
        recordset.Open(query, connection)
        if not recordset.EOF:
            recordset.MoveFirst()
            while not recordset.EOF:
                path = recordset.Fields.Item("System.ItemPathDisplay").Value
                if path and os.path.exists(path):
                    music.append(path)
                recordset.MoveNext()
                
        recordset.Close()
        connection.Close()
    except Exception as e:
        music = []
    root.after(0, build_list)

def build_list():
    for item in music:
        item_frame = tk.Frame(lst_cont, bd=0, bg="#DFA9FF", cursor="hand2")
        item_frame.pack(fill="x", ipady=10, anchor="w", padx=5)

        label = tk.Label(
            item_frame, 
            text=os.path.basename(item), 
            bg="#DFA9FF", 
            fg="#050A0F", 
            font=("Roboto", 12, "bold"),
            anchor="w",
            padx=10
        )
        label.pack(fill="both", expand=True)

        item_frame.bind("<Enter>", lambda e, f=item_frame, l=label: on_enter(e, f, l))
        item_frame.bind("<Leave>", lambda e, f=item_frame, l=label: on_leave(e, f, l))
        label.bind("<Enter>", lambda e, f=item_frame, l=label: on_enter(e, f, l))
        label.bind("<Leave>", lambda e, f=item_frame, l=label: on_leave(e, f, l))

        click_action = lambda event, name=item: clc(name)
        item_frame.bind("<Button-1>", click_action)
        label.bind("<Button-1>", click_action)
        
        all_items.append((item.lower(), item_frame))
    canvas.configure(scrollregion=canvas.bbox("all"))
    song_label.configure(text="")
    root.update_idletasks()
    song_label.configure(text="Трек не выбран")


# Настройка окна
root = tk.Tk()
root.title("DPlayer")
window_width = 850
window_height = 900
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
center_x = int(screen_width / 2 - window_width / 2)
center_y = int(screen_height / 2 - window_height / 2)
root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
root.resizable(False, False)
try:
    icon = tk.PhotoImage(file="DPlayer.png")
    root.iconphoto(False, icon)
except Exception:
    root.withdraw() 
    messagebox.showerror("Ошибка системы", "Не найден файл DPlayer.png. Пожалуйста, верните файл в папку DPlayer")
    os._exit(0)
root.configure(bg="#5985FF")

# Шрифты
title_font = font.Font(family="Helvetica", size=20, weight="bold")
frame_font = font.Font(family="Helvetica", size=18, weight="bold")
btn_font = font.Font(family="Sans", size=25, weight="bold")


#Окно
title_label = tk.Label(root, text="DPlayer", font=title_font, fg="#050A0F", bg="#5985FF")
title_label.pack(pady=20, side=tk.TOP)

main_frame = tk.Frame(root, bd=3, relief="groove", width=700, height=750, bg="#C9D5FA")
main_frame.pack_propagate(False)
main_frame.pack(pady=20)

song_label = tk.Label(main_frame, text="Загрузка треков...", font=frame_font, fg="#050A0F", bg="#C9D5FA")
song_label.pack(pady=20, side=tk.TOP)

controls_frame = tk.Frame(main_frame, bg="#C9D5FA")
controls_frame.pack(pady=50, side=tk.BOTTOM)

prev_btn = tk.Button(controls_frame, text="⏮", font=btn_font, fg="#050A0F", bg="#5985FF", width=3, height=1, command=play_prev)
prev_btn.pack(side=tk.LEFT, padx=10)

btn = tk.Button(controls_frame, text="▶", font=btn_font, fg="#050A0F", bg="#5985FF", width=5, height=1, command=listen)
btn.pack(side=tk.LEFT, padx=10)

next_btn = tk.Button(controls_frame, text="⏭", font=btn_font, fg="#050A0F", bg="#5985FF", width=3, height=1, command=play_next)
next_btn.pack(side=tk.LEFT, padx=10)



search_var = tk.StringVar()
search_entry = tk.Entry(
    main_frame, 
    textvariable=search_var, 
    font=("Roboto", 11), 
    bg="#FFFFFF", 
    fg="#050A0F", 
    bd=1, 
    relief="solid"
)
search_entry.pack(fill="x", padx=20, pady=(10, 0))

scroll_wrapper = tk.Frame(main_frame, relief="groove", bd=2, bg="#DFA9FF")
scroll_wrapper.pack(padx=20, pady=20, fill="both", expand=True)

canvas = tk.Canvas(scroll_wrapper, bg="#DFA9FF", highlightthickness=0)
v_scrollbar = tk.Scrollbar(scroll_wrapper, orient="vertical", command=canvas.yview)
h_scrollbar = tk.Scrollbar(scroll_wrapper, orient="horizontal", command=canvas.xview)

canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

canvas.grid(row=0, column=0, sticky="nsew")
v_scrollbar.grid(row=0, column=1, sticky="ns")
h_scrollbar.grid(row=1, column=0, sticky="ew")

scroll_wrapper.grid_rowconfigure(0, weight=1)
scroll_wrapper.grid_columnconfigure(0, weight=1)

lst_cont = tk.Frame(canvas, bg="#DFA9FF")
canvas_window = canvas.create_window((0, 0), window=lst_cont, anchor="nw")

def update_scroll_region(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

lst_cont.bind("<Configure>", update_scroll_region)

def _on_mousewheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
canvas.bind_all("<MouseWheel>", _on_mousewheel)

def on_enter(event, frame, label):
    frame.configure(bg="#D387FF")
    label.configure(bg="#D387FF")

def on_leave(event, frame, label):
    frame.configure(bg="#DFA9FF")
    label.configure(bg="#DFA9FF")

def filter_list(*args):
    search_query = search_var.get().lower()
    for text_lower, frame in all_items:
        if search_query in text_lower:
            frame.pack(fill="x", ipady=10, anchor="w", padx=5)
        else:
            frame.pack_forget()
    canvas.configure(scrollregion=canvas.bbox("all"))

search_var.trace_add("write", filter_list)


time_frame = tk.Frame(main_frame, bd=3, relief="groove", width=600, height=100, bg="#C9D5FA")
time_frame.pack_propagate(False)
time_frame.pack(pady=20)
all_lbl = tk.Label(time_frame, text="00:00", font=frame_font, fg="#050A0F", bg="#C9D5FA")
all_lbl.pack(side=tk.RIGHT)
now_lbl = tk.Label(time_frame, text="00:00", font=frame_font, fg="#050A0F", bg="#C9D5FA")
now_lbl.pack(side=tk.LEFT)



progress_canvas = tk.Canvas(time_frame, width=slider_width, height=20, bg="#C9D5FA", highlightthickness=0, bd=0, cursor="hand2")
progress_canvas.pack(side=tk.LEFT, padx=10, fill="x", expand=True)

progress_canvas.create_rectangle(0, 8, slider_width, 12, fill="#A4B3E6", outline="", tags="bg_line")
progress_canvas.create_rectangle(0, 8, 0, 12, fill="#5985FF", outline="", tags="fill_line")
progress_canvas.create_rectangle(0, 2, 10, 18, fill="#050A0F", outline="", tags="thumb")

progress_canvas.bind("<Button-1>", click_slider)
progress_canvas.bind("<B1-Motion>", drag_slider)
progress_canvas.bind("<ButtonRelease-1>", release_slider)



threading.Thread(target=fetch_music, daemon=True).start()

root.protocol("WM_DELETE_WINDOW", force_close)

root.mainloop()
