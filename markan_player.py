# Import modules
import os, time
from random import sample
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


        # Add a song time Label
        self.song_time_lbl = Label(self.music_info_frame, text="")
        self.song_time_lbl.grid(column=1, row=1, padx=5)

        # Initialize song_paths lists
        self.song_paths = []
        # Dictionary to map listbox indices to file paths
        self.index_to_path = {}
        # Current song label
        self.current_song = ""
        # Song length
        self.song_len = ""
        # Is the song paused or not?
        self.paused = False
        # Is the song stopped or playing?
        self.stopped = False
        # Is the playlist shuffled or not?
        self.shuffled = False

        # Add button images
        self.play_img = self.load_image("imgs/play_btn.png")
        self.pause_img = self.load_image("imgs/pause_btn.png")
        self.shuffle_off_img = self.load_image("imgs/shuffle_btn_off.png")
        self.shuffle_on_img = self.load_image("imgs/shuffle_btn_on.png")
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
        self.shuffle_btn = Button(self.control_panel, image=self.shuffle_on_img, command=self.shuffle)
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


    def load_image(self, path):
        """Function to handle loading of images"""
        img = Image.open(path)
        return ImageTk.PhotoImage(img)

    def extract_song_info(self, file_path):
        """Extracts song metadata (artist and title)"""
        try:
            audio = MP3(file_path)
            artist = audio['TPE1'].text[0] if 'TPE1' in audio else 'Unknown Artist'
            title = audio['TIT2'].text[0] if 'TIT2' in audio else 'Unknown Title'
            return {'artist': artist, 'title': title}
        except Exception as e:
            print(f"Error extracting metadata for {file_path}: {e}")
            return None


    def add_music(self):
        files = filedialog.askopenfilenames(initialdir="D:\\My Music",
                                            filetypes=(("MP3 files", "*.mp3"),))
        for file_path in files:
            # Extract metadata
            song_info = self.extract_song_info(file_path)
            if song_info:
                # Add song info to playlist listbox
                self.playlist_listbox.insert(END, f"{song_info['artist']} - {song_info['title']}")
                # Add file path to song_paths list
                index = self.playlist_listbox.size() - 1
                self.song_paths.append(file_path)
                # Update index_to_path dictionary
                self.index_to_path[index] = file_path


    def remove_song(self):
        """Function to remove selected song"""
        music_playlist = self.playlist_listbox.curselection()
        if music_playlist:
            # Stop the song
            self.stop_song()
            # Get the index of the selected song
            removed_index = music_playlist[0]
            # Delete the song from the playlist listbox
            self.playlist_listbox.delete(removed_index)
            # Remove the path from song_paths list
            self.song_paths.pop(removed_index)
            # Remove the corresponding entry from index_to_path
            del self.index_to_path[removed_index]
            # Clear the status variable
            self.status_variable.set("")
            # Reset the play/pause button
            self.play_pause_btn.config(image=self.play_img)

            # Remove the last entry in index_to_path dictionary
            if self.index_to_path:
                self.index_to_path.popitem()


    def clear_all(self):
        """Function to clear the playlist"""
        # Stop the song
        self.stop_song()
        # Clear the playlist listbox
        self.playlist_listbox.delete(0, END)
        # Clear the song_paths list
        self.song_paths.clear()
        # Clear the index_to_path dictionary
        self.index_to_path.clear()
        # Clear the status variable
        self.status_variable.set("")
        # Reset the play/pause button
        self.play_pause_btn.config(image=self.play_img)


    def play_song(self, event=None):
        """Function to play the selected song"""
        music_playlist = self.playlist_listbox.curselection()
        if music_playlist:
            index = music_playlist[0]
            song_path = self.index_to_path[index]
            # Reset Progress Slider and Song Time Label
            self.progress_slider.config(value=0)
            self.song_time_lbl.config(text="")
            # Set Stopped variable to False
            self.stopped = False
            # Use song path from song_paths list
            song_path = self.song_paths[music_playlist[0]]
            mixer.music.load(song_path)
            mixer.music.play(loops=0)
            self.play_pause_btn.config(image=self.pause_img)
            # Extract song info
            song_info = self.extract_song_info(song_path)
            if song_info:
                # Update status variable with artist and title
                self.status_variable.set(f"{song_info['artist']} - {song_info['title']}")
            # Update the elapsed time when song is playing
            self.update_time()


    def stop_song(self):
        """Function to stop the selected song"""
        # Reset Progress Slider and Song Time Label
        self.progress_slider.config(value=0)
        self.song_time_lbl.config(text="")
        # Stop the song
        mixer.music.stop()
        self.playlist_listbox.selection_clear(ACTIVE)
        # Clear the status variable
        self.status_variable.set("")
        # Get Stop variable to True
        self.stopped = True
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


    def shuffle(self):
        """Function to handle toggling between shuffle on or off"""
        # Shuffle the playlist?
        if self.shuffled:
            self.shuffled = False
            self.shuffle_btn.config(image=self.shuffle_on_img)
        else:
            self.shuffled = True
            self.shuffle_btn.config(image=self.shuffle_off_img)


    def backward(self):
        """Function to handle playing the previous song."""
        # Reset Progress Slider and Song Time Label
        self.progress_slider.config(value=0)
        self.song_time_lbl.config(text="")
        # Get the current song number
        music_playlist = self.playlist_listbox.curselection()
        # Check if music_playlist is not empty
        if music_playlist:
            if self.shuffled:
                prev_song = sample(range(0, self.playlist_listbox.size()), 1)[0]
                # Ensure the next song is not the current one
                while prev_song == music_playlist[0]:
                    prev_song = sample(range(0, self.playlist_listbox.size()), 1)[0]
            else:
                if music_playlist[0] > 0:
                    # Move it by one
                    prev_song = music_playlist[0] - 1
                else:
                    # If on the first song, move it to the end
                    prev_song = self.playlist_listbox.size() - 1
            # Grab the song title
            song = self.song_paths[prev_song]  # Use song path from song_paths list
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
            # Extract song info
            song_info = self.extract_song_info(song)
            if song_info:
                # Update status variable with artist and title
                self.status_variable.set(f"{song_info['artist']} - {song_info['title']}")


    def forward(self):
        """Function to handle playing the next song."""
        # Reset Progress Slider and Song Time Label
        self.progress_slider.config(value=0)
        self.song_time_lbl.config(text="")
        # Get the current song number
        music_playlist = self.playlist_listbox.curselection()
        # Check if music_playlist is not empty
        if music_playlist:
            if self.shuffled:
                next_song = sample(range(0, self.playlist_listbox.size()), 1)[0]
                # Ensure the next song is not the current one
                while next_song == music_playlist[0] or next_song == self.playlist_listbox.size():
                    next_song = sample(
                        range(0, self.playlist_listbox.size()), 1)[0]
            else:
                # Check if the current song is not the last one in the playlist
                if music_playlist[0] < self.playlist_listbox.size() - 1:
                    # Move it by one
                    next_song = music_playlist[0] + 1
                else:
                    # If on the last song, move it to the beginning
                    next_song = 0
            # Grab the song title
            song = self.song_paths[next_song]  # Use song path from song_paths list
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
            # Extract song info
            song_info = self.extract_song_info(song)
            if song_info:
                # Update status variable with artist and title
                self.status_variable.set(
                    f"{song_info['artist']} - {song_info['title']}")

    
    def set_volume(self, value):
        """Function to handle the volume"""
        mixer.music.set_volume(self.volume_scale.get() / 10)


    def slide(self, music_playlist):
        """Function to handle the Progress slider"""
        music_playlist = self.playlist_listbox.curselection()
        if music_playlist:
            # Use song path from song_paths list
            song = self.song_paths[music_playlist[0]]
            mixer.music.load(song)
            mixer.music.play(loops=0, start=int(self.progress_slider.get()))


    def update_time(self):
        """Function to update the elapsed time"""
        # Get currently playing song
        music_playlist = self.playlist_listbox.curselection()
        if music_playlist:
            if self.stopped:
                return

            # Get the elapsed time
            current_time = mixer.music.get_pos() / 1000
            mins, secs = divmod(int(current_time), 60)
            elapsed_time = "{:02d}:{:02d}".format(mins, secs)
            # Grab the song title
            # Use song path from song_paths list
            song = self.song_paths[music_playlist[0]]
            # Load song with Mutagen
            song_mut = MP3(song)
            # Get song length
            self.song_len = song_mut.info.length
            # Convert to time format
            mins, secs = divmod(int(self.song_len), 60)
            total_time = "{:02d}:{:02d}".format(mins, secs)

            # Increase current time by 1 sec
            current_time += 1

            if int(self.progress_slider.get()) == int(self.song_len):
                # Go to the next song after the current finishes - wait for 1 sec
                time.sleep(1)
                self.forward()

            elif self.paused:
                pass

            elif int(self.progress_slider.get()) == int(current_time):
                # Update Slider to Position
                slider_pos = int(self.song_len)
                self.progress_slider.config(to=slider_pos, value=int(current_time))
            else:
                # Update Slider to Position
                slider_pos = int(self.song_len)
                self.progress_slider.config(to=slider_pos, value=int(self.progress_slider.get()))

                # Convert the time from the Progress Slider into min and sec format
                mins, secs = divmod(int(self.progress_slider.get()), 60)
                elapsed_time = "{:02d}:{:02d}".format(mins, secs)

                # Update the song time
                self.song_time_lbl.config(text=f"{elapsed_time} / {total_time}")

                # Move this thing along by 1 sec
                next_time = int(self.progress_slider.get()) + 1
                self.progress_slider.config(value=next_time)

            # Update the elapsed time
            self.root.after(1000, self.update_time)



if __name__ == "__main__":
    pjesmarica = MediaPlayer()
    pjesmarica.root.mainloop()