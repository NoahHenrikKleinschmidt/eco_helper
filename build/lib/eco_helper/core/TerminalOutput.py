"""
This class handles the stdout and stderr of a subprocess run.
"""

import subprocess

class TerminalOutput(object):
    """
    A class to capture the output of a subprocess run.

    Parameters
    ----------
    process : subprocess.CompletedProcess
        The completed process object from which to read the output.

    """
    def __init__(self, process : subprocess.CompletedProcess):
        self.read_output(process)
        
    def success(self):
        """
        Check if the subprocess run was successful.
        """
        return self.returncode == 0

    def read_output(self, process : subprocess.CompletedProcess):
        """
        Read the output of a subprocess run.

        Parameters
        ----------
        process : subprocess.CompletedProcess
            The completed process object from which to read the output.
        """
        self.stdout = process.stdout.decode("utf-8").strip()
        self.stderr = process.stderr.decode("utf-8").strip()
        self.returncode = process.returncode
        return self

    def __str__(self):
        return self.stdout
    
    def __repr__(self):
        return f"TerminalOutput(stdout={self.stdout}, stderr={self.stderr}, returncode={self.returncode})"
    
    def __bool__(self):
        return self.success()
