# Adapted from Python 3.3 idlelib/PyParse.py
def _study1(i, n, ch):
    while i == 3:
        i = 4
        if ch:
            assert i < 5
            continue
        if n:
            return n

assert _study1(3, 4, False) == 4
