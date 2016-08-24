import json

from utils.configuration.zukeconfigmanager import ZukeConfigmanager
from utils.connection.zukeconnector import ZukeConnector
from utils.threadhandling.threaddecorators import thread


class ZukeDriver:
    def __init__(self):
        self.zuke_configurator = ZukeConfigmanager("sources/config.txt")
        self.zuke_connector = ZukeConnector(self.zuke_configurator.get_config())
        self.follow = True

    @thread
    def send_track(self, url):
        params = json.dumps({'url': url, 'user': self.zuke_configurator.getUser()})
        headers = {'content-type': 'application/json'}
        response = self.zuke_connector.send_request("POST", "/player/tracks", params, headers)
        return response

    @thread
    def send_track_with_message(self, url, message):
        params = json.dumps({'url': url, 'user': self.zuke_configurator.getUser(), 'message': message, 'lang': 'hu'})
        headers = {'content-type': 'application/json'}
        response = self.zuke_connector.send_request("POST", "/player/tracks", params, headers)
        return response

    def set_volume(self, volume_value):
        params = json.dumps({'volume': volume_value})
        headers = {'content-type': 'application/json'}
        self.zuke_connector.send_request("PATCH", "/player/control", params, headers)

    def set_seek(self, seek_value):
        params = json.dumps({'time': seek_value})
        headers = {'content-type': 'application/json'}
        self.zuke_connector.send_request("PATCH", "/player/control", params, headers)

    def get_control(self):
        json_response = self.zuke_connector.send_request("GET", "/player/control")
        return json_response

    def get_tracks(self):
        json_response = self.zuke_connector.send_request("GET", "/player/tracks")
        return json_response

    def get_recent_tracks(self):
        json_response=self.zuke_connector.send_request("GET", "/player/recent-tracks")
        return json_response

    def delete_track(self, track_id):
        json_response = self.zuke_connector.send_request("DELETE", "/player/tracks/{number}".format(number=track_id))
        return json_response

    def play_or_pause(self, play_or_pause):
        params = json.dumps({'playing': play_or_pause})
        headers = {'content-type': 'application/json'}
        json_response =self.zuke_connector.send_request("PATCH", "/player/control", params, headers)
        return json_response

    def getvolume(self):
        return self.get_control()["volume"]

    # def getconf(self):
    #     return self.username + " " + self.zukebox_ip + " " + self.zukebox_port
    #
    # def getsendcommand(self):
    #     return "connection POST {ip}:{port}/player/tracks url=\"{url}\" user=\"{user}\"".format(
    #         ip=self.zukebox_ip,
    #         port=self.zukebox_port,
    #         url="x",
    #         user=self.username
    #     )
