"""
These are the main functions that are used by ``eco_helper drop``.
"""

import eco_helper.core.dataset as ds

def drop_samples( dataset : ds.Dataset, samples : list ) -> ds.Dataset:
    """
    Drop samples from the dataset.

    Parameters
    ----------
    dataset : Dataset
        The dataset to drop samples from.
    samples : list
        The samples to drop.

    Returns
    -------
    Dataset
        The dataset with the cropped dataset.
    """
    return drop_from_col(dataset, samples, "Sample")

def drop_celltypes( dataset : ds.Dataset, celltypes : list ) -> ds.Dataset:
    """
    Drop celltypes from the dataset.

    Parameters
    ----------
    dataset : Dataset
        The dataset to drop samples from.
    celltypes : list
        The celltypes to drop.

    Returns
    -------
    Dataset
        The dataset with the cropped dataset.
    """
    return drop_from_col(dataset, celltypes, "CellType")

def drop_ids( dataset : ds.Dataset, ids : list ) -> ds.Dataset:
    """
    Drop entries from the dataset.

    Parameters
    ----------
    dataset : Dataset
        The dataset to drop samples from.
    ids : list
        The IDs to drop.

    Returns
    -------
    Dataset
        The dataset with the cropped dataset.
    """
    return drop_from_col(dataset, ids, "ID")

def drop_from_col( dataset : ds.Dataset, values : list, col : str ) -> ds.Dataset:
    """
    Drop entries from the dataset using some column.

    Parameters
    ----------
    dataset : Dataset
        The dataset to drop samples from.
    values : list
        The entries belonging to these values should be dropped.
    col : str
        The column to use for dropping.

    Returns
    -------
    Dataset
        The dataset with the cropped dataset.
    """

    annotation, expression = dataset.annotation, dataset.expression

    if col != "ID" and col not in annotation.columns:
        raise ValueError(f"Column {col} not found in annotation file.")
    elif col not in annotation.columns:
        raise ValueError(f"Column {col} not found in annotation file.")

    values = list(values)

    get_ids = lambda mask: annotation[mask].index.values 
    if col == "ID" and "ID" not in annotation.columns:
        mask = lambda values: annotation.index.isin(values)
    else:
        mask = lambda values: annotation[col].isin(values)

    # drop entries from annotation
    drop_mask = mask(values)
    ids_to_drop = get_ids(drop_mask)

    annotation = annotation[ ~drop_mask ]

    # drop entries from expression
    expression = expression.drop( list(ids_to_drop), axis=1 )

    return ds.Dataset(annotation, expression)

