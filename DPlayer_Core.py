# DPlayer_Core.py
import os
import threading
import pythoncom
from just_playback import Playback
import win32com.client
import tkinter as tk

playback = Playback()
current_track = None
timer_id = None
is_dragging = False
slider_width = 560
current_index = -1

music = []
all_items = []

ACCENT = None
TEXT_COLOR = None
BG_SCROLL = None
root = None
btn = None
song_label = None
all_lbl = None
now_lbl = None
progress_canvas = None
canvas = None
lst_cont = None
search_var = None

# Функции
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
        btn.configure(text="▶", command=listen)          
        now_lbl.configure(text="00:00")
        all_lbl.configure(text="00:00")                 
        update_slider_visual(0)
    except Exception as e:
        print(e)

def listen():
    if current_track:
        try:
            playback.load_file(current_track)
            playback.play()
            btn.configure(text="⏸", command=stop)       
            all_lbl.configure(text=format_time(playback.duration))  
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
        all_lbl.configure(text=format_time(playback.duration)) 
    except Exception as e:
        print(f"Ошибка чтения длины: {e}")
        all_lbl.configure(text="00:00")                          
    return c

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
    pass

def on_enter(event, frame, label):
    frame.configure(fg_color=ACCENT)     
    label.configure(text_color=TEXT_COLOR)

def on_leave(event, frame, label):
    frame.configure(fg_color=BG_SCROLL)
    label.configure(text_color=TEXT_COLOR)

def filter_list(*args):
    search_query = search_var.get().lower()
    for text_lower, frame in all_items:
        if search_query in text_lower:
            frame.pack(fill="x", ipady=10, anchor="w", padx=5)
        else:
            frame.pack_forget()
    canvas.configure(scrollregion=canvas.bbox("all"))