import json

import time
from PyQt5 import QtCore

from driver.utils.configuration.zukeconfiguration import ZukeConfigManager
from driver.utils.connection.zukeconnection import ZukeRequest, ZukeRequestThread


class RequestManager(QtCore.QThread):

    def __init__(self, config_manager: ZukeConfigManager):
        QtCore.QThread.__init__(self)
        self._config_manager = config_manager
        self._requests = []

    def send_request(self, request: ZukeRequest, response_callback=None):
        request = ZukeRequestThread(request, response_callback)
        request.start()
        self._requests.append(request)

    def run(self):
        pass


class UrlSendingManager(RequestManager):

    def send_track(self, url, response_callback=None, message: str=None):

        body = {'url': url, 'user': self._config_manager.zuke_user}
        if message:
            body.update({'message': message, 'lang': 'hu'})
        self.send_request(
            ZukeRequest(
                self._config_manager.zuke_ip,
                self._config_manager.zuke_port,
                "POST",
                "/player/tracks",
                body=json.dumps(body),
                headers={'content-type': 'application/json'}
            ),
            response_callback
        )


class VolumeSetterManager(RequestManager):

    def set_volume(self, volume_value, response_callback=None):
        self.send_request(
            ZukeRequest(
                self._config_manager.zuke_ip,
                self._config_manager.zuke_port,
                "PATCH",
                "/player/control",
                body=json.dumps({'volume': volume_value}),
                headers={'content-type': 'application/json'}
            ),
            response_callback
        )


class SeekSetterManager(RequestManager):

    def set_seek(self, seek_value, response_callback=None):
        self.send_request(
            ZukeRequest(
                self._config_manager.zuke_ip,
                self._config_manager.zuke_port,
                "PATCH",
                "/player/control",
                body=json.dumps({'time': seek_value}),
                headers={'content-type': 'application/json'}
            ),
            response_callback
        )


class PlayPauseManager(RequestManager):

    manager_id = "playpause_manager"
    response_signal = stop_signal = QtCore.pyqtSignal(dict, name=manager_id)

    def play_or_pause(self, play_or_pause, response_callback=None):
        self.send_request(
            ZukeRequest(
                self._config_manager.zuke_ip,
                self._config_manager.zuke_port,
                "PATCH",
                "/player/control",
                body=json.dumps({'playing': play_or_pause}),
                headers={'content-type': 'application/json'}
            ),
            response_callback
        )


class RefreshManager(RequestManager):

    manager_id = "refresh_manager"
    response_signal = stop_signal = QtCore.pyqtSignal(dict, name=manager_id)

    def __init__(self, zcm: ZukeConfigManager):
        super().__init__(zcm)
        self.__control = None
        self._refreshing = False

    def run(self):
        while self._refreshing:
                self.send_request(
                    ZukeRequest(
                        self._config_manager.zuke_ip,
                        self._config_manager.zuke_port,
                        "GET",
                        "/player/control"
                    ),
                    self._callback
                )
                time.sleep(1)

    @property
    def control(self):
        return self.__control

    def start_refreshing(self, callback=None):
        if not self._refreshing:
            self._callback = callback
            self._refreshing = True
            self.start()

    def stop_refreshing(self):
        if self._refreshing:
            self._refreshing = False
            self.quit()


class ZukeUiManager:

    def __init__(
            self,
            usm: UrlSendingManager,
            vsm: VolumeSetterManager,
            ssm: SeekSetterManager,
            ppm: PlayPauseManager,
            rm: RefreshManager
    ):
        self.prev_control = None
        self.__usm = usm
        self.__vsm = vsm
        self.__ssm = ssm
        self.__ppm = ppm
        self.__rm = rm

    def send_url(self, url: str, message: str, callback=None):
        if url:
            self.__usm.send_track(url, callback, message)

    def set_volume(self, volume, callback=None):
        self.__vsm.set_volume(volume, callback)

    def set_seek(self, seek, callback=None):
        self.__ssm.set_seek(seek, callback)

    def play_or_pause(self, play_or_pause, callback=None):
        self.__ppm.play_or_pause(play_or_pause, callback)

    def stop_refreshing(self):
        self.__rm.stop_refreshing()

    def start_refreshing(self, ui_callback):
        self.__rm.start_refreshing(ui_callback)

    @property
    def control(self):
        return self.__rm.control

