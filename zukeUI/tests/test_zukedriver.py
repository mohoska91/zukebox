import unittest

from utils.zukedriver import ZukeDriver


class ZukeDriverTest(unittest.TestCase):
    def setUp(self):
        self.zbd = ZukeDriver()

    def test_username(self):
        self.assertEqual("MOHI 10.30.255.175 5000", self.zbd.getconf())

    def test_sendcommand(self):
        self.assertEqual("", self.zbd.getsendcommand())


if __name__ == '__main__':
    unittest.main()
