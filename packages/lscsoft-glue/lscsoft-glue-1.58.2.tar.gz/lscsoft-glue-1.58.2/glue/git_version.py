id = "ed01d8cb8ea1ff04564c89941661aae4ca1092e9"
date = "2018-03-15 01:55:49 +0000"
branch = "master"
tag = "glue-release-1.58.2"
if tag == "None":
    tag = None
author = "Ryan Fisher <ryan.fisher@ligo.org>"
builder = "Ryan Fisher <ryan.fisher@ligo.org>"
committer = "Ryan Fisher <ryan.fisher@ligo.org>"
status = "CLEAN: All modifications committed"
version = id
verbose_msg = """Branch: master
Tag: glue-release-1.58.2
Id: ed01d8cb8ea1ff04564c89941661aae4ca1092e9

Builder: Ryan Fisher <ryan.fisher@ligo.org>
Build date: 2018-03-21 22:21:46 +0000
Repository status: CLEAN: All modifications committed"""

import warnings

class VersionMismatchError(ValueError):
    pass

def check_match(foreign_id, onmismatch="raise"):
    """
    If foreign_id != id, perform an action specified by the onmismatch
    kwarg. This can be useful for validating input files.

    onmismatch actions:
      "raise": raise a VersionMismatchError, stating both versions involved
      "warn": emit a warning, stating both versions involved
    """
    if onmismatch not in ("raise", "warn"):
        raise ValueError(onmismatch + " is an unrecognized value of onmismatch")
    if foreign_id == "ed01d8cb8ea1ff04564c89941661aae4ca1092e9":
        return
    msg = "Program id (ed01d8cb8ea1ff04564c89941661aae4ca1092e9) does not match given id (%s)." % foreign_id
    if onmismatch == "raise":
        raise VersionMismatchError(msg)

    # in the backtrace, show calling code
    warnings.warn(msg, UserWarning)

