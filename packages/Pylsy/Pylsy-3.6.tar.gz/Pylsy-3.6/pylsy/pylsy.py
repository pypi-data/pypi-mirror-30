#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Pylsy Authors
# For a full list of authors, see the AUTHORS file at
# https://github.com/Leviathan1995/Pylsy/blob/master/AUTHORS.
# @license MIT
from __future__ import print_function
from wcwidth import wcwidth


class pylsytable(object):

    def __init__(self, attributes):
        """Creates a new PylsyTable object with the given attrs (cols)."""
        self.StrTable = ""
        self.Table = []
        self.AttributesLength = []
        self.Lines_num = 0
        if type(attributes) != list:
            attributes = [attributes]
        self.Attributes = [u"{0}".format(attr) for attr in attributes]
        self.Cols_num = len(self.Attributes)
        for attribute in self.Attributes:
            col = dict()
            col[attribute] = []
            self.Table.append(col)

    def _print_divide(self):
        """Prints all those table line dividers."""
        for space in self.AttributesLength:
            self.StrTable += "+ " + "- " * space
        self.StrTable += "+"+"\n"

    def append_data(self, attribute, values):
        """Appends the given value(s) to the attribute (column)."""
        found = False
        if type(values) != list:
            values = [values]
        for col in self.Table:
            if attribute in col:
                dict_values = [u"{0}".format(value) for value in values]
                col[attribute] += dict_values
                found = True
        if not found:
            raise KeyError(attribute)

    def add_data(self, attribute, values):
        """Sets the given values for the attribute (column)."""
        found = False
        if type(values) != list:
            values = [values]
        for col in self.Table:
            if attribute in col:
                dict_values = [u"{0}".format(value) for value in values]
                col[attribute] = dict_values
                found = True
        if not found:
            raise KeyError(attribute)

    def _create_table(self):
        """
        Creates a pretty-printed string representation of the table as
        ``self.StrTable``.
        """
        self.StrTable = ""
        self.AttributesLength = []
        self.Lines_num = 0
        # Prepare some values..
        for col in self.Table:
            # Updates the table line count if necessary
            values = list(col.values())[0]
            self.Lines_num = max(self.Lines_num, len(values))
            # find the length of longest value in current column
            key_length = max([self._disp_width(v) for v in values] or [0])
            # and also the table header
            key_length = max(key_length, self._disp_width(list(col.keys())[0]))
            self.AttributesLength.append(key_length)
        # Do the real thing.
        self._print_head()
        self._print_value()

    def _print_head(self):
        """Generates the table header."""
        self._print_divide()
        self.StrTable += "| "
        for colwidth, attr in zip(self.AttributesLength, self.Attributes):
            self.StrTable += self._pad_string(attr, colwidth * 2)
            self.StrTable += "| "
        self.StrTable += '\n'
        self._print_divide()

    def _print_value(self):
        """Generates the table values."""
        for line in range(self.Lines_num):
            for col, length in zip(self.Table, self.AttributesLength):
                vals = list(col.values())[0]
                val = vals[line] if len(vals) != 0 and line < len(vals) else ''
                self.StrTable += "| "
                self.StrTable += self._pad_string(val, length * 2)
            self.StrTable += "|"+'\n'
            self._print_divide()

    def _disp_width(self, pwcs, n=None):
        """
        A wcswidth that never gives -1. Copying existing code is evil, but..

        github.com/jquast/wcwidth/blob/07cea7f/wcwidth/wcwidth.py#L182-L204
        """
        # pylint: disable=C0103
        #         Invalid argument name "n"
        # TODO: Shall we consider things like ANSI escape seqs here?
        #       We can implement some ignore-me segment like those wrapped by
        #       \1 and \2 in readline too.
        end = len(pwcs) if n is None else n
        idx = slice(0, end)
        width = 0
        for char in pwcs[idx]:
            width += max(0, wcwidth(char))
        return width

    def _pad_string(self, str, colwidth):
        """Center-pads a string to the given column width using spaces."""
        width = self._disp_width(str)
        prefix = (colwidth - 1 - width) // 2
        suffix = colwidth - prefix - width
        return ' ' * prefix + str + ' ' * suffix

    def __str__(self):
        """Returns a pretty-printed string representation of the table."""
        self._create_table()
        return self.StrTable
