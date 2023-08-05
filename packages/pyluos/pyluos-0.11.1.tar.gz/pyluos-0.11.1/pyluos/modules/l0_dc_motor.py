from __future__ import division

from .module import Module


class L0DCMotor(Module):
    def __init__(self, id, alias, robot):
        Module.__init__(self, 'L0DCMotor', id, alias, robot)

        # Write
        self._s1 = None
        self._s2 = None

    @property
    def m1_speed(self):
        """ Left speed in [-1, 1] """
        return self._s1

    @m1_speed.setter
    def m1_speed(self, s1):
        s1 = min(max(s1, -1.0), 1.0)

        if s1 != self._s1:
            self._s1 = s1
            self._push_value('s1', self._s1)

    @property
    def m2_speed(self):
        """ Right speed in [-1, 1] """
        return self._s2

    @m2_speed.setter
    def m2_speed(self, s2):
        s2 = min(max(s2, -1.0), 1.0)

        if s2 != self._s2:
            self._s2 = s2
            self._push_value('s2', self._s2)
