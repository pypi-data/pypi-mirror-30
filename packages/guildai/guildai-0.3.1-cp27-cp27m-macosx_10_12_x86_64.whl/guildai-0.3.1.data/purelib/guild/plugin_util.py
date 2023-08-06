# Copyright 2017-2018 TensorHub, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Util functions used by plugins at op runtime.
"""

from __future__ import absolute_import
from __future__ import division

import os
import sys

import yaml

import guild.run

class NoCurrentRun(Exception):
    pass

def exit(msg, exit_status=1):
    """Exit the Python runtime with a message.
    """
    sys.stderr.write(os.path.basename(sys.argv[0]))
    sys.stderr.write(": ")
    sys.stderr.write(msg)
    sys.stderr.write("\n")
    sys.exit(exit_status)

def current_run():
    """Returns an instance of guild.run.Run for the current run.

    The current run directory must be specified with the RUN_DIR
    environment variable. If this variable is not defined, raised
    NoCurrentRun.

    """
    path = os.getenv("RUN_DIR")
    if not path:
        raise NoCurrentRun()
    return guild.run.Run(os.getenv("RUN_ID"), path)

def parse_op_args(args):
    if len(args) < 2:
        exit("usage: %s COMMAND [ARG...]" % args[0])
    return args[1], args[2:]

def args_to_flags(args):
    flags = {}
    name = None
    for arg in args:
        if arg[:2] == "--":
            name = arg[2:]
            flags[name] = True
        elif arg[:1] == "-":
            if len(arg) == 2:
                name = arg[1]
                flags[name] = True
            elif len(arg) > 2:
                name = None
                flags[arg[1]] = arg[2:]
        elif name is not None:
            try:
                arg = yaml.safe_load(arg)
            except yaml.YAMLError:
                pass
            flags[name] = arg
    return flags
