import os


class ZukeConfigmanager:

    def __init__(self, filename):
        self.filename = filename
        self.__create_config_from_file()

    def __create_config_from_file(self):
        configfile = open(os.path.join(os.getcwd(), self.filename), 'r')
        configfile_lines = configfile.read().splitlines()
        self.zukebox_configuration = {
            "user": configfile_lines[0],
            "zukebox_ip": configfile_lines[1],
            "zukebox_port": configfile_lines[2]
        }

    def get_config(self):
        return self.zukebox_configuration

    def getIp(self):
        return self.zukebox_configuration["zukebox_ip"]

    def getPort(self):
        return self.zukebox_configuration["zukebox_port"]

    def getUser(self):
        return self.zukebox_configuration["zukebox_user"]