import base64
import io
import os
import tkinter as tk
import urllib.request

import time

from utils.threadhandling.threaddecorators import thread, daemon
from utils.zukedriver import ZukeDriver
from PIL import Image, ImageTk

class ZukeUi(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self,root)
        self.after_initialization = False
        self.zd = ZukeDriver()
        control = self.zd.get_control()
        self.init_ui(root, control)
        self.refresh = True
        self.refresh_seekscale = True
        self.refresh_volumescale = True
        self.refresher()

        self.pack(fill="both", expand="true")

        self.after_initialization = True


    def __del__(self):
        self.refresh = False

    def init_ui(self,root,control):
        self.root = root
        self.root.title("ZukeUi")
        self.root.iconphoto(True,ImageTk.PhotoImage(file='sources/zukebox.jpg'))
        self.actual_track_title = ""
        self.pic_and_title_frame = tk.Frame(self)
        self.pic_and_title_frame.pack(fill="x")
        opened_img = Image.open(os.path.join(os.getcwd(), 'sources/default.jpg'))
        opened_img = opened_img.resize((350, 350), Image.PERSPECTIVE)
        self.actual_track_image = ImageTk.PhotoImage(opened_img)
        self.track_img_label = tk.Label(self.pic_and_title_frame, image=self.actual_track_image)
        self.track_img_label.pack(padx=5, pady=5)
        self.track_img_label.image = self.actual_track_image
        self.track_title_label = tk.Label(self.pic_and_title_frame, text="")
        self.track_title_label.pack()

        self.sender_frame = tk.Frame(self)
        self.sender_frame.pack(fill="x")
        self.sender_label = tk.Label(self.sender_frame, text="Sender:",width=10)
        self.sender_label.pack(side="left",padx=5, pady=5)
        self.name_label = tk.Label(self.sender_frame)
        self.name_label.pack(fill="x",side="right",padx=5, pady=5, expand="true")

        self.url_frame = tk.Frame(self)
        self.url_frame.pack(fill="x")
        self.url_label = tk.Label(self.url_frame, text="URL:",width=10)
        self.url_label.pack(side="left",padx=5,pady=5)
        self.url_entry= tk.Entry(self.url_frame)
        self.url_entry.pack(fill="x",side="right",padx=5,pady=5,expand="true")

        self.message_frame = tk.Frame(self)
        self.message_frame.pack(fill="x")
        self.message_label = tk.Label(self.message_frame, text="Message:",width=10)
        self.message_label.pack(side="left",padx=5, pady=5)
        self.message_entry = tk.Entry(self.message_frame)
        self.message_entry.pack(fill="x",side="right",padx=5, pady=5, expand="true")


        self.volume_set_frame = tk.Frame(self)
        self.volume_set_frame.pack(fill="x")
        self.volume_label = tk.Label(self.volume_set_frame, text="Volume:", width=10)
        self.volume_label.pack(side="left",padx=5,pady=5)

        self.volume_setter = \
            tk.Scale(self.volume_set_frame, from_=0, to=100, command=self.set_volume, orient="horizontal", length=200)
        self.volume_setter.pack(side="right",fill="x",expand="true",padx=5,pady=5)
        self.volume_setter.set(control["volume"])

        self.seek_set_frame = tk.Frame(self)
        self.seek_set_frame.pack(fill="x")
        self.seek_label = tk.Label(self.seek_set_frame, text="Seek:", width=10)
        self.seek_label.pack(side="left", padx=5, pady=5)

        self.actual_track_duration = 200
        if "duration" in control["track"].keys():
            self.actual_track_duration = control["track"]["duration"]

        self.seek_setter = \
            tk.Scale(self.seek_set_frame, from_=0, to=self.actual_track_duration,command=self.set_seek, orient="horizontal", length=200)
        self.seek_setter.pack(side="right", fill="x", expand="true", padx=5, pady=5)
        self.seek_setter.set(control["time"])

        self.button_frame = tk.Frame(self)
        self.button_frame.pack(fill="x",expand="true")

        self.playorpause_button = tk.Button(self.button_frame, text="Play/Pause", command=self.play_or_pause)
        self.playorpause_button.pack(fill="x")
        self.send_button = tk.Button(self.button_frame, text="Send", command=self.send_link_and_message)
        self.send_button.pack(fill="x")

    @daemon
    def refresher(self):
        while self.refresh:
            control = self.zd.get_control()
            track = control["track"]
            self.refresh_volumescale = False
            self.volume_setter.set(control["volume"])
            if track and "title" in track.keys():
                self.refresh_seekscale=False
                self.seek_setter.set(control["time"])
                if track["title"] != self.actual_track_title:
                    self.seek_setter.configure(to=track["duration"])
                    self.actual_track_title = track["title"]
                    self.actual_sender = track["user"]
                    self.actual_track_image = ImageTk.PhotoImage(self.get_pic(track["thumbnail"]))
                    self.track_img_label.configure(image=self.actual_track_image)
                    self.track_img_label.image=self.actual_track_image
                    self.track_title_label.configure(text=self.actual_track_title)
                    self.name_label.configure(text=self.actual_sender)
            time.sleep(1)

    def get_pic(self, image_url):
        image, headers = urllib.request.urlretrieve(image_url)
        opened_img = Image.open(image)
        opened_img = opened_img.resize((350, 350), Image.PERSPECTIVE)
        return opened_img


    def play_or_pause(self):
        if self.after_initialization:
            if self.zd.get_control()["playing"] == 1:
                self.zd.play_or_pause(0)
            elif self.zd.get_control()["track"]:
                self.zd.play_or_pause(1)

    def send_link_and_message(self):
        response = ""
        if self.after_initialization:
            url = self.url_entry.get()
            message = self.message_entry.get()
            if url:
                if message:
                    response = self.zd.send_track_with_message(url,message)
                    self.message_entry.delete(0, 'end')
                else:
                    response = self.zd.send_track(url)
                self.url_entry.delete(0, 'end')


    def set_volume(self, volume):
        if self.after_initialization and self.refresh_volumescale:
            self.zd.set_volume(volume)
        self.refresh_volumescale=True

    def set_seek(self, seek):
        if self.after_initialization and self.refresh_seekscale:
            self.zd.set_seek(seek)
        self.refresh_seekscale=True


def main():
    root = tk.Tk()
    ZukeUi(root).pack(expand=True, fill='both')
    root.mainloop()


if __name__ == "__main__":
    main()
