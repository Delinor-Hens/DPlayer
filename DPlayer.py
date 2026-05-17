# Программа для прослушивания музыки
import tkinter as tk
from tkinter import font
from just_playback import Playback
import win32com.client
import os

playback = Playback()
current_track = None
timer_id = None
# Фукнции
def check_playback():
    global timer_id
    if playback.playing:
        if (playback.duration - playback.curr_pos) <= 0.3:
            stop()
        else:
            timer_id = root.after(300, check_playback)
    else:
        stop()

def stop():
    global timer_id
    try:
        if timer_id:
            root.after_cancel(timer_id)
            timer_id = None
        playback.stop()
        btn.config(text="▶", command=listen)
    except Exception as e:
        print(e)

def listen():
    if current_track:
        try:
            playback.load_file(current_track)
            playback.play()
            btn.config(text="⏸", command=stop)
            root.after(100, check_playback)
        except Exception as e:
            print(e)
    else:
        song_label.configure(text="Трек не выбран")

def clc(c):
    stop()
    global current_track
    current_track = c
    song_label.configure(text=os.path.basename(c))
    return c


music = []
try:
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
icon = tk.PhotoImage(file="DPlayer.png")
root.iconphoto(False, icon)
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

song_label = tk.Label(main_frame, text="Трек не выбран", font=frame_font, fg="#050A0F", bg="#C9D5FA")
song_label.pack(pady=20, side=tk.TOP)

btn = tk.Button(main_frame, text="▶", font=btn_font, fg="#050A0F", bg="#5985FF", width=5, height=1, command=listen)
btn.pack(pady=50, side=tk.BOTTOM)



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

all_items = []

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

def filter_list(*args):
    search_query = search_var.get().lower()
    for text_lower, frame in all_items:
        if search_query in text_lower:
            frame.pack(fill="x", ipady=10, anchor="w", padx=5)
        else:
            frame.pack_forget()
    canvas.configure(scrollregion=canvas.bbox("all"))

search_var.trace_add("write", filter_list)



true_lbl = tk.Label()

root.mainloop()
