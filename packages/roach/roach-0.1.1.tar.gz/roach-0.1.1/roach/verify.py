# Copyright (C) 2018 Jurriaan Bremer.
# This file is part of Roach - https://github.com/jbremer/roach.
# See the file 'docs/LICENSE.txt' for copying permission.

import re

class Verify(object):
    @staticmethod
    def ascii(s):
        return bool(re.match("^[\x20-\x7f]*$", s, re.DOTALL))
