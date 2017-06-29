from driver.utils.connection.request_managing import RequestManager


class ZukeUiManager:

    def __init__(self, rm: RequestManager):
        self.__rm = rm

    def send_url(self, url: str, message: str, callback=None):
        if url:
            self.__rm.send_track(url, callback, message)

    def set_volume(self, volume, callback=None):
        self.__rm.set_volume(volume, callback)

    def set_seek(self, seek, callback=None):
        self.__rm.set_seek(seek, callback)

    def play_or_pause(self, play_or_pause, callback=None):
        self.__rm.play_or_pause(play_or_pause, callback)

    def stop_refreshing(self):
        self.__rm.stop_refreshing()

    def start_refreshing(self, ui_callback):
        self.__rm.start_refreshing(ui_callback)

    def get_control(self, callback=None):
        self.__rm.get_control(callback)

    @property
    def control(self):
        return self.__rm.control
