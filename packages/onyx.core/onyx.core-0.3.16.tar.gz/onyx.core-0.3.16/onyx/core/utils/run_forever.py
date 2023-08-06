###############################################################################
#
#   Copyright: (c) 2017 Carlo Sbraccia
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
###############################################################################

import subprocess
import sys
import os
import logging
import argh


# -----------------------------------------------------------------------------
def run_forever(executable=None, script=None, logging_config_file=None):
    executable = executable or sys.executable

    if script is None:
        args = [executable]
    else:
        args = [executable, script]

    if logging_config_file is not None:
        if os.path.exists(logging_config_file):
            args.append("-l")
            args.append(logging_config_file)
        else:
            raise FileNotFoundError("Logging "
                "config file {0:s} not found".format(logging_config_file))

    # --- configure logger for the run_forever script
    config = {
        "level": logging.INFO,
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    }
    logging.basicConfig(**config)
    logger = logging.getLogger(__name__)

    if sys.platform == "win32":
        # Don't display the Windows GPF dialog if the invoked program dies.
        # https://mail.python.org/pipermail/python-list/2009-January/520255.html
        # see also:
        # https://www.activestate.com/blog/2007/11/supressing-windows-error-report-messagebox-subprocess-and-ctypes
        import ctypes
        SEM_FAILCRITICALERRORS = 1
        SEM_NOGPFAULTERRORBOX  = 2
        SEM_NOOPENFILEERRORBOX = 0x8000
        ctypes.windll.kernel32.SetErrorMode(SEM_FAILCRITICALERRORS |
                                            SEM_NOGPFAULTERRORBOX |
                                            SEM_NOOPENFILEERRORBOX);

    while True:
        try:
            subprocess.check_call(args, shell=False, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as err:
            logger.error("subprocess died with error: {0!s}".format(err))
        else:
            logger.info("subprocess finished without errors, restarting...")


# -----------------------------------------------------------------------------
def main():
    argh.dispatch_command(run_forever)
        