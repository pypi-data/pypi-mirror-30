'''
The MIT License (MIT)

Copyright (c) 2012-2018 Thorsten Simons (sw@snomis.de)

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import time

# initialized needed variables
#
class gvars():
    '''
    gvars holds constants and variables that need to be present within the
    whole project.
    '''

    # version control
    _version        = "1.0.20"
    _build          = "2018-03-27/Sm"
    _description    = "HCP tools"

    # constants
    Version         = "v.{0} ({1})".format(_version, _build)
    Description     = 'hcpt'
    Author          = "Contact: sw@snomis.de"
    StartTime       = time.time()
    EndTime         = 0

