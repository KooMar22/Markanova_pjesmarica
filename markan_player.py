# Import modules
import os
import time
from random import shuffle
from tkinter import *
from tkinter import filedialog, ttk
from pygame import mixer
from PIL import Image, ImageTk
from mutagen.mp3 import MP3


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
        self.menu.add_cascade(label="Manage Music", menu=self.add_music_menu)
        self.add_music_menu.add_command(label="Add Music", command=self.add_music)
        self.add_music_menu.add_cascade(label="Remove Music", command=self.remove_song)
        self.add_music_menu.add_cascade(label="Clear Playlist", command=self.clear_all)


        # Playlist listbox
        self.playlist_listbox = Listbox(self.playlist_frame, width=110, height=20,
                                selectbackground="gray", selectforeground="black",
                                selectmode=SINGLE)
        self.playlist_listbox.pack(fill=BOTH, expand=True)
        self.playlist_listbox.bind("<<ListboxSelect>>", self.play_song)

        # Add a Status Info about currently playing song
        self.status_variable = StringVar()
        self.status_variable.set("")
        self.status_lbl = Label(self.music_info_frame, textvariable=self.status_variable)
        self.status_lbl.grid(column=0, row=0, padx=10, pady=10, sticky="ew")

        # Add Progress Slider
        self.progress_slider = ttk.Scale(self.music_info_frame, length=600,
                                         from_=0, to=100, orient="horizontal",
                                         value=0, command=self.slide)
        self.progress_slider.grid(column=0, row=1, padx=10, sticky="w")

        # Create a temporary Slider Label
        self.slider_lbl = Label(self.music_info_frame, text="0")
        self.slider_lbl.grid(column=0, row=2)

        # Add a song time Label
        self.song_time_lbl = Label(self.music_info_frame, text="")
        self.song_time_lbl.grid(column=1, row=1, padx=5)

        # Current song label
        self.current_song = ""
        # Song length
        self.song_len = ""
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
        """Function to handle loading of images"""
        img = Image.open(path)
        return ImageTk.PhotoImage(img)

    def add_music(self):
        """Function to add songs from directories"""
        directory = filedialog.askdirectory(initialdir="D:\\My Music")
        os.chdir(directory)
        for song in os.listdir(directory):
            if song.endswith(".mp3"):
                self.playlist_listbox.insert(END, song)

    def remove_song(self):
        """Function to remove selected song"""
        music_playlist = self.playlist_listbox.curselection()
        if music_playlist:
            mixer.music.stop()
            self.playlist_listbox.delete(music_playlist[0])
            self.status_variable.set("")
            self.play_pause_btn.config(image=self.play_img)

    def clear_all(self):
        """Function to clear the playlist"""
        mixer.music.stop()
        self.playlist_listbox.delete(0, END)
        self.status_variable.set("")
        self.play_pause_btn.config(image=self.play_img)

    def play_song(self, event=None):
        """Function to play the selected song"""
        music_playlist = self.playlist_listbox.curselection()
        if music_playlist:
            song = self.playlist_listbox.get(music_playlist[0])
            mixer.music.load(song)
            mixer.music.play(loops=0)
            self.play_pause_btn.config(image=self.pause_img)
            self.status_variable.set(song)
            # Update the elapsed time when song is playing
            self.update_time()
            # Update Slider to Position
            slider_pos = int(self.song_len)
            self.progress_slider.config(to=slider_pos, value=0)

    def stop_song(self):
        """Function to stop the selected song"""
        mixer.music.stop()
        self.playlist_listbox.selection_clear(ACTIVE)
        # Clear the status variable
        self.status_variable.set("")
        self.play_pause_btn.config(image=self.play_img)
        # Clear the song time
        self.song_time_lbl.config(text="")

    def play_or_pause(self):
        """Function to handle toggling between Play and Pause buttons"""
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
        pass

    def backward(self):
        """Function to handle playing the previous song."""
        # Get the current song number
        music_playlist = self.playlist_listbox.curselection()
        if music_playlist[0] > 0:
            # Move it by one
            prev_song = music_playlist[0] - 1
        else:
            # If on the first song, move it to the end
            prev_song = self.playlist_listbox.size() - 1
        # Grab the song title
        song = self.playlist_listbox.get(prev_song)
        # Load it and play
        mixer.music.load(song)
        mixer.music.play(loops=0)
        # Move the bar to that song so the next one could be selected again
        self.playlist_listbox.selection_clear(0, END)
        self.playlist_listbox.activate(prev_song)
        # Set active bar to previous song
        self.playlist_listbox.selection_set(prev_song, last=None)
        # Display Pause button
        self.play_pause_btn.config(image=self.pause_img)
        # Display the song title into the song status
        self.status_variable.set(song)


    def forward(self):
        """Function to handle playing the next song."""
        # Get the current song number
        music_playlist = self.playlist_listbox.curselection()
        if music_playlist[0] < self.playlist_listbox.size() - 1:
            # Move it by one
            next_song = music_playlist[0] + 1
        else:
            # If on the last song, move it to the beginning
            next_song = 0
        # Grab the song title
        song = self.playlist_listbox.get(next_song)
        # Load it and play
        mixer.music.load(song)
        mixer.music.play(loops=0)
        # Move the bar to that song so the next one could be selected again
        self.playlist_listbox.selection_clear(0, END)
        self.playlist_listbox.activate(next_song)
        # Set active bar to next song
        self.playlist_listbox.selection_set(next_song, last=None)
        # Display Pause button
        self.play_pause_btn.config(image=self.pause_img)
        # Display the song title into the song status
        self.status_variable.set(song)

    
    def set_volume(self, val):
        """Function to handle the volume"""
        volume = float(val) / 10
        mixer.music.set_volume(volume)

    def slide(self, music_playlist):
        # self.slider_lbl.config(text=f"{int(self.progress_slider.get())} / {int(self.song_len)}")
        music_playlist = self.playlist_listbox.curselection()
        if music_playlist:
            song = self.playlist_listbox.get(music_playlist[0])
            mixer.music.load(song)
            mixer.music.play(loops=0, start=int(self.progress_slider.get()))


    def update_time(self):
        """Function to update the elapsed time"""
        # Get currently playing song
        music_playlist = self.playlist_listbox.curselection()
        if music_playlist:
            # Get the elapsed time
            current_time = mixer.music.get_pos() / 1000
            mins, secs = divmod(int(current_time), 60)
            elapsed_time = "{:02d}:{:02d}".format(mins, secs)
            # Grab the song title
            song = self.playlist_listbox.get(music_playlist[0])
            # Load song with Mutagen
            song_mut = MP3(song)
            # Get song length
            self.song_len = song_mut.info.length
            # Convert to time format
            mins, secs = divmod(int(self.song_len), 60)
            total_time = "{:02d}:{:02d}".format(mins, secs)

            # Update the song time
            self.song_time_lbl.config(text=f"{elapsed_time} / {total_time}")

            # Update Slider position value to current song position
            self.progress_slider.config(value=int(current_time))

            # Go to the next song after the current finishes - wait for 1 sec
            if elapsed_time == total_time:
                time.sleep(1)
                self.forward()

            # Update the elapsed time
            self.root.after(1000, self.update_time)


if __name__ == "__main__":
    pjesmarica = MediaPlayer()
    pjesmarica.root.mainloop()