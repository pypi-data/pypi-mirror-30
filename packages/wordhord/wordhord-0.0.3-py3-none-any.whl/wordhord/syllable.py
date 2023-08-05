#!/usr/bin/env python3
# -*- coding: utf-8 -*-
################################################################################
#    wordhord Copyright (C) 2018 Suizokukan
#    Contact: suizokukan _A.T._ orange dot fr
#
#    This file is part of wordhord.
#    wordhord is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    wordhord is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with wordhord.  If not, see <http://www.gnu.org/licenses/>.
################################################################################
"""
        wordhord by suizokukan (suizokukan AT orange DOT fr)

        Toolbox for the analyse Old English texts.
        ________________________________________________________________________

        syllable.py : everything about syllable as onset, nucleus and coda.
        ________________________________________________________________________

        see README.md for more documentation.
        ________________________________________________________________________

        o class Syllable
"""

# ==============================================================================
# project's settings
#
# o for __version__ format string, see https://www.python.org/dev/peps/pep-0440/ :
#   e.g. "0.1.2.dev1" or "0.1a"
#
# o See also https://pypi.python.org/pypi?%3Aaction=list_classifiers
#
# ==============================================================================


class Syllable(object):
    """
        Syllable class

        Use it to store the (onset, nucleus, coda) of a syllable.
    """

    def __init__(self, onset="", nucleus="", coda=""):
        """
                Syllable.__init__()
        """
        self.onset = onset
        self.nucleus = nucleus
        self.coda = coda

    def __str__(self):
        """
                Syllable.__str__()
        """
        return "{{ '{0}'; '{1}'; '{2}'; }}".format(self.onset, self.nucleus, self.coda)

    def get_pretty_repr(self):
        """
                Syllable.get_pretty_repr()
        """
        return self.onset + self.nucleus + self.coda

    def is_empty(self):
        """
                Syllable.is_empty()
        """
        return self.onset == "" and self.nucleus == "" and self.coda == ""

    def is_ok(self):
        """
                Syllable.is_ok()
        """
        if self.nucleus == "":
            return False

        return True
