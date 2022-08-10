"""
The core functions of eco_helper that work with the terminal and running subprocesses.
"""

import os
import sys
import subprocess
from . import TerminalOutput


def run( cmd : str ): 
    """
    Run a command in the terminal without catching any outputs.
    
    Parameters
    ----------
    cmd : str
        The command to run.
    """
    subprocess.run( cmd, shell = True )

def from_terminal( cmd : str ) -> TerminalOutput:
    """
    Run a command in the terminal and return the output.
    
    Parameters
    ----------
    cmd : str
        The command to run.

    Returns
    -------
    TerminalOutput
        The output of the command. Which stores the stdout, stderr, and returncode.
    """
    return TerminalOutput( subprocess.run( cmd, shell = True, capture_output = True ) )

def stdout( cmd : str ) -> str : 
    """
    Run a command in the terminal and return the stdout.
    
    Parameters
    ----------
    cmd : str
        The command to run.

    Returns
    -------
    str
        The stdout of the command.
    """
    return from_terminal( cmd ).stdout

def stderr( cmd : str ) -> str :
    """
    Run a command in the terminal and return the stderr.
    
    Parameters
    ----------
    cmd : str
        The command to run.

    Returns
    -------
    str
        The stderr of the command.
    """
    return from_terminal( cmd ).stderr

def returncode( cmd : str ) -> int :
    """
    Run a command in the terminal and return the returncode.
    
    Parameters
    ----------
    cmd : str
        The command to run.

    Returns
    -------
    int
        The returncode of the command.
    """
    return from_terminal( cmd ).returncode