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

        oetext.py, main file of the project
        ________________________________________________________________________

        see README.md for more documentation.
        ________________________________________________________________________

        o  OETextElement class
        o  OEText class
"""
import logging

from wordhord.utils import rm_dict_uppercase_dupli
from wordhord.utils import rm_strlist_uppercase_dupli
from wordhord.utils import complete_strlist_with_capitals
from wordhord.ssp import check_ssp
from wordhord.syllable import Syllable

LOGGER = logging.getLogger(__name__)


class OETextElement(object):
    """
        OETextElement class

        May contain either a syllable (self.syllable is a Syllable object) either a character
        (self.syllable=None, self.character=(str))
    """

    def __init__(self, syllable=None, character=None):
        """
                OETextElement.__init__()
        """
        if syllable is None:
            self.syllable = None
            self.character = character
        else:
            self.syllable = syllable
            self.character = ""

    def __str__(self):
        """
                OETextElement.__str__()
        """
        if self.is_a_syllable():
            return str(self.syllable)
        return self.character

    def get_pretty_repr(self):
        """
                OETextElement.get_pretty_repr()
        """
        if self.is_a_syllable():
            res = self.syllable.get_pretty_repr()
        else:
            res = self.character

        res = res.replace("\t", " ")
        res = res.replace("\n", "|")

        return res

    def is_a_character(self):
        """
                OETextElement.is_a_character()
        """
        return self.syllable is None

    def is_a_syllable(self):
        """
                OETextElement.is_a_syllable()
        """
        return self.syllable is not None


class OEText(object):
    """
        OEText class

        Read a text with the self.init_from_raw_text() and get the result in self.text .
    """

    def __init__(self):
        """
                OEText.__init__()
        """
        # text with an internal orthography :
        #
        #  you may want to access self.text through self.get_pretty_repr_of_the_text()
        #
        self.text = []

    def __str__(self):
        """
                OEText.__str__()
        """
        res = []

        for elem in self.text:
            res.append(str(elem))

        return "".join(res)

    def apply_internalortho_to_stats(self, stats, srcformat):
        """
                Inverse l'effet de ortho2internalortho() mais ne modifie que <stats>
        """

        # we don't apply this method to internal characters :
        # ---- internal characters --------------------------------------------
        # result = []
        # for char in stats["internal characters"]:
        #     result.append(self.internalortho2ortho(char, srcformat))
        # stats["internal characters"] = result

        # ---- missing vowels -------------------------------------------------
        result = dict()
        for vowel in stats["missing vowels"]:
            _vowel = self.internalortho2ortho(vowel, srcformat)
            result[_vowel] = stats["missing vowels"][vowel]
        stats["missing vowels"] = result

        # ---- missing consonants ---------------------------------------------
        result = dict()
        for consonant in stats["missing consonants"]:
            _consonant = self.internalortho2ortho(consonant, srcformat)
            result[_consonant] = stats["missing consonants"][consonant]
        stats["missing consonants"] = result

        # ---- alien characters ------------------------------------------
        result = []
        for char in stats["alien characters"]:
            result.append(self.internalortho2ortho(char, srcformat))
        stats["alien characters"] = result

        # ---- onsets ---------------------------------------------------------
        result = dict()
        for onset in stats["onsets"]:
            _onset = self.internalortho2ortho(onset, srcformat=srcformat)
            result[_onset] = (stats["onsets"][onset][0],
                              self.internalortho2ortho(stats["onsets"][onset][1],
                                                       srcformat=srcformat),
                              stats["onsets"][onset][2])
        stats["onsets"] = result

        # ---- nucleus ---------------------------------------------------------
        result = dict()
        for nucleus in stats["nucleus"]:
            _nucleus = self.internalortho2ortho(nucleus, srcformat=srcformat)
            result[_nucleus] = (stats["nucleus"][nucleus][0],
                                self.internalortho2ortho(stats["nucleus"][nucleus][1],
                                                         srcformat=srcformat),
                                stats["nucleus"][nucleus][1])
        stats["nucleus"] = result

        # ---- codas ---------------------------------------------------------
        result = dict()
        for coda in stats["codas"]:
            _coda = self.internalortho2ortho(coda, srcformat=srcformat)
            result[_coda] = (stats["codas"][coda][0],
                             self.internalortho2ortho(stats["codas"][coda][1],
                                                      srcformat=srcformat),
                             stats["codas"][coda][2])
        stats["codas"] = result

        # ---- missing onsets combinations ------------------------------------
        result = []
        for char in stats["missing onsets combinations"]:
            result.append(self.internalortho2ortho(char, srcformat))
        stats["missing onsets combinations"] = result

        # ---- missing nucleuss combinations ------------------------------------
        result = []
        for char in stats["missing nucleus combinations"]:
            result.append(self.internalortho2ortho(char, srcformat))
        stats["missing nucleus combinations"] = result

        return stats

    def balance_last_syllable(self, onsets_combinations):
        """
                OEText.balance_last_syllable()

                balance self.text[-1] and self.text[-2]

                some characters in self.text[-2].coda are moved into self.text[-1].onset

                e.g. "mon.e" → "mo.ne"
        """
        if len(self.text) <= 1:
            return

        if self.text[-1].syllable is None:
            return

        if self.text[-2].syllable is None:
            return

        buff = ""
        for char in self.text[-2].syllable.coda[::-1]:
            if char + buff + self.text[-1].syllable.onset in onsets_combinations:
                buff = char + buff
            else:
                break

        if buff:
            self.text[-1].syllable.onset = buff + self.text[-1].syllable.onset
            self.text[-2].syllable.coda = self.text[-2].syllable.coda[:-len(buff)]

    def check_syllables(self):
        """
                OEText.check_syllables()

                Return True if all syllables are normal, False otherwise
                        * test : is the nucleus non empty ?
        """
        # test : is the nucleus non empty ?
        for i, elem in enumerate(self.text):
            if elem.is_a_syllable() and not elem.syllable.is_ok():
                LOGGER.error("Ill-formed syllable (no nucleus) : %s; context=%s",
                             elem,
                             self.get_context_around(i))

    def complete_statistics(self,
                            stats,
                            onsets_combinations,
                            nucleus_combinations,
                            srcformat):
        """
                OEText.complete_statistics()

                Complete the current statistics during a call to init_from_raw_text()

                This method needs statistics["internal characters"] and self.texts .
        """
        stats["internal characters"] = sorted(stats["internal characters"])

        # onsets' occurences:
        stats["onsets"] = dict()
        for i, elem in enumerate(self.text):
            if elem.is_a_syllable() and elem.syllable.onset not in stats["onsets"]:
                context = self.get_context_around(i)
                suffix = ""
                if not check_ssp(string=elem.syllable.onset,
                                 srcformat=srcformat,
                                 ascend=True):
                    suffix = " (!SSP!)"
                stats["onsets"][elem.syllable.onset] = [1, context, suffix]
            elif elem.is_a_syllable() and elem.syllable.onset in stats["onsets"]:
                stats["onsets"][elem.syllable.onset][0] += 1

        # nucleus' occurences:
        stats["nucleus"] = dict()
        for i, elem in enumerate(self.text):
            if elem.is_a_syllable() and elem.syllable.nucleus not in stats["nucleus"]:
                context = self.get_context_around(i)
                stats["nucleus"][elem.syllable.nucleus] = [1, context, ""]
            elif elem.is_a_syllable() and elem.syllable.nucleus in stats["nucleus"]:
                stats["nucleus"][elem.syllable.nucleus][0] += 1

        # codas' occurences:
        stats["codas"] = dict()
        for i, elem in enumerate(self.text):
            if elem.is_a_syllable() and elem.syllable.coda not in stats["codas"]:
                context = self.get_context_around(i)
                suffix = ""
                if not check_ssp(string=elem.syllable.coda,
                                 srcformat=srcformat,
                                 ascend=False):
                    suffix = " (!SSP!)"
                stats["codas"][elem.syllable.coda] = [1, context, suffix]
            elif elem.is_a_syllable() and elem.syllable.coda in stats["codas"]:
                stats["codas"][elem.syllable.coda][0] += 1

        # missing onsets combinations:
        stats["missing onsets combinations"] = []
        for onsets_combination in onsets_combinations:
            found = False
            for elem in self.text:
                if elem.is_a_syllable() and elem.syllable.onset == onsets_combination:
                    found = True

            if not found:
                stats["missing onsets combinations"].append(onsets_combination)

        # missing nucleus combinations:
        stats["missing nucleus combinations"] = []
        for nucleus_combination in nucleus_combinations:
            found = False
            for elem in self.text:
                if elem.is_a_syllable() and elem.syllable.nucleus == nucleus_combination:
                    found = True

            if not found:
                stats["missing nucleus combinations"].append(nucleus_combination)

        return stats

    def delete_text_empty_syllables(self):
        """
                OEText.delete_text_empty_syllables()
        """
        res = []

        for elem in self.text:
            if elem.is_a_syllable() and elem.syllable.is_empty():
                pass
            else:
                res.append(elem)

        self.text = res

    def get_context_around(self, index):
        """
                OEText.get_context_around()

                Return a string, what's lie just before/after self.text[index]
        """
        res = []

        if index > 0 and self.text:
            res.append("…")

        for pos in range(index-10, index+10):
            if pos >= 0 and pos < len(self.text):
                res.append(self.text[pos].get_pretty_repr())

        if index < len(self.text)-1 and self.text:
            res.append("…")

        return "".join(res)

    def get_pretty_repr_of_the_text(self,
                                    srcformat,
                                    symbol_between_two_syllables="*"):
        """
                OEText.get_pretty_repr_of_the_text()

                Apply self.internalortho2ortho()
        """
        res = []

        for elem in self.text:
            if not elem.is_a_syllable():
                res.append(elem.get_pretty_repr())
            else:
                res.append(self.internalortho2ortho(string=elem.get_pretty_repr(),
                                                    srcformat=srcformat))

        return symbol_between_two_syllables.join(res)

    @staticmethod
    def get_src_characters(srcformat):
        """
                OEText.get_src_characters()

                RETURNED VALUE : (consonants, vowels, onsets_combinations, nucleus_combinations)

                (doc)internal orthograph for the different source formats:
                ˮ■  "heorot"
                ˮ    ■  x → ks
                ˮ    ■  sc → ʃ
                ˮ    ■  Sc → Ʃ
                ˮ    ■  cg → ç
                ˮ    ■  Cg → Ç
                ˮ    ■  wr → ρ
                ˮ    ■  Wr → Ρ
                ˮ    ■  wl → ɫ
                ˮ    ■  Wl → Ɫ
                ˮ    ■  æg → æġ
                ˮ    ■  eg → eġ
                ˮ    ■  ég → éġ
                ˮ    ■  ëg → ëġ
                ˮ    ■  ig → iġ
                ˮ    ■  íg → íġ
                ˮ    ■  ïg → ïġ
                ˮ    ■  yg → yġ
                ˮ    ■  ýg → ýġ
                ˮ    ■  ÿg → ÿġ
        """
        if srcformat == "heorot":
            # confer https://en.wikipedia.org/wiki/Old_English_phonology#Onset
            onsets_combinations =\
                ("p", "pr", "pl",
                 "b", "br", "bl",
                 "t", "tr", "tw",
                 "d", "dr", "dw",
                 "c", "cn", "cr", "cl", "cw",
                 "k", "kn", "kr", "kl", "kw",
                 "g", "gn", "gr", "gl",
                 "s", "sm", "sn", "sl", "sw", "sp", "spr", "spl", "st", "str", "sks", "skr",
                 "ʃ", "ʃr",
                 "f", "fn", "fr", "fl",
                 "þ", "þr", "þw",
                 "ð", "ðr", "ðw",
                 "h", "hn", "hr", "hl", "hw",
                 "m",
                 "n",
                 "l",
                 "r",
                 "w",
                 "ġ",
                 "ç",
                 "ρ",
                 "ɫ",)
            onsets_combinations = complete_strlist_with_capitals(onsets_combinations)

            nucleus_combinations = ("a", "á", "ä",
                                    "æ",  # "ǽ" = aé
                                    "e", "é", "ë",
                                    "i", "í",  # no "ï"
                                    "o", "ó", "ö",
                                    "u", "ú",  # no "ü"
                                    "y", "ý", "ÿ",
                                    "aé",
                                    "io", "ío",
                                    "eo", "éo",
                                    "ea", "éa",)
            nucleus_combinations = complete_strlist_with_capitals(nucleus_combinations)

            # nota bene : "Ġ" doesn't exist for srcformat=="heorot"
            consonants = "bcdfghklmnprstwþðçʃɫġρɫ" + "BCDFGHKLMNPRSTWÞÐÇƩⱢΡⱢ"
            vowels = "aAáÁäÄæÆeEéÉëËiIíÍïÏoOóÓöÖuUúÚÜüyYýÝÿŸ"
        else:
            LOGGER.error("unknown source format '%s'", srcformat)

        return consonants, vowels, onsets_combinations, nucleus_combinations

    def get_total_nbr_of_syllables(self):
        """
                OEText.get_total_nbr_of_syllables()
        """
        res = 0

        for elem in self.text:
            if elem.is_a_syllable():
                res += 1

        return res

    @staticmethod
    def improve_results(stats, improve_results):
        """
                OEText.improve_results()

                (doc)improve_results:
                ˮ■  "onsets::remove uppercase keys duplicate":
                ˮ    if True, remove from statistics["onsets"] every <onset>
                ˮ    if lowercase(onset) is already in statistics["onsets"].
                ˮ
                ˮ■  "nucleus::remove uppercase keys duplicate":
                ˮ    if True, remove from statistics["nucleus"] every <nucleus>
                ˮ    if lowercase(nucleus) is already in statistics["nucleus"].
                ˮ
                ˮ■  "codas::remove uppercase keys duplicate":
                ˮ    if True, remove from statistics["codas"] every <coda> if lowercase(coda)
                ˮ    is already in statistics["codas"].
                ˮ
                ˮ■  "missing onsets combinations::remove uppercase keys duplicate":
                ˮ    if True, remove from statistics["missing onsets combinations"] every <onset>
                ˮ    if lowercase(onset) is already in statistics["missing onsets combinations"].
                ˮ
                ˮ■  "missing onsets combinations::remove if lowercase key is in onset":
                ˮ    if True, remove from statistics["missing onsets"] every <onset>
                ˮ    if lowercase(onset) is already in statistics["onset"]
                ˮ
                ˮ■  "missing nucleus combinations::remove if lowercase key is in nucleus":
                ˮ    if True, remove from statistics["missing nucleus"] every <nucleus>>
                ˮ    if lowercase(nucleus) is already in statistics["nucleus"]
        """
        if improve_results["onsets::remove uppercase keys duplicate"]:
            stats["onsets"] = rm_dict_uppercase_dupli(stats["onsets"])

        if improve_results["nucleus::remove uppercase keys duplicate"]:
            stats["nucleus"] = rm_dict_uppercase_dupli(stats["nucleus"])

        if improve_results["codas::remove uppercase keys duplicate"]:
            stats["codas"] = rm_dict_uppercase_dupli(stats["codas"])

        if improve_results["missing onsets combinations::remove uppercase keys duplicate"]:
            stats["missing onsets combinations"] =\
                    rm_strlist_uppercase_dupli(stats["missing onsets combinations"])

        if improve_results["missing onsets combinations::remove if lowercase key is in onset"]:
            res = []
            for missing_value in stats["missing onsets combinations"]:
                if missing_value.lower() not in stats["onsets"]:
                    res.append(missing_value)
            stats["missing onsets combinations"] = res

        if improve_results["missing nucleus combinations::remove if lowercase key is in nucleus"]:
            res = []
            for missing_value in stats["missing nucleus combinations"]:
                if missing_value.lower() not in stats["nucleus"]:
                    res.append(missing_value)
            stats["missing nucleus combinations"] = res

        return stats

    def init_from_raw_text(self, raw_src, srcformat):
        """
                OEText.init_from_raw_text()
        """
        (consonants,
         vowels,
         onsets_combinations,
         nucleus_combinations) = self.get_src_characters(srcformat)

        #  will be completed by a call to self.complete_statistics()
        stats = {"internal characters": set(),
                 "alien characters": set(),
                 "missing vowels": dict((vowel, True) for vowel in vowels),
                 "missing consonants": dict((consonant, True) for consonant in consonants), }

        self.text.clear()
        self.text.append(OETextElement(syllable=Syllable()))

        source = self.ortho2internalortho(raw_src, srcformat)

        for char in source:
            stats["internal characters"].add(char)

            if char in vowels:
                stats["missing vowels"][char] = False
            if char in consonants:
                stats["missing consonants"][char] = False

            if char not in vowels and char not in consonants:
                stats["alien characters"].add(char)
                self.text.append(OETextElement(character=char))

            elif self.text[-1].is_a_character():
                if char in vowels:
                    self.text.append(OETextElement(syllable=Syllable(nucleus=char)))
                else:
                    self.text.append(OETextElement(syllable=Syllable(onset=char)))

            elif self.text[-1].is_a_syllable():
                if char in vowels and self.text[-1].syllable.coda == "":
                    if self.text[-1].syllable.nucleus + char in nucleus_combinations:
                        self.text[-1].syllable.nucleus += char
                    else:
                        self.text.append(OETextElement(syllable=Syllable(nucleus=char)))

                elif char in vowels and self.text[-1].syllable.coda != "":
                    self.text.append(OETextElement(syllable=Syllable(nucleus=char)))

                elif char in consonants and self.text[-1].syllable.nucleus == "":
                    self.text[-1].syllable.onset += char

                    if self.text[-1].syllable.onset not in onsets_combinations:
                        LOGGER.error("Anomaly : unexpected onset in syllable %s; context=%s",
                                     self.text[-1].syllable,
                                     self.get_context_around(len(self.text)-1))

                elif char in consonants and self.text[-1].syllable.nucleus != "":
                    self.text[-1].syllable.coda += char

            self.balance_last_syllable(onsets_combinations)

        self.delete_text_empty_syllables()
        self.check_syllables()

        # statistics :
        stats = self.complete_statistics(stats,
                                         onsets_combinations,
                                         nucleus_combinations,
                                         srcformat)

        stats = self.apply_internalortho_to_stats(stats, srcformat)

        return self, stats

    @staticmethod
    def internalortho2ortho(string, srcformat):
        """
                inverse of self.ortho2internalortho()

                (doc)internal orthograph for the different source formats:
                ˮ■  "heorot"
                ˮ    ■  x → ks
                ˮ    ■  sc → ʃ
                ˮ    ■  Sc → Ʃ
                ˮ    ■  cg → ç
                ˮ    ■  Cg → Ç
                ˮ    ■  wr → ρ
                ˮ    ■  Wr → Ρ
                ˮ    ■  wl → ɫ
                ˮ    ■  Wl → Ɫ
                ˮ    ■  æg → æġ
                ˮ    ■  eg → eġ
                ˮ    ■  ég → éġ
                ˮ    ■  ëg → ëġ
                ˮ    ■  ig → iġ
                ˮ    ■  íg → íġ
                ˮ    ■  ïg → ïġ
                ˮ    ■  yg → yġ
                ˮ    ■  ýg → ýġ
                ˮ    ■  ÿg → ÿġ
        """
        if srcformat == "heorot":
            string = string.replace("ġ", "g")

            string = string.replace("ks", "x")
            string = string.replace("ʃ", "sc")
            string = string.replace("Ʃ", "Sc")
            string = string.replace("ç", "cg")
            string = string.replace("Ç", "Cg")
            string = string.replace("ρ", "wr")
            string = string.replace("Ρ", "Wr")
            string = string.replace("ɫ", "wl")
            string = string.replace("Ɫ", "Wl")
        else:
            LOGGER.error("unknown source format '%s'", srcformat)

        return string

    @staticmethod
    def ortho2internalortho(string, srcformat):
        """
                Modify <string> along <srcformat> : ortho to internal ortho.

                inverse of self.internalortho2ortho()

                (doc)internal orthograph for the different source formats:
                ˮ■  "heorot"
                ˮ    ■  x → ks
                ˮ    ■  sc → ʃ
                ˮ    ■  Sc → Ʃ
                ˮ    ■  cg → ç
                ˮ    ■  Cg → Ç
                ˮ    ■  wr → ρ
                ˮ    ■  Wr → Ρ
                ˮ    ■  wl → ɫ
                ˮ    ■  Wl → Ɫ
                ˮ    ■  æg → æġ
                ˮ    ■  eg → eġ
                ˮ    ■  ég → éġ
                ˮ    ■  ëg → ëġ
                ˮ    ■  ig → iġ
                ˮ    ■  íg → íġ
                ˮ    ■  ïg → ïġ
                ˮ    ■  yg → yġ
                ˮ    ■  ýg → ýġ
                ˮ    ■  ÿg → ÿġ
        """
        string = string.replace("æg", "æġ")

        string = string.replace("eg", "eġ")
        string = string.replace("ég", "éġ")
        string = string.replace("ëg", "ëġ")

        string = string.replace("ig", "iġ")
        string = string.replace("íg", "íġ")
        string = string.replace("ïg", "ïġ")

        string = string.replace("yg", "yġ")
        string = string.replace("ýg", "ýġ")
        string = string.replace("ÿg", "ÿġ")

        if srcformat == "heorot":
            string = string.replace("x", "ks")
            string = string.replace("sc", "ʃ")
            string = string.replace("Sc", "Ʃ")
            string = string.replace("cg", "ç")
            string = string.replace("Cg", "Ç")
            string = string.replace("wr", "ρ")
            string = string.replace("Wr", "Ρ")
            string = string.replace("wl", "ɫ")
            string = string.replace("Wl", "Ɫ")
        else:
            LOGGER.error("unknown source format '%s'", srcformat)

        return string

    def reshape_statistics_cli(self,
                               stats,
                               improve_results):
        """
                Format the statistics returned by self.init_from_raw_text() .
                Console output

                (doc)improve_results:
                ˮ■  "onsets::remove uppercase keys duplicate":
                ˮ    if True, remove from statistics["onsets"] every <onset>
                ˮ    if lowercase(onset) is already in statistics["onsets"].
                ˮ
                ˮ■  "nucleus::remove uppercase keys duplicate":
                ˮ    if True, remove from statistics["nucleus"] every <nucleus>
                ˮ    if lowercase(nucleus) is already in statistics["nucleus"].
                ˮ
                ˮ■  "codas::remove uppercase keys duplicate":
                ˮ    if True, remove from statistics["codas"] every <coda> if lowercase(coda)
                ˮ    is already in statistics["codas"].
                ˮ
                ˮ■  "missing onsets combinations::remove uppercase keys duplicate":
                ˮ    if True, remove from statistics["missing onsets combinations"] every <onset>
                ˮ    if lowercase(onset) is already in statistics["missing onsets combinations"].
                ˮ
                ˮ■  "missing onsets combinations::remove if lowercase key is in onset":
                ˮ    if True, remove from statistics["missing onsets"] every <onset>
                ˮ    if lowercase(onset) is already in statistics["onset"]
                ˮ
                ˮ■  "missing nucleus combinations::remove if lowercase key is in nucleus":
                ˮ    if True, remove from statistics["missing nucleus"] every <nucleus>>
                ˮ    if lowercase(nucleus) is already in statistics["nucleus"]
        """
        res = []  # will be "\n".join()
        total_nbr_of_syllables = self.get_total_nbr_of_syllables()

        stats = self.improve_results(stats, improve_results)

        # ---- internal characters --------------------------------------------
        res.append("▶ internal characters: " +
                   "; ".join(repr(char) for char in stats["internal characters"]))

        # ---- alien characters ------------------------------------------
        res.append("▶ alien characters: " +
                   "; ".join(repr(char) for char in stats["alien characters"]))

        # ---- missing vowels -------------------------------------------------
        missing_vowels = "; ".join(vowel for vowel in stats["missing vowels"]
                                   if stats["missing vowels"][vowel])
        res.append("▶ missing vowels: " + missing_vowels)

        # ---- missing consonants ---------------------------------------------
        missing_consonants = "; ".join(consonant for consonant in stats["missing consonants"]
                                       if stats["missing consonants"][consonant])
        res.append("▶ missing consonants: " + missing_consonants)

        # ---- missing onsets combinations ------------------------------------
        res.append("▶ missing onsets combinations: " +
                   "; ".join(repr(char) for char in stats["missing onsets combinations"]))

        # ---- missing nucleus combinations ------------------------------------
        res.append("▶ missing nucleus combinations: " +
                   "; ".join(repr(char) for char in stats["missing nucleus combinations"]))

        # ---- onsets ---------------------------------------------------------
        res.append("▶ onsets:")
        for onset in sorted(stats["onsets"],
                            key=lambda item: stats["onsets"][item][0],
                            reverse=True):

            if total_nbr_of_syllables != 0:
                freq = 100*stats["onsets"][onset][0]/total_nbr_of_syllables
            else:
                freq = 0

            res.append("   '{0}' : ({1:.3}%) \"{2}\"{3}".format(onset,
                                                                freq,
                                                                stats["onsets"][onset][1],
                                                                stats["onsets"][onset][2]))

        # ---- nucleus --------------------------------------------------------
        res.append("▶ nucleus:")
        for nucleus in sorted(stats["nucleus"],
                              key=lambda item: stats["nucleus"][item][0],
                              reverse=True):

            if total_nbr_of_syllables != 0:
                freq = 100*stats["nucleus"][nucleus][0]/total_nbr_of_syllables
            else:
                freq = 0

            res.append("   '{0}' : ({1:.3}%) \"{2}\"{3}".format(nucleus,
                                                                freq,
                                                                stats["nucleus"][nucleus][1],
                                                                stats["nucleus"][nucleus][2]))

        # ---- codas ----------------------------------------------------------
        res.append("▶ codas:")
        for coda in sorted(stats["codas"],
                           key=lambda item: stats["codas"][item][0],
                           reverse=True):

            if total_nbr_of_syllables != 0:
                freq = 100*stats["codas"][coda][0]/total_nbr_of_syllables
            else:
                freq = 0

            res.append("   '{0}' : ({1:.3}%) \"{2}\"{3}".format(coda,
                                                                freq,
                                                                stats["codas"][coda][1],
                                                                stats["codas"][coda][2]))

        return "\n".join(res)

    def reshape_statistics_md(self,
                              stats,
                              improve_results):
        """
                Format the statistics returned by self.init_from_raw_text() .
                Markdown output

                (doc)improve_results:
                ˮ■  "onsets::remove uppercase keys duplicate":
                ˮ    if True, remove from statistics["onsets"] every <onset>
                ˮ    if lowercase(onset) is already in statistics["onsets"].
                ˮ
                ˮ■  "nucleus::remove uppercase keys duplicate":
                ˮ    if True, remove from statistics["nucleus"] every <nucleus>
                ˮ    if lowercase(nucleus) is already in statistics["nucleus"].
                ˮ
                ˮ■  "codas::remove uppercase keys duplicate":
                ˮ    if True, remove from statistics["codas"] every <coda> if lowercase(coda)
                ˮ    is already in statistics["codas"].
                ˮ
                ˮ■  "missing onsets combinations::remove uppercase keys duplicate":
                ˮ    if True, remove from statistics["missing onsets combinations"] every <onset>
                ˮ    if lowercase(onset) is already in statistics["missing onsets combinations"].
                ˮ
                ˮ■  "missing onsets combinations::remove if lowercase key is in onset":
                ˮ    if True, remove from statistics["missing onsets"] every <onset>
                ˮ    if lowercase(onset) is already in statistics["onset"]
                ˮ
                ˮ■  "missing nucleus combinations::remove if lowercase key is in nucleus":
                ˮ    if True, remove from statistics["missing nucleus"] every <nucleus>>
                ˮ    if lowercase(nucleus) is already in statistics["nucleus"]
        """
        res = []  # will be "\n".join()
        total_nbr_of_syllables = self.get_total_nbr_of_syllables()

        stats = self.improve_results(stats, improve_results)

        res.append("# miscellaneous:")
        res.append("----")

        # ---- internal characters --------------------------------------------
        res.append("## internal characters: ")
        res.append("> " + "; ".join(repr(char) for char in stats["internal characters"]))
        res.append("")
        res.append("----")

        # ---- alien characters ------------------------------------------
        res.append("## alien characters: ")
        res.append("> " + "; ".join(repr(char) for char in stats["alien characters"]))
        res.append("")
        res.append("----")

        # ---- missing onsets combinations ------------------------------------
        res.append("## missing onsets combinations: ")
        res.append("> " + "; ".join(repr(char) for char in stats["missing onsets combinations"]))
        res.append("")
        res.append("----")

        # ---- missing nucleus combinations ------------------------------------
        res.append("## missing nucleus combinations:")
        res.append("> " + "; ".join(repr(char) for char in stats["missing nucleus combinations"]))
        res.append("")
        res.append("----")

        res.append("# syllables:")
        res.append("----")

        # ---- onsets ---------------------------------------------------------
        res.append("## onsets:")
        for onset in sorted(stats["onsets"],
                            key=lambda item: stats["onsets"][item][0],
                            reverse=True):

            if total_nbr_of_syllables != 0:
                freq = 100*stats["onsets"][onset][0]/total_nbr_of_syllables
            else:
                freq = 0

            res.append("* '{0}' : ({1:.3}%) \"{2}\"{3}".format(onset,
                                                               freq,
                                                               stats["onsets"][onset][1],
                                                               stats["onsets"][onset][2]))
        res.append("----")

        # ---- nucleus --------------------------------------------------------
        res.append("## nucleus:")
        for nucleus in sorted(stats["nucleus"],
                              key=lambda item: stats["nucleus"][item][0],
                              reverse=True):

            if total_nbr_of_syllables != 0:
                freq = 100*stats["nucleus"][nucleus][0]/total_nbr_of_syllables
            else:
                freq = 0

            res.append("* '{0}' : ({1:.3}%) \"{2}\"{3}".format(nucleus,
                                                               freq,
                                                               stats["nucleus"][nucleus][1],
                                                               stats["nucleus"][nucleus][2]))

        res.append("----")

        # ---- codas ----------------------------------------------------------
        res.append("## codas:")
        for coda in sorted(stats["codas"],
                           key=lambda item: stats["codas"][item][0],
                           reverse=True):

            if total_nbr_of_syllables != 0:
                freq = 100*stats["codas"][coda][0]/total_nbr_of_syllables
            else:
                freq = 0

            res.append("* '{0}' : ({1:.3}%) \"{2}\"{3}".format(coda,
                                                               freq,
                                                               stats["codas"][coda][1],
                                                               stats["codas"][coda][2],))

        res.append("----")

        return "\n".join(res)
