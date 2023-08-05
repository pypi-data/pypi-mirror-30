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

        utils.py
        ________________________________________________________________________

        see README.md for more documentation.
        ________________________________________________________________________
        ________________________________________________________________________
"""


def complete_strlist_with_capitals(src):
    """
            src := ('k', 'kl', 'klo')  -> ('k', 'kl', 'klo', 'K', 'Kl', 'Klo')
    """
    res = []

    for elem in src:
        res.append(elem)
        res.append(elem.capitalize())

    return res


def rm_dict_uppercase_dupli(src):
    """
                rm_dict_uppercase_dupli()

                remove each <key> from the dict <src> if <key.lowercase()>
                already exist in <src>.

                { "a" : "a_value, "A" : "A_value", "c" : "c_value" }
                        -> { "a" : "a_value, "c" : "c_value" }
    """
    res = dict()

    for key, value in src.items():
        if key.lower() != key and key.lower() in src:
            pass
        else:
            res[key] = value

    return res


def rm_strlist_uppercase_dupli(src):
    """
        rm_strlist_uppercase_dupli()

        ['a', 'A', 'b'] -> ['a', 'b']
    """
    res = []

    for elem in src:
        if elem.lower() != elem and elem.lower() in src:
            pass
        else:
            res.append(elem)

    return res
