import math


def kb_formatter(kb, precision=2):
    kb = int(kb)
    if kb < 1024:
        return round(kb, precision).__str__() + "KB"
    elif kb < 1048576:
        return round(kb / 1024, precision).__str__() + "MB"
    elif kb < 1073741824:
        return round(kb / 1048576, precision).__str__() + "GB"
    else:
        return round(kb / 1073741824, precision).__str__() + "TB"


"""
converts seconds to days, hours, minutes, seconds
"""


def sex_formatter(seconds):
    m, s = divmod(float(seconds), 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    result = ""
    if d != 0:
        result += int(d).__str__() + " days, "
    if h != 0:
        result += int(h).__str__() + " hours, "
    if m != 0:
        result += int(m).__str__() + " minutes, "
    if s != 0:
        result += round(s, 3).__str__() + " seconds, "

    return result
