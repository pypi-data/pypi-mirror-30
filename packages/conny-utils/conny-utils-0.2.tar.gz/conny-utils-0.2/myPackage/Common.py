import re
import sys
import os

# a wrapper for clean lamda coding
# flat_list = (LamdaList(flat_list)
#              .filter(LamdaList.FILTER_WHITESPACES)
#              .map(LamdaList.STRIP)
#              .map(LamdaList.LSTRIP_SPECIALCHARS)
#              .map(LamdaList.LOWER_CASE)
#              .result()
#              )

class LamdaList:
    STRIP=lambda s: s.strip()
    LSTRIP_SPECIALCHARS=lambda s:  re.sub(r"^[\s•–\-:]*", '', s)
    LOWER_CASE=lambda s: s.lower()
    FILTER_WHITESPACES=lambda s: not re.match(r'^\s*$', s)
    def __init__(self, list):
        self.list = list
    def map(self, lamda):
        self.list = list(map(lamda, self.list))
        return self
    def filter(self, lamda):
        self.list = list(filter(lamda, self.list))
        return self
    def result(self):
        return self.list


def printEncodings():
    print("getdefaultencoding", sys.getdefaultencoding())
    print("stdin", sys.stdin.encoding)
    print("stdout", sys.stdout.encoding)
    print("stderr", sys.stderr.encoding)

    print("you can set the standard encoding via EVN parameters: "
          'YTHONIOENCODING="utf-8"',
          'PYTHONLEGACYWINDOWSSTDIO="utf-8"'
          )

