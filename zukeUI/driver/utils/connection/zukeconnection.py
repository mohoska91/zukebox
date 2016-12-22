import http.client
import json
from PyQt5 import QtCore
from json import JSONDecodeError


class InvalidZukeResponseError(Exception):
    pass


class ZukeAvailabilityError(Exception):
    pass


class ZukeRequest:

    def __init__(self, ip: str, port: str, command: str, url: str, *, body: dict=None, headers: dict=None):
        self.ip = ip
        self.port = port
        self.command = command
        self.url = url
        self.body = body if body else ""
        self.headers = headers if headers else {}

    def do_request(self):
        conn = http.client.HTTPConnection(self.ip, self.port)
        try:
            conn.request(
                self.command,
                self.url,
                self.body,
                self.headers
            )
            return json.loads(conn.getresponse().read().decode('utf-8'))
        except JSONDecodeError:
            raise InvalidZukeResponseError("Invalid zukeresponse")
        except:
            raise ZukeAvailabilityError("Zukebox unavailable")
        finally:
            conn.close()


class ZukeRequestThread(QtCore.QThread):
    response_signal = QtCore.pyqtSignal(dict)

    def __init__(self, zukerequest: ZukeRequest, callback):
        QtCore.QThread.__init__(self)
        self._zr = zukerequest
        self._callback = callback

    def run(self):
        if self._callback:
            self.response_signal.connect(self._callback)
            self.response_signal.emit(self._zr.do_request())
        else:
            self._zr.do_request()
