# Import modules
import os
from random import shuffle
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter.messagebox import showinfo, showerror, showwarning
from pygame import mixer
from PIL import Image, ImageTk


# Create empty playlist to store selected music
playlist = []


class MediaPlayer:
    def __init__(self):
        self.root = Tk()
        mixer.init()
        
        self.root.title("Markanova Pjesmarica")
        self.root.resizable(False, False)
        self.root.iconbitmap("imgs/music_notes_icon.ico")

        # Size of the window
        self.win_width = 700
        self.win_height = 500

        # Size of the screen
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # Center it
        self.x_coord = (self.screen_width - self.win_width) // 2
        self.y_coord = (self.screen_height - self.win_height) // 2
        self.root.geometry("{}x{}+{}+{}".format(self.win_width, self.win_height,
                                                self.x_coord, self.y_coord))

        # Add Frames - Playlist Frame, Music Info Frame and Control Panel Frame
        self.playlist_frame = Frame(self.root)
        self.playlist_frame.grid(column=0, row=0, padx=10, pady=(0, 10))

        self.music_info_frame = Frame(self.root)
        self.music_info_frame.grid(column=0, row=1)

        self.control_panel = Frame(self.root)
        self.control_panel.grid(column=0, row=2, padx=10, pady=10)
        self.control_panel.configure(border=1, relief="flat", borderwidth=2)

        # Music Menu
        self.menu = Menu(self.root)
        self.root.config(menu=self.menu)
        self.add_music_menu = Menu(self.menu)
        self.menu.add_cascade(label="Menu", menu=self.add_music_menu)
        self.add_music_menu.add_command(label="Add Music", command=self.add_music)
        self.add_music_menu.add_cascade(label="Remove Music", command=self.remove_song)


        # Playlist listbox
        self.playlist_listbox = Listbox(self.playlist_frame, width=110, height=20,
                                selectmode=SINGLE)
        for song in playlist:
            self.playlist_listbox.insert(END, song)
        self.playlist_listbox.pack(fill=BOTH, expand=True)
        self.playlist_listbox.bind("<<ListboxSelect>>", self.play_song)

        # Add Progress Bar
        self.progress_bar = ttk.Progressbar(self.music_info_frame, orient="horizontal",
                                            length=630, mode="determinate")
        self.progress_bar.grid(column=0, row=1, padx=5)

        # Elapsed time
        self.elapsed_time = Label(self.music_info_frame, text="00:00")
        self.elapsed_time.grid(column=1, row=1)

        self.status_variable = StringVar()
        self.status_variable.set("")
        self.status_lbl = Label(self.music_info_frame, textvariable=self.status_variable)
        self.status_lbl.grid(column=0, row=0, padx=10, pady=10, sticky="ew")

        # Current song label
        self.current_song = ""
        # Is the song paused or not?
        self.paused = False

        # Add button images
        self.play_img = self.load_image("imgs/play_btn.png")
        self.pause_img = self.load_image("imgs/pause_btn.png")
        self.shuffle_img = self.load_image("imgs/shuffle_btn.png")
        self.back_img = self.load_image("imgs/back_btn.png")
        self.stop_img = self.load_image("imgs/stop_btn.png")
        self.fwd_img = self.load_image("imgs/forward_btn.png")

        # Play and Pause button
        self.play_pause_btn = Button(self.control_panel, image=self.play_img,
                                     command=self.play_or_pause)
        self.play_pause_btn.image = self.play_img
        self.play_pause_btn.grid(column=2, row=0, padx=10, pady=10)

        # Stop button
        self.stop_btn = Button(self.control_panel, image=self.stop_img, command=self.stop_song)
        self.stop_btn.image = self.stop_img
        self.stop_btn.grid(column=3, row=0, padx=10, pady=10)

        # Shuffle button
        self.shuffle_btn = Button(self.control_panel, image=self.shuffle_img, command=self.shuffle)
        self.shuffle_btn.image = self.shuffle_btn
        self.shuffle_btn.grid(column=0, row=0, padx=10, pady=10)

        # Backward button
        self.back_btn = Button(self.control_panel, image=self.back_img, command=self.backward)
        self.back_img.image = self.back_img
        self.back_btn.grid(column=1, row=0, padx=10, pady=10)

        # Forward
        self.fwd_btn = Button(self.control_panel, image=self.fwd_img, command=self.forward)
        self.fwd_btn.image= self.fwd_img
        self.fwd_btn.grid(column=4, row=0, padx=10, pady=10)

        # Volume Control
        self.volume_variable = DoubleVar()
        self.volume_variable.set(5)
        self.volume_scale = Scale(self.control_panel, orient="horizontal", from_=0, to=10,
                                  variable=self.volume_variable, command=self.set_volume)
        self.volume_scale.grid(column=5, row=0, padx=10, pady=10)

    def load_image(self, path):
        img = Image.open(path)
        return ImageTk.PhotoImage(img)

    def add_music(self):
        selected_files = filedialog.askopenfilenames(title="Please select a song",
                                                     filetypes=(("MP3 Files", "*.mp3"),))
        # Put opened files into tuple
        file_tuple = self.root.splitlist(selected_files)
        # Convert that tuple to a list
        file_list = list(file_tuple)
        # Add the full file names to the playlist, but also display short version
        for song in file_list:
            if song not in playlist:
                playlist.append(song)
                temp_array = song.split("/")
                song_short = temp_array[len(temp_array) - 1]
                self.playlist_listbox.insert(END, song_short)

    def remove_song(self):
        current_song = self.playlist_listbox.curselection()
        self.playlist_listbox.delete(current_song[0])
        mixer.music.stop()

    def play_song(self, event):
        if len(playlist) == 0:
            showinfo("Notice!", "No songs in your playlist. Please add a song.")
        else:
            mixer.music.stop()
            selected_songs = self.playlist_listbox.curselection()
            self.current_song = playlist[int(selected_songs[0])]
            mixer.music.load(self.current_song)
            self.status_variable.set(os.path.splitext(os.path.basename(self.current_song))[0])
            self.progress_bar["maximum"] = mixer.Sound(self.current_song).get_length()
            self.update_progressbar()
            mixer.music.play(0, 0.0)
            self.play_pause_btn.config(image=self.pause_img)

    def stop_song(self):
        mixer.music.stop()
        self.play_pause_btn.config(image=self.play_img)

    def play_or_pause(self):
        # Play or Pause the selected song
        if self.paused:
            mixer.music.unpause()
            self.paused = False
            self.play_pause_btn.config(image=self.pause_img)
        else:
            mixer.music.pause()
            self.paused = True
            self.play_pause_btn.config(image=self.play_img)

    def shuffle(self): # Ovo tek trebam implementirati kako treba
        songs = list(self.playlist_listbox.get(0, END))
        shuffle(songs)
        self.playlist_listbox.delete(0, END)
        for song in songs:
            self.playlist_listbox.insert(END, song)

    def backward(self):
        selection = self.playlist_listbox.curselection()
        if selection:
            prev_song_idx = int(selection[0]) - 1
            if prev_song_idx >= 0:
                prev_song = playlist[prev_song_idx]
                self.current_song = prev_song
                mixer.music.load(self.current_song)
                self.status_variable.set(os.path.splitext(os.path.basename(self.current_song))[0])
                mixer.music.play()
                self.play_pause_btn.config(image=self.pause_img)
            else:
                showwarning("Warning!", "This is the first song.")
        else:
            showerror("Error!", "No song is currently selected!")

    def forward(self):
        selection = self.playlist_listbox.curselection()
        if selection:
            next_song_idx = int(selection[0]) + 1
            if next_song_idx < self.playlist_listbox.size():
                next_song = playlist[next_song_idx]
                self.current_song = next_song
                mixer.music.load(self.current_song)
                self.status_variable.set(os.path.splitext(os.path.basename(self.current_song))[0])
                mixer.music.play()
                self.play_pause_btn.config(image=self.pause_img)
            else:
                showwarning("Warning!", "This is the last song in your playlist.")
    
    def set_volume(self, val):
        volume = float(val) / 10
        mixer.music.set_volume(volume)

    def update_progressbar(self):
        current_time = mixer.music.get_pos() / 1000
        self.progress_bar["value"] = current_time
        mins, secs = divmod(int(current_time), 60)
        self.elapsed_time.config(text="{:02d}:{:02d}".format(mins, secs))
        self.root.after(1000, self.update_progressbar)


if __name__ == "__main__":
    pjesmarica = MediaPlayer()
    pjesmarica.root.mainloop()