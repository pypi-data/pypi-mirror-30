#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
################################################################################
#                                                                              #
# text_to_QR_code                                                              #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program converts text to a QR code                                      #
#                                                                              #
# copyright (C) 2018 William Breaden Madden                                    #
#                                                                              #
# This software is released under the terms of the GNU General Public License  #
# version 3 (GPLv3).                                                           #
#                                                                              #
# This program is free software: you can redistribute it and/or modify it      #
# under the terms of the GNU General Public License as published by the Free   #
# Software Foundation, either version 3 of the License, or (at your option)    #
# any later version.                                                           #
#                                                                              #
# This program is distributed in the hope that it will be useful, but WITHOUT  #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or        #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for     #
# more details.                                                                #
#                                                                              #
# For a copy of the GNU General Public License, see                            #
# <http://www.gnu.org/licenses/>.                                              #
#                                                                              #
################################################################################

usage:
    program [options]

options:
    -h, --help           display help message
    --version            display version and exit

    --text=TEXT          text to convert to QR code       [default: hello world]
    --scale=INT          scale of output QR code image    [default: 50]
    --filepath=FILEPATH  filepath of output QR code image [default: QR_code.png]
    --display=BOOL       display image after creation     [default: true]
"""

import docopt
import os
import subprocess

import pyqrcode

name    = "text_to_QR_code"
version = "2018-03-26T0007Z"

def main(options):

    text     =     options["--text"]
    scale    = int(options["--scale"])
    filepath =     options["--filepath"]
    display  =     options["--display"].lower() == "true"

    filepath = os.path.expanduser(os.path.expandvars(filepath))
    pyqrcode.create(text).png(filepath, scale = scale)
    if display:
        process = subprocess.Popen(["xdg-open", filepath], stdout = subprocess.PIPE)
        output, error = process.communicate()

if __name__ == "__main__":
    options = docopt.docopt(__doc__)
    if options["--version"]:
        print(version)
        exit()
    main(options)
