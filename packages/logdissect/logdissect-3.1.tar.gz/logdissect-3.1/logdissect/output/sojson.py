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

import json
from logdissect.output.type import OutputModule as OurModule

class OutputModule(OurModule):
    def __init__(self, args=None):
        """Initialize the single object JSON output module"""
        self.name = 'sojson'
        self.desc = 'output to a single JSON object'

        if args:
            args.add_argument('--sojson', action='store', dest='sojson',
                    help='set the output file for single object JSON output')
            args.add_argument('--pretty', action='store_true', dest='pretty',
                    help='use pretty formatting for sojson output')

    def write_output(self, data, args=None, filename=None, pretty=False):
        """Write log data to a single JSON object"""
        if args:
            if not args.sojson:
                return 0
            pretty = args.pretty
        if not filename: filename = args.sojson
        if pretty:
            logstring = json.dumps(
                    data['entries'], indent=2, sort_keys=True,
                    separators=(',', ': '))
        else:
            logstring = json.dumps(data['entries'], sort_keys=True)
        
        with open(str(filename), 'w') as output_file:
            output_file.write(logstring)
