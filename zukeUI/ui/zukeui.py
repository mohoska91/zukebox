import os
import sys

import time
import urllib.request

from PyQt5 import QtWidgets

from PyQt5 import uic
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication

from driver.utils.configuration.zukeconfiguration import ZukeConfigManager
from driver.utils.connection.zukeconnection import ZukeAvailabilityError, InvalidZukeResponseError
from driver.utils.connection.request_managing import UrlSendingManager, ZukeUiManager, VolumeSetterManager, SeekSetterManager, RefreshManager, \
    PlayPauseManager


class Ui(QtWidgets.QDialog):
    def __init__(self, path, zuc: ZukeUiManager):
        super(Ui, self).__init__()
        uic.loadUi(path, self)
        self.__zuc = zuc
        self.track_picture = self.findChild(QtWidgets.QLabel, 'track_picture')
        self.track_sender = self.findChild(QtWidgets.QLabel, 'track_sender')
        self.track_title = self.findChild(QtWidgets.QLabel, 'track_title')
        self.error_message = self.findChild(QtWidgets.QLabel, 'error_message')
        self.send_button = self.findChild(QtWidgets.QPushButton, 'send_button')
        self.playorpause_button = self.findChild(QtWidgets.QPushButton, 'playorpause_button')
        self.link_edit = self.findChild(QtWidgets.QTextEdit, 'link_edit')
        self.message_edit = self.findChild(QtWidgets.QTextEdit, 'message_edit')
        self.volume_slider = self.findChild(QtWidgets.QSlider, 'volume_slider')
        self.seek_slider = self.findChild(QtWidgets.QSlider, 'seek_slider')

        self.send_button.clicked.connect(self.send_link)
        self.playorpause_button.clicked.connect(self.play_or_pause)
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.seek_slider.valueChanged.connect(self.set_seek)
        self.__is_refreshing = False
        self.__prev_title = None
        self.__prev_url = None
        try:
            self.__zuc.start_refreshing(self._refresh_callback)
        except (ZukeAvailabilityError, InvalidZukeResponseError) as ex:
            self.__zuc.stop_refreshing()
            print("Exception during starting refreshing")
            self.error_message.setText("Error! Ui refreshing turned off")
        self.__zuc.start_refreshing(self._refresh_callback)

    def __del__(self):
        self.__zuc.stop_refreshing()

    def send_link(self):
        try:
            self.__zuc.send_url(self.link_edit.toPlainText(), self.message_edit.toPlainText(), self._send_callback)
        except (ZukeAvailabilityError, InvalidZukeResponseError) as ex:
            self.__zuc.stop_refreshing()
            print("Exception during sending link")
            self.error_message.setText("Error! Ui refreshing turned off")

    def _send_callback(self, response):
        if self.link_edit.toPlainText():
            self.link_edit.setText("")
        if self.message_edit.toPlainText():
            self.message_edit.setText("")

    def play_or_pause(self):
        try:
            self.__zuc.play_or_pause(0 if self.__zuc.control["playing"] else 1)
        except (ZukeAvailabilityError, InvalidZukeResponseError) as ex:
            self.__zuc.stop_refreshing()
            print("Exception during play or pause")
            self.error_message.setText("Error! Ui refreshing turned off")

    def set_volume(self):
        if not self.__is_refreshing:
            try:
                self.__zuc.set_volume(self.volume_slider.sliderPosition())
            except (ZukeAvailabilityError, InvalidZukeResponseError) as ex:
                self.__zuc.stop_refreshing()
                print("Exception during setting volume")
                self.error_message.setText("Error! Ui refreshing turned off")

    def set_seek(self):
        if not self.__is_refreshing:
            try:
                self.__zuc.set_seek(self.seek_slider.sliderPosition())
            except (ZukeAvailabilityError, InvalidZukeResponseError) as ex:
                self.__zuc.stop_refreshing()
                print("Exception during setting seek")
                self.error_message.setText("Error! Ui refreshing turned off")

    def _refresh_callback(self, control: dict):
        track = control.get("track", {})
        title = track.get("title", None) if track else None
        if title:
            if title != self.__prev_title:
                self.track_picture.setPixmap(QPixmap(urllib.request.urlretrieve(track["thumbnail"])[0]))
                self.track_sender.setText(track["user"])
                self.track_title.setText(title)
                self.__prev_title = title
            if not self.seek_slider.isSliderDown():
                self.__is_refreshing = True
                self.seek_slider.setMaximum(track["duration"])
                self.seek_slider.setSliderPosition(control["time"])
                self.__is_refreshing = False
        if not self.volume_slider.isSliderDown():
            self.__is_refreshing = True
            self.volume_slider.setSliderPosition(control["volume"])
            self.__is_refreshing = False


if __name__ == "__main__":
    assets_path = sys.argv[1]
    zcm = ZukeConfigManager(os.path.join(assets_path, 'config.json'))
    zcm.init_config()
    app = QApplication(sys.argv)
    w = Ui(
        os.path.join(assets_path, 'zukeUI.ui'),
        ZukeUiManager(
            UrlSendingManager(zcm),
            VolumeSetterManager(zcm),
            SeekSetterManager(zcm),
            PlayPauseManager(zcm),
            RefreshManager(zcm)
        )
    )
    w.show()
    sys.exit(app.exec_())
