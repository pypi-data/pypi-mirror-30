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

        ssp.py : the Sonority Sequency Principle

                 cf https://en.wikipedia.org/wiki/Sonority_Sequencing_Principle
        ________________________________________________________________________

        see README.md for more documentation.
"""
import logging

LOGGER = logging.getLogger(__name__)

# confer John Laver, Principles of phonetics, p. 504
#
# SONORITY_DEGREES[source format][phoneme] = (int)value
#
# (doc)internal orthography for the different source formats:
# ˮ■  "heorot"
# ˮ    ■  x -> ks
# ˮ    ■  sc -> ʃ
# ˮ    ■  Sc -> Ʃ
# ˮ    ■  cg -> ç
# ˮ    ■  Cg -> Ç
# ˮ    ■  wr -> ρ
# ˮ    ■  Wr -> Ρ
# ˮ    ■  wl -> ɫ
# ˮ    ■  Wl -> Ɫ
# ˮ    ■  æg -> æġ
# ˮ    ■  eg -> eġ
# ˮ    ■  ég -> éġ
# ˮ    ■  ëg -> ëġ
# ˮ    ■  ig -> iġ
# ˮ    ■  íg -> íġ
# ˮ    ■  ïg -> ïġ
# ˮ    ■  yg -> yġ
# ˮ    ■  ýg -> ýġ
# ˮ    ■  ÿg -> ÿġ
SONORITY_DEGREES = {"heorot":
                    {"b": 0,  # stops
                     "B": 0,
                     "c": 0,
                     "C": 0,
                     "d": 0,
                     "D": 0,
                     "g": 0,
                     "G": 0,
                     "k": 0,
                     "K": 0,
                     "p": 0,
                     "P": 0,
                     "t": 0,
                     "T": 0,

                     "ç": 1,  # afficates
                     "Ç": 1,

                     "f": 2,  # fricatives
                     "F": 2,
                     "ð": 2,
                     "Ð": 2,
                     "þ": 2,
                     "Þ": 2,
                     "ʃ": 2,
                     "Ʃ": 2,
                     "s": 2,
                     "S": 2,
                     "h": 2,
                     "H": 2,

                     "m": 3,  # nasals
                     "M": 3,
                     "n": 3,
                     "N": 3,

                     "r": 4,  # liquids
                     "R": 4,
                     "ρ": 4,
                     "Ρ": 4,
                     "l": 4,
                     "L": 4,
                     "ɫ": 4,
                     "Ɫ": 4,

                     "ġ": 10,
                     "Ġ": 10,
                     "w": 10,  # glide (?)
                     "W": 10, }, }


def check_ssp(string, srcformat, ascend):
    """
        is <string> a list of phonemes coherent with the SSP ?

        ascend = True if sonority must increase, False it it must decrease.

        returned value : (bool)
    """
    if srcformat == "heorot":
        sonorities = SONORITY_DEGREES[srcformat]
    else:
        LOGGER.error("unknown source format '%s'", srcformat)

    res = True

    for i, char in enumerate(string):

        if i > 0:
            pre_char = string[i-1]

            if char not in sonorities:
                LOGGER.error("Don't know the sonority degree of '%s'.", char)
            if pre_char not in sonorities:
                LOGGER.error("Don't know the sonority degree of '%s'.", pre_char)

            if pre_char in ("s", "S") and i == 1:
                # a special case : the first "s" of a cluster of consonants violates
                # the SSP; e.g. "str" or "sp" is a valid cluster.
                pre_char_sonoritydegree = 0
            else:
                pre_char_sonoritydegree = sonorities[pre_char]

            char_sonoritydegree = sonorities[char]

            if ascend and pre_char_sonoritydegree > char_sonoritydegree:
                res = False
                break

            if not ascend and pre_char_sonoritydegree < char_sonoritydegree:
                res = False
                break

    return res
