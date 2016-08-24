import http.client
import json
import os


class ZukeConnector:

    def __init__(self, configuration):
        self.zukebox_configuration = configuration


    def send_request(self, command, url, params=None, headers={}):
        conn = http.client.HTTPConnection(self.zukebox_configuration["zukebox_ip"],
                                          self.zukebox_configuration["zukebox_port"])
        conn.request(command, url, params, headers)
        json_string = conn.getresponse().read().decode('utf-8')
        json_response = json.loads(json_string)
        conn.close()
        return json_response

