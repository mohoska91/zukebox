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
        self._refreshing = False
        self._callback = None
        self._control = None

    def send_request(self, request: ZukeRequest, response_callback=None):
        request = ZukeRequestThread(request, response_callback)
        request.start()
        self._requests.append(request)

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

    def get_control(self, callback=None):
        self.send_request(
            ZukeRequest(
                self._config_manager.zuke_ip,
                self._config_manager.zuke_port,
                "GET",
                "/player/control"
            ),
            callback
        )

    def run(self):
        while self._refreshing:
                self.get_control(self._callback)
                time.sleep(1)

    def _refresh_callback(self, response):
        self._control = response
        self._callback(response)

    def start_refreshing(self, callback=None):
        if not self._refreshing:
            self._callback = callback
            self._refreshing = True
            self.start()

    def stop_refreshing(self):
        if self._refreshing:
            self._refreshing = False
            self.quit()

    @property
    def control(self):
        return self._control