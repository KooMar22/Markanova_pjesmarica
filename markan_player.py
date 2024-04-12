# Import modules
import os
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter.messagebox import showwarning, showerror
from pygame import mixer


class MediaPlayer:
    def __init__(self):
        self.root = Tk()
        mixer.init()
        
        self.root.title("Markanova Pjesmarica")
        self.root.resizable(False, False)

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
        self.playlist = Listbox(self.playlist_frame, width=110, height=20)
        self.playlist.pack(fill=BOTH, expand=True)
        self.playlist.bind("<<ListboxSelect>>", self.play_song)

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

        # Play and Pause button
        self.play_variable = StringVar()
        self.play_variable.set("Play")
        self.play_pause_btn = Button(self.control_panel, textvariable=self.play_variable,
                                     command=self.play_or_pause)
        self.play_pause_btn.grid(column=1, row=0, padx=10, pady=10)

        # Backward button
        self.back_btn = Button(self.control_panel, text="⏪", command=self.backward)
        self.back_btn.grid(column=0, row=0, padx=10, pady=10)

        # Forward
        self.fwd_btn = Button(self.control_panel, text="⏩", command=self.forward)
        self.fwd_btn.grid(column=2, row=0, padx=10, pady=10)

        # Volume Control
        self.volume_variable = DoubleVar()
        self.volume_variable.set(1)
        self.volume_scale = Scale(self.control_panel, orient="horizontal", from_=0, to=1,
                                  variable=self.volume_variable, command=self.set_volume)
        self.volume_scale.grid(column=4, row=0, padx=10, pady=10)

    def add_music(self):
        file_locations = filedialog.askopenfilenames(title="Please select a song",
                                                     filetypes=(("MP3 Files", "*.mp3"),))
        for song in file_locations:
            if song not in self.playlist.get(0, END):
                self.playlist.insert(END, song)

    def remove_song(self):
        current_song = self.playlist.curselection()
        self.playlist.delete(current_song[0])

    def play_song(self, event):
        selected_song = self.playlist.get(self.playlist.curselection())
        self.current_song = selected_song
        mixer.music.load(self.current_song)
        self.status_variable.set(f"{os.path.basename(self.current_song)[0:40]}...")
        self.progress_bar["maximum"] = mixer.Sound(self.current_song).get_length()
        self.update_progressbar()
        mixer.music.play()
        self.play_variable.set("Pause")


    def play_or_pause(self):
        # Play or Pause the selected song
        if self.paused:
            mixer.music.unpause()
            self.paused = False
            self.play_variable.set("Pause")
        else:
            mixer.music.pause()
            self.paused = True
            self.play_variable.set("Play")

    def backward(self):
        selection = self.playlist.curselection()
        if selection:
            prev_song_idx = int(selection[0]) - 1
            if prev_song_idx > 0:
                prev_song = self.playlist.get(prev_song_idx)
                self.current_song = prev_song
                mixer.music.load(self.current_song)
                self.status_variable.set(f"{os.path.basename(self.current_song)[0:40]}...")
                mixer.music.play()
                self.play_variable.set("Pause")
            else:
                showwarning("Warning!", "This is the first song.")
        else:
            showerror("Error!", "No song is currently selected!")

    def forward(self):
        selection = self.playlist.curselection()
        if selection:
            next_song_idx = int(selection[0]) + 1
            if next_song_idx < self.playlist.size():
                next_song = self.playlist.get(next_song_idx)
                self.current_song = next_song
                mixer.music.load(self.current_song)
                self.status_variable.set(f"{os.path.basename(self.current_song[0:40])}...")
                mixer.music.play()
                self.play_variable.set("Pause")
            else:
                showwarning("Warning!", "This is the last song in your playlist.")
    
    def set_volume(self, val):
        volume = float(val)
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