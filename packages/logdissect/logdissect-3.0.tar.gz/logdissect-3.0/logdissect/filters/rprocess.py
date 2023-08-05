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

import re
from logdissect.filters.type import FilterModule as OurModule

class FilterModule(OurModule):
    def __init__(self, args=None):
        """Initialize the process filter module"""
        self.name = "rprocess"
        self.desc = "filter out a source process"

        if args:
            args.add_argument('--rprocess', action='append', dest='rprocess',
                    metavar='PROCESS', help='filter out a source process')

    def filter_data(self, data, values=None, args=None):
        """Remove entries from specified process (single log)"""
        if args:
            if not args.rprocess:
                return data
        if not values: values = args.rprocess
        newdata = {}
        if 'parser' in data.keys():
            newdata['parser'] = data['parser']
            newdata['source_path'] = data['source_path']
            newdata['source_file'] = data['source_file']
            newdata['source_file_mtime'] = data['source_file_mtime']
            newdata['source_file_year'] = data['source_file_year']
        newdata['entries'] = []

        for entry in data['entries']:
            if 'source_process' in entry.keys():
                if entry['source_process'] not in values:
                    newdata['entries'].append(entry)
            else:
                newdata['entries'].append(entry)

        return newdata
