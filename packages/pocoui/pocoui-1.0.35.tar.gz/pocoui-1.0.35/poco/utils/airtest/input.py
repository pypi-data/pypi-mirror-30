# coding=utf-8

try:
    from airtest.core.api import device as current_device
    from airtest.core.api import touch, swipe
    from airtest.core.helper import device_platform
except ImportError:
    # 兼容旧版本
    from airtest.cli.runner import device as current_device
    from airtest.core.main import touch, swipe
    from airtest.core.main import get_platform as device_platform
from poco.sdk.interfaces.input import InputInterface


class AirtestInput(InputInterface):
    def __init__(self):
        super(AirtestInput, self).__init__()
        self.default_touch_down_duration = 0.01

    def _get_touch_resolution(self):
        """
        get real time resolution on device if full screen
         or window size if running in window mode
        """
        return current_device().get_current_resolution()

    def setTouchDownDuration(self, duration):
        self.default_touch_down_duration = duration

    def getTouchDownDuration(self):
        return self.default_touch_down_duration

    def click(self, x, y):
        pw, ph = self._get_touch_resolution()
        pos = [x * pw, y * ph]
        touch(pos, duration=self.default_touch_down_duration)

    def swipe(self, x1, y1, x2, y2, duration=2.0):
        if duration <= 0:
            raise ValueError("Operation duration cannot be less equal 0. Please provide a positive number.")
        direction = x2 - x1, y2 - y1
        pw, ph = self._get_touch_resolution()
        p1 = [x1 * pw, y1 * ph]
        steps = int(duration * 40) + 1
        swipe(p1, vector=direction, duration=duration, steps=steps)

    def longClick(self, x, y, duration=2.0):
        if duration <= 0:
            raise ValueError("Operation duration cannot be less equal 0. Please provide a positive number.")
        pw, ph = self._get_touch_resolution()
        pos = [x * pw, y * ph]
        touch(pos, duration=duration)
