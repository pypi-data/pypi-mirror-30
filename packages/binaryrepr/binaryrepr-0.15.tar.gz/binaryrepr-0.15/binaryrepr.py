#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File: binaryrepr.py
Author: David LAMOULLER
Email: dlamouller@protonmail.com
Github: https://github.com/dlamouller
Description: binaryrep is a utility to display position of the bits of a number.
"""

from __future__ import unicode_literals
import sys
from math import log
from operator import itemgetter
import click
import prettytable as pt

#option fo click
click.disable_unicode_literals_warning = True
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


class BaseDepiction(object):
    """BaseDepiction"""

    def __init__(self, x, alldecimal, type_rep="bin", outformat="basic", short_repr=False, header=True):
        super(BaseDepiction, self).__init__()
        self.table = pt.PrettyTable()
        self.x = x[0]
        self.base = x[1]
        self.power = dict(hex=4, oct=3).get(type_rep, 1)
        self.outformat = outformat
        self.table.header = header
        self.table.hrules = pt.ALL
        if self.outformat == "gfm":
            self.table.junction_char = "|"
        elif self.outformat == "nohrules":
            self.table.hrules = pt.NONE
        elif self.outformat == "noline":
            self.table.border = False
            self.table.hrules = pt.NONE
            self.outformat = {"border" : False,
                              "header" : True,
                              "junction_char" : "+",
                              "hrules" : pt.NONE}
        self.depth = 7
        for deep in filter(lambda e: round(log(self.x, 2) + 0.5) <= e, [8, 16, 32, 64, 128]):
            self.depth = deep
            break
        if self.power == 4:
            self.x = format(self.x, 'x')
        elif self.power == 3:
            self.x = format(self.x, 'o')
        else:
            self.x = format(self.x, 'b')

        if not short_repr:
            self.x = int((self.depth/self.power - len(self.x) + 1)) * "0" + self.x
        if sys.byteorder == "little":
            nbbits = [i * self.power for i in range(len(self.x) -1, -1, -1)]
        else:
            nbbits = [i * self.power for i in range(len(self.x) -1)]
        self.position = list(map(str, nbbits))
        self.x = list(self.x)
        self.position.insert(0, "value")
        self.x.insert(0, format(x[0], self.base))
        if not alldecimal:
            self.position.insert(0, "value dec")
            self.x.insert(0, format(x[0], 'd'))
        self.table.field_names = self.position

    def __repr__(self):
        sout = self.table.get_string()
        if self.outformat == "gfm": #don't know how to set for gfm format
            sout = sout.split("\n")
            sout = "\n".join(sout[1:-1])
        return sout

    def __add__(self, other):
        if other.depth != self.depth:
            pad = len(self.x) - len(other.x)
            while pad > 0:
                other.x.insert(1, "0")
                pad -= 1
        self.table.add_row(other.x)
        return self.table.get_string()

    def add_row(self):
        "add a new row"
        self.table.add_row(self.x)


@click.command(context_settings=CONTEXT_SETTINGS,
               help="""representation of a number in binary, hexadecimal or oct according to your
               system byteorder""")
@click.option("-t", "--type_repr",
              default="bin",
              type=click.Choice(['bin', 'hex', 'oct']),
              help="type of representation of number, binary by default")
@click.option("-f", "--outformat",
              default="basic",
              type=click.Choice(['noline', 'gfm', 'basic', 'nohrules']),
              help="outpout format representation. basic by default")
@click.option("-s", "--short", count=True, help="short representation")
@click.argument("value", nargs=-1, type=click.STRING)
def binaryrepr(value, type_repr, outformat, short):
    "display number in binary, hexadecimal or oct in a human readable view"
    convert = lambda x: (int(x, 16), 'x') if x.startswith('0x') else ((int(x, 2), 'b')\
            if x.startswith('0b') else ((int(x, 8), 'o') if x.startswith('0') else (int(x), 'd')))
    values = list(map(convert, value))
    alldecimal = all(y == 'd' for x, y in values)
    values.sort(key=itemgetter(0), reverse=True)
    maxv = values.pop(0)
    if values:
        short = False
    master = BaseDepiction(maxv, alldecimal, type_repr, outformat, short)
    master.add_row()
    for val in values:
        base = BaseDepiction(val, alldecimal, type_repr, outformat, short, header=False)
        master + base
    print(master)

if __name__ == "__main__":
    binaryrepr()
