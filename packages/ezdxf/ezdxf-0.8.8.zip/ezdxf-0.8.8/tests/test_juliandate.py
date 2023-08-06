# Created: 21.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import sys
import pytest
from datetime import datetime

from ezdxf.tools.juliandate import juliandate, calendardate


class TestJulianDate:
    def test_1582_10_15(self):
        assert 2299161. == pytest.approx(juliandate(datetime(1582, 10, 15)))

    def test_1990_01_01(self):
        assert 2447893. == pytest.approx(juliandate(datetime(1990, 1, 1)))

    def test_2000_01_01(self):
        assert 2451545. == pytest.approx(juliandate(datetime(2000, 1, 1)))

    def test_2011_03_21(self):
        assert 2455642.75 == pytest.approx(juliandate(datetime(2011, 3, 21, 18, 0, 0)))

    def test_1999_12_31(self):
        assert 2451544.91568287 == pytest.approx(juliandate(datetime(1999, 12, 31, 21, 58, 35)))


@pytest.mark.skipif(sys.version_info < (3, 0), reason="usual pypy2 testing problem, I don't care.")
class TestCalendarDate:
    def test_1999_12_31(self):
        assert calendardate(2451544.91568288) == pytest.approx(datetime(1999, 12, 31, 21, 58, 35))

    def test_2011_03_21(self):
        assert calendardate(2455642.75) == pytest.approx(datetime(2011, 3, 21, 18, 0, 0))


