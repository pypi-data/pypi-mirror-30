# coding=utf-8


import time
import json
from airtest_hunter import AirtestHunter, open_platform
from poco.drivers.netease.internal import NeteasePoco

from pocounit.case import PocoTestCase
from airtest.core.api import connect_device, device as current_device
from poco.drivers.android.uiautomation import AndroidUiautomationPoco


class Case(PocoTestCase):
    @classmethod
    def setUpClass(cls):
        super(Case, cls).setUpClass()
        if not current_device():
            connect_device('Android:///')

    def runTest(self):
        from poco.drivers.cocosjs import CocosJsPoco
        poco = CocosJsPoco()
        for n in poco():
            print n.get_name()


# if __name__ == '__main__':
#     import pocounit
#     pocounit.main()


from hunter_cli import Hunter, open_platform
from poco.drivers.netease.internal import NeteasePoco

tokenid = open_platform.get_api_token('test')
hunter = Hunter(tokenid, 'h54', 'h54_at_a53a88bee64f4d3a8aca0596d9387fcd')
poco = NeteasePoco('h54', hunter)

print poco().get_name()
