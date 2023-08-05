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
    def __init__(self):
        """Initialize the cisco ios parsing module"""
        self.name = 'ciscoios'
        self.desc = 'cisco ios parsing module'
        self.date_format = \
                "^([A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+\S+\s+\d+:\s+(\S+):\s+%([a-zA-Z0-9_]+)-(\d)-[a-zA-Z0-9_]+: (.*)"
        self.fields = ['date_stamp', 'log_source', 'severity',
                'source_process', 'message']
        self.backup_date_format = "^([A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\.?\d*)\s+(\S+)\s+([^\[\]]+)\s%[a-zA-Z0-9_]+-\w-([a-zA-Z0-9_]+): (.*)"
        self.backup_fields = ['date_stamp', 'log_source', 'source_process',
        'action', 'message']
        self.tzone = None
        self.datestamp_type = 'standard'
