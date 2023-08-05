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
        """Initialize the syslog (ISO timestamp) parsing module"""
        self.name = 'syslogiso'
        self.desc = 'syslog (ISO timestamp) parsing module'
        self.date_format = \
                '^(\d\d\d\d-?\d\d-?\d\dT\d\d:?\d\d:?\d\d\.?\d*[+-:0-9Z]+)\s+(\S+)\s+([^\[\] ]+)\[?(\d*)\]?: (.*)'
        self.fields = ['date_stamp', 'log_source', 'source_process',
                'source_pid', 'message']
        self.backup_date_format = None
        self.backup_fields = []
        self.tzone = None
        self.datestamp_type = 'iso'
