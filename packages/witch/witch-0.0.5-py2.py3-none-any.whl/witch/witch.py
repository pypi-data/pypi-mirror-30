# -*- coding: utf-8 -*-

"""Main module."""

import os
import subprocess
from subprocess import CalledProcessError

def witch(app):
    """Return a list of locations a given application.

    Parameters
    ----------
    app : str
        Can be any application on the system path e.g. java.

    Returns
    -------
    result : str
        A list of locations where applications is installed.

    Useage
    ------
    >>>where_is_executable('javac')
    'C:\\Program Files\\Java\\jdk1.8.0_162\\bin\\javac.exe'
    """
    result = ""

    command = 'where'
    if os.name != "nt":  # Windows
        command = 'which'

    try:
        result = subprocess.check_output("{} {}".format(command, app))

    except CalledProcessError as err:
        print("Application {} not found.".format(err))
        return retun

    result = result.decode().splitlines()
    result = [line for line in result if len(line)]
    result = "\n".join(result)

    return result
