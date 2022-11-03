"""
The class to handle EcoTyper datasets as pairs of annotation-tables and expression-matrices.
"""

BENCHMARK_COLS = ( "ID", "CellType", "Sample" )

import pandas as pd
import warnings

class Dataset:
    """
    This class handles an EcoTyper dataset.

    Parameters
    ----------
    annotation : str
        The filename of the annotation file.
    expression : str
        The filename of the expression matrix file.
    """
    def __init__(self, annotation : (str or pd.DataFrame), expression : (str or pd.DataFrame) ): 
        if isinstance(annotation, str):
            self.annotation = read_anotation(annotation)
        elif isinstance(annotation, pd.DataFrame):
            self.annotation = annotation
        else:
            raise TypeError("annotation must be a filename or a pandas DataFrame")
        
        if isinstance(expression, str):
            self.expression = read_expression(expression)
        elif isinstance(expression, pd.DataFrame):
            self.expression = expression
        else:
            raise TypeError("expression must be a filename or a pandas DataFrame")

    def read( self, annotation : str = None, expression : str = None ):
        """
        Read in a (new) dataset from files.

        Parameters
        ----------
        annotation : str
            The filename of the annotation file.
        expression : str
            The filename of the expression matrix file.
        """
        if annotation is None:
            self.annotation = read_anotation(annotation)
        if expression is None:
            self.expression = read_expression(expression)

    def write( self, annotation : str = None, expression : str = None ):
        """
        Write the dataset to files.

        Parameters
        ----------
        annotation : str
            The filename of the annotation file.
        expression : str
            The filename of the expression matrix file.
        """
        if annotation is None:
            self.annotation.to_csv(annotation, sep='\t')
        if expression is None:
            self.expression.to_csv(expression, sep='\t')

def read_anotation( filename : str ):
    """
    Reads in an annotation file and returns a pandas DataFrame.

    Parameters
    ----------
    filename : str
        The filename of the annotation file.
    
    Returns
    -------
    annotation : pandas.DataFrame
        The annotation file as a pandas DataFrame.
    """
    df = pd.read_csv(filename, sep='\t', index_col=0)
    for col in BENCHMARK_COLS:
        if col not in df.columns:
            warnings.warn(f"The annotation file is not Ecotyper-friendly (yet): Column {col} not found...")
    return df

def read_expression( filename : str ):
    """
    Reads in an expression matrix file and returns a pandas DataFrame.

    Parameters
    ----------
    filename : str
        The filename of the expression matrix file.
    
    Returns
    -------
    expression : pandas.DataFrame
        The expression matrix file as a pandas DataFrame.
    """
    return pd.read_csv(filename, sep='\t', index_col=0)

def write_annotation( dataset : "Dataset", filename : str ):
    """
    Writes the annotation file of a dataset to a file.

    Parameters
    ----------
    dataset : Dataset
        The dataset to write the annotation file for.
    filename : str
        The filename to write the annotation file to.
    """
    dataset.annotation.to_csv(filename, sep='\t')

def write_expression( dataset : "Dataset", filename : str ):
    """
    Writes the expression matrix of a dataset to a file.

    Parameters
    ----------
    dataset : Dataset
        The dataset to write the expression matrix for.
    filename : str
        The filename to write the expression matrix to.
    """
    dataset.expression.to_csv(filename, sep='\t')