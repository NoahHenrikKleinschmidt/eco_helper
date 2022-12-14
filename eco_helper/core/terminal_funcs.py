"""
These are core functions of `eco_helper` that work with the terminal and running subprocesses.
They are mostly wrappers for ``subprocess.run(...)`` that capture output directly without the need for manually catching and decoding them.
"""
import subprocess
from .TerminalOutput import TerminalOutput


def run( cmd : str ): 
    """
    Run a command in the terminal without catching any outputs.
    Note, this will run in `shell=True`.
    
    Parameters
    ----------
    cmd : str
        The command to run.
    """
    subprocess.run( cmd, shell = True, executable = bash() )

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
    return TerminalOutput( subprocess.run( cmd, shell = True, capture_output = True, executable = bash() ) )

def stdout( cmd : str, file : str = None ) -> str : 
    """
    Run a command in the terminal and return the stdout.
    
    Parameters
    ----------
    cmd : str
        The command to run.
    file : str
        A file to write the stdout to. Note this will **overwrite** any previously existing file of the same name!
    Returns
    -------
    str
        The stdout of the command.
    """
    out = from_terminal( cmd ).stdout
    if file :
        with open( file, "w" ) as f:
            f.write( out )
    return out

def stderr( cmd : str, file : str = None ) -> str :
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
    err = from_terminal( cmd ).stderr
    if file :
        with open( file, "w" ) as f:
            f.write( err )
    return err

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


def bash():
    """
    Get the current bash executable.
    
    Returns
    -------
    str
        The path to the bash executable.
    """
    return subprocess.run( "which bash", capture_output = True, shell = True ).stdout.decode().strip()