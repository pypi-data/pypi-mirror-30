# MIT License
# 
# Copyright (c) 2017 Dan Persons <dpersonsdev@gmail.com>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from logdissect.parsers.type import ParseModule as OurModule

class ParseModule(OurModule):
    def __init__(self, options=[]):
        """Initialize the tcpdump terminal output parsing module"""
        self.name = 'tcpdump'
        self.desc = 'tcpdump terminal output parsing module'
        self.format_regex = \
                "^(\d{2}:\d{2}:\d{2}\.?\d*)\s+(\w+)\s+([\w\-\.]+)\s+>\s+([\w\-\.]+): (.*)"
        self.fields = ['date_stamp', 'protocol', 'source_host', 'dest_host',
                'message']
        self.backup_format_regex = \
                "^(\d{2}:\d{2}:\d{2}\.?\d*)\s+(\w+),\s+(.*)"
        self.backup_fields = ['date_stamp', 'protocol', 'message']
        self.tzone = None
        self.datestamp_type = 'nodate'
