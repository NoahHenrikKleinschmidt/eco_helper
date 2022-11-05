"""
Core functions for data visualization. 
These are primarily intended for manual use when analyzing enrichment results generated through `eco_helper enrich` and are
not part of the CLI.

StateScatterplot
----------------

The `StateScatterplot` class is a wrapper for the `scatterplot` function that allows for the visualization of enrichment data
and selective highlighting of subsets within the data. To do so, set up a `StateScatterplot` object with the data of interest
and call the `highlight` method with the desired subsets. `subsets` may be a dictionary of subset keys (labels) and lists of `regex` patterns
to match against a reference column within the data. Alternatively, a `function` can be supplied that accepts the dataframe as sole argument
and returns an array-like object that can be used as subset column. The subsets are always applied through differential coloring. 

Example

    .. code-block:: python

        from eco_helper.visualise import StateScatterplot

        # Create a StateScatterplot object
        sc = StateScatterplot( df, x = "enrichment_score", y = "log10_pvalue", hue = None, style = "gene_set" )

    By itself the StateScatterplot object will will not visualise anything. To generate a basic plot use the `plot` method:

    .. code-block:: python

        # Generate a basic plot
        fig = sc.plot()
        fig.show()
    
    To highlight subsets of the data, use the `highlight` method. 
    For instance, if we liked to highlight all enriched terms containing terms or 
    fragments associated with sugar metabolism and G-protein coupled receptors, we could do:

    .. code-block:: python

        subsets = { 
                    # anything that contains *ose*, or *glyco*, or *gluco* (these are always case insensitive)
                    "sugar metabolism" : [ "ose", "glyco", "gluco" ],

                    # anything that contains *gpcr* or G-protein-coupled-receptors (or any combination with space, dash, or underscore)
                    "GPCR associated" : [ "gpcr", "g( |-|_)protein( |-|_)coupled( |-|_)receptor" ]
                }

        # Highlight the subsets
        fig = sc.highlight( subsets, ref_col = "Term" )
        fig.show()

Plotting backends
-----------------

`eco_helper enrich` can be run in two different backends: `matplotlib` and `plotly`. 
The `matplotlib` backend is the default and and uses `seaborn` and `matplotlib` to generate figures.
The `plotly` backend uses `plotly` and `plotly.graph_objs` to generate figures. 
These figures are interactive and allow features such as hoverinfo or zooming. 

To switch the backend back and forth set `eco_helper.visualise.backend` to either `"matplotlib"` or `"plotly"`.

.. code-block:: python

    import eco_helper.visualise as vis

    vis.backend = "matplotlib" # to use matplotlib figures (default)

    vis.backend = "plotly" # to use plotly figures

"""

from weakref import ref
from qpcr._auxiliary.graphical import make_layout_from_list

import eco_helper.enrich as enrich

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import plotly.express as px

import warnings

# suppress the match groups warning because it's annoying 
# and we don't want to capture the groups anyway...
warnings.filterwarnings("ignore", "This pattern is interpreted as a regular expression, and has match groups." )

# suppress the value being set on a copy of a slice warning
# because we don't care about that here...
warnings.filterwarnings("ignore", "A value is trying to be set on a copy of a slice from a DataFrame" )

backend = "matplotlib"
"""
The plotting backend to use. This can be either `matplotlib` or `plotly`.
"""

def collection_scatterplot( collection : enrich.EnrichmentCollection, x : str, y : str, hue : str = None, style : str = None, **kwargs ):
    """
    Visualize the enrichment data from the prerank or enrichr dictionaries by a scatterplot, one for each ecotype.

    Parameters
    ----------
    collection : EnrichmentCollection
        The EnrichmentCollection to visualize.
    x : str
        The column to use as x-axis.
    y : str
        The column to use as y-axis.
    hue : str
        The column to use as hue.
    style : str
        The column to use as style.
    **kwargs
        Additional keyword arguments to pass to seaborn.scatterplot.
    
    Returns
    -------
    fig : matplotlib.figure.Figure or plotly.graph_objs.Figure
        The figure object.
    """

    if backend == "matplotlib":
        
        return _matplotlib_collection_scatterplot(collection, x, y, hue, style, **kwargs )
    elif backend == "plotly":
        return _plotly_collection_scatterplot(collection, x, y, hue, style, **kwargs )
    else:
        raise ValueError(f"Unknown backend '{backend}'")



def scatterplot( df : pd.DataFrame, x : str, y : str, hue : str = None, style : str = None, **kwargs ):
    """
    Visualize the enrichment data from the prerank or enrichr dictionaries by a scatterplot.
    
    Parameters
    ----------
    df : pd.DataFrame
        The dataframe to visualize.
    x : str
        The column to use as x-axis.
    y : str
        The column to use as y-axis.
    hue : str
        The column to use as hue.
    style : str
        The column to use as style.
    **kwargs
        Additional keyword arguments to pass to seaborn.scatterplot.
    
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object.
    """
    if backend == "matplotlib":
        return _matplotlib_scatterplot(df, x, y, hue, style, **kwargs)
    elif backend == "plotly":
        return _plotly_scatterplot(df, x, y, hue, style, **kwargs)


class StateScatterplot: 
    """
    This class allows scatterplot visualisation of a single celltype / state dataframe. Especially, it allows to
    selectively highlight subsets within the data easily for quicker insight.

    Parameters
    ----------
    df : pd.DataFrame
        The source dataframe. 
    x : str
        The column to use as x-axis.
    y : str
        The column to use as y-axis.
    hue : str
        The column to use as hue.
    style : str
        The column to use as marker style.
    """
    def __init__( self, df : pd.DataFrame, x : str, y : str, hue : str = None, style : str = None ):
        self.df = df
        self.x = x
        self.y = y
        self.hue = hue
        self.style = style
    
    def plot( self, **kwargs ):
        """
        The base plotting function.

        Returns
        -------
        fig : matplotlib.figure.Figure or plotly.graph_objs.Figure
            The figure object.
        """
        return scatterplot( self.df, self.x, self.y, self.hue, self.style, **kwargs )

    def count_highlights( self, subsets : (dict or function), ref_col : str = None, topmost : float = None, cutoff : int = None, dual : bool = True, absolute : bool = False, ax : plt.Axes = None, **kwargs  ):
        """
        Highlight subsets within the dataframe based on a reference column and a dictionary of subsets to highlight, showing the counts of terms associated with each subset in a barplot.

        Parameters
        ----------
        subsets : dict or function
            The dictionary of subsets to highlight. 
            This requires strings as keys and lists of regex patterns of associated terms as values.
            In case a function is provided, this function may take exactly one argument (the dataframe) 
            and must return an array-like object suitable as a new dataframe column on which to base the highlighting.
        ref_col : str
            The reference column of the dataframe. This is only required if a dictionary of subsets is provided.
        topmost : float (optional)
            Count term association in the fraction of topmost enriched terms. This can either be used to restrict counting in total or to add a second counting dataset.
        cutoff : int (optional)
            Remove any subsets that do not have at least this number of counts associated with them. Note, this will affect both the full count and a topmost count in the same way!
        dual : bool (optional)
            If True, the full counts and topmost counts are plotted as separate subsets. Otherwise if topmost is provided, only the topmost counts are shown.
        absolute : bool (optional)
            If True the counts are plotted as absolute values. 
            Otherwise the counts are converted to fractions of all terms within the reference dataset.
        ax : plt.Axes
            The subplot in which to plot. By default a new figure is being created.
            This is ignored in `plotly` backend.
        **kwargs
            Additional keyword arguments.
        
        Returns
        -------
        fig : matplotlib.figure.Figure or plotly.graph_objs.Figure
            The figure object.
        """

        counts = self._count_highlight( ref_col, subsets, topmost, cutoff, dual, absolute )

        xlabel = kwargs.pop( "xlabel", "subset" )
        ylabel = kwargs.pop( "ylabel", "count" )
        title = kwargs.pop( "title", "subset counts" ) 

        if backend == "matplotlib":
            
            fig = self._matplotlib_highlight_count( counts, xlabel, ylabel, title, ax = ax, **kwargs )
            
        elif backend == "plotly":

            fig = self._plotly_highlight_count( counts, xlabel, ylabel, title, **kwargs)

        return fig 

    def highlight( self, subsets : (dict or function), ref_col : str = None, other_color : str = "gray", other_alpha : float = 0.1, ax : plt.Axes = None, **kwargs ): 
        """
        Highlight subsets within the dataframe based on a reference column and a dictionary of subsets to highlight, showing the highlighted terms in a colored scatterplot.

        Note
        ----
        The `other` subset fading is only available in the `matplotlib` backend.
        In `plotly` backend `other` is just another regular subset. 
        However, in this case the subset can simply be turned off in the legend.

        Parameters
        ----------
        subsets : dict or function
            The dictionary of subsets to highlight. 
            This requires strings as keys and lists of regex patterns of associated terms as values.
            In case a function is provided, this function may take exactly one argument (the dataframe) 
            and must return an array-like object suitable as a new dataframe column on which to base the highlighting.
        ref_col : str
            The reference column of the dataframe. This is only required if a dictionary of subsets is provided.
        other_color : str
            The color to use for any data points not belonging to any of the highlighted subsets.
        other_alpha : float
            The factor by which to reduce the opacity of non-highlighted data points relative to the highlighted subsets.
        ax : plt.Axes
            The subplot in which to plot. By default a new figure is being created.
            This is ignored in `plotly` backend.
        **kwargs
            Additional keyword arguments.
        
        Returns
        -------
        fig : matplotlib.figure.Figure or plotly.graph_objs.Figure
            The figure object.
        """
        if isinstance( subsets, dict ):
            if ref_col is None:
                raise ValueError( "Reference column must be provided if dictionary of subsets is provided." )
            self._highlight( ref_col, subsets )

        elif callable( subsets ):
            self.df["__hue__"] = subsets( self.df )

        else:
            raise TypeError( "subsets must be a dict or a function" )

        clear_hue = kwargs.pop( "clear_hue", True )
        x, y, title, xlabel, ylabel, style = self._get_kwargs( kwargs )  

        if backend == "matplotlib":
            
            fig = self._matplotlib_highlight(other_color, other_alpha, ax, style, x, y, title, xlabel, ylabel, **kwargs)
        
        elif backend == "plotly":

            hover_data = self._prep_hoverdata(ref_col, kwargs)
            fig = self._plotly_highlight(x, y, style, title, xlabel, ylabel, hover_data = hover_data, **kwargs)

        if clear_hue:
            self.df.drop( columns = ["__hue__"], inplace = True )

        return fig 

    def top_gene_sets( self, subsets : (dict or function) = None, ref_col : str = None, n : int = None, x_threshold : float = None, y_threshold : float = None, ax : plt.Axes = None, **kwargs ):
        """
        Highlight the topmost-enriched gene sets. This can be either globally or based on a reference column and a dictionary of subsets to highlight, showing the topmost gene sets for each subset highlighted terms in a colored scatterplot.

        Note
        ----
        The `other` subset fading is only available in the `matplotlib` backend.
        In `plotly` backend `other` is just another regular subset. 
        However, in this case the subset can simply be turned off in the legend.

        Parameters
        ----------
        subsets : dict or function
            The dictionary of subsets to highlight. 
            This requires strings as keys and lists of regex patterns of associated terms as values.
            In case a function is provided, this function may take exactly one argument (the dataframe) 
            and must return an array-like object suitable as a new dataframe column on which to base the highlighting.
        ref_col : str
            The reference column of the dataframe. This is only required if a dictionary of subsets is provided.
        n : int
            The number of top gene sets to highlight. If this is provided, then the threshold arguments are ignored.
        x_threshold : float
            The threshold for the x-axis. Only gene sets with an x-axis value above this threshold will be highlighted.
        y_threshold : float
            The threshold for the y-axis. Only gene sets with an y-axis value above this threshold will be highlighted.
        ax : plt.Axes
            The subplot in which to plot. By default a new figure is being created.
            This is ignored in `plotly` backend.
        **kwargs
            Additional keyword arguments.
        
        Returns
        -------
        fig : matplotlib.figure.Figure or plotly.graph_objs.Figure
            The figure object.
        """
        if isinstance( subsets, dict ):
            if ref_col is None:
                raise ValueError( "Reference column must be provided if dictionary of subsets is provided." )
            self._highlight( ref_col, subsets )

        elif callable( subsets ):
            self.df["__hue__"] = subsets( self.df )

        else:
            raise TypeError( "subsets must be a dict or a function" )

        clear_hue = kwargs.pop( "clear_hue", True )
        x, y, title, xlabel, ylabel, style = self._get_kwargs( kwargs )  

        if backend == "matplotlib":
            
            fig = self._matplotlib_top_gene_sets( n, x_threshold, y_threshold, ax, x, y, title, xlabel = xlabel, ylabel = ylabel, **kwargs)
        
        elif backend == "plotly":

            fig = self._plotly_top_gene_sets( x, y, n, x_threshold, y_threshold, xlabel = xlabel, ylabel = ylabel, **kwargs)

        if clear_hue:
            self.df.drop( columns = ["__hue__"], inplace = True )
        return fig


    def _prep_hoverdata(self, ref_col, kwargs):
        """
        Prepare the hover data for the plotly backend.
        """

        hover_data = kwargs.pop( "hover_data", { ref_col : self.df[ref_col] } )

        # make sure to get all the specified data columns
        for key, value in hover_data.items():
            if isinstance( value, str ) and value in self.df.columns:
                hover_data[ key ] = self.df[ value ]

        # and make sure to add the "Term" column (in case it is not anyway the reference column...)
        if "Term" in self.df.columns:
            hover_data["Term"] = self.df["Term"]

        return hover_data

    def _plotly_highlight(self, x, y, style, title, xlabel, ylabel, **kwargs):
        """
        The plotly backend plotting method for highlighted plots.
        """
        style = self.df[ style ] if style else None 
        fig = px.scatter( 
                            x = self.df[x] ,
                            y = self.df[y] ,
                            color = self.df["__hue__"],
                            symbol = style, 
                            title = title,
                            labels = { "x" : xlabel, "y" : ylabel },
                            **kwargs
                        )
        fig.update_layout( legend = dict( title = "") )

        return fig

    def _matplotlib_highlight(self, other_color, other_alpha, ax, style, x, y, title, xlabel, ylabel, **kwargs):
        """
        The matplotlib backend plotting method for highlighted plots
        """
        alpha = kwargs.pop( "alpha", 1 )
        facecolor = kwargs.pop( "facecolor", "none" )

        if ax is None:
            fig, ax = plt.subplots( figsize = kwargs.pop( "figsize", (4, 4) ), dpi = kwargs.pop( "dpi", 300 ) )
        else:
            fig = ax.get_figure()
    
        categories = self.df.query( "__hue__ != 'other'" )
        other = self.df.query( "__hue__ == 'other'" )

        sns.scatterplot(    x = x, y = y, 
                            color = other_color, 
                            style = style, 
                            data = other, 
                            alpha = other_alpha * alpha, 
                            legend = False,
                            ax = ax, **kwargs )

        sns.scatterplot(    x = x, y = y, 
                            hue = "__hue__", 
                            style = style, 
                            data = categories, 
                            alpha = alpha, 
                            ax = ax, **kwargs )

        ax.set( title = title,
                xlabel = xlabel,
                ylabel = ylabel,
                facecolor = facecolor, )

        ax.legend( bbox_to_anchor = (1.01, 1), loc = 2, borderaxespad = 0., frameon = False, facecolor = None )

        return fig

    def _matplotlib_highlight_count( self, df, xlabel, ylabel, title, **kwargs ):
        """
        The matplotlib backend plotting method for highlighted counts plots
        """
        ax = kwargs.pop( "ax", None )
        if ax is None:
            fig, ax = plt.subplots( figsize = kwargs.pop( "figsize", (4, 4) ), dpi = kwargs.pop( "dpi", 300 ) )
        
        rot = kwargs.pop( "rot", 45 )
        align = kwargs.pop( "ha", "left" )
        yscale = kwargs.pop( "yscale", "linear" )

        sns.barplot( data = df, x = "subset", y = "count", hue = "type", **kwargs )
        ax.legend( bbox_to_anchor = (1.01, 1), loc = 2, borderaxespad = 0., frameon = False, facecolor = None )
        
        plt.setp( ax.xaxis.get_majorticklabels(), rotation = -rot, ha = align, rotation_mode = "anchor" )  

        ax.set( title = title,
                xlabel = xlabel,
                ylabel = ylabel,
                yscale = yscale )
    
        return fig 

    def _plotly_highlight_count( self, df, xlabel, ylabel, title, **kwargs ):
        """
        The plotly backend plotting method for highlighted counts plots
        """
        fig = px.bar( df, x = "subset", y = "count", color = "type", barmode = "group", title = title, labels = { "x" : xlabel, "y" : ylabel }, **kwargs ) 
        fig.update_layout( legend = dict( title = "") )
        return fig


    def _count_highlight( self, ref_col, subsets, topmost : float = None, cutoff : int = None, dual : bool = True, absolute : bool = False ):
        """
        Count the number of terms in each subset.

        Parameters
        ----------
        ref_col : str
            The reference column of the dataframe.
        subsets : dict
            The dictionary of subsets to highlight.
            This requires strings as keys and lists of regex patterns of associated terms as values.
        topmost : float, optional
            If provided, the counting can be restricted to a fraction of the data by only taking the topmost fraction of most enriched terms.
            This is useful to avoid overplotting.
        cutoff : int, optional
            To further restrict the results, using a cutoff any subsets with less than this number of terms are removed.
        dual : bool, optional
            If True and topmost is provided, the counts for topmost and total are taken and plotted as separate subgroups.
        absolute : bool, optional
            If True, the counts are taken as absolute values, otherwise they are taken as relative values.

        Returns
        -------
        df : pd.DataFrame
            The dataframe with the counts of subset associated terms.
        """

        if isinstance( subsets, dict ):
            if ref_col is None:
                raise ValueError( "Reference column must be provided if dictionary of subsets is provided." )
            self._highlight( ref_col, subsets )

        elif callable( subsets ):
            self.df["__hue__"] = subsets( self.df )

        else:
            raise TypeError( "subsets must be a dict or a function" )

        counts = self._count_subsets( self.df )
        counts["type"] = "Full count" 

        if not absolute: 
            counts["count"] /= len( self.df )

        if topmost:
            
            fraction = int( len(self.df) * topmost )
            topmost = self.df.sort_values( "Combined Score", ascending = False ).head( fraction ) 
            length = len( topmost )

            topmost = self._count_subsets( topmost )
            topmost["type"] = "Topmost count"

            if not absolute:
                topmost["count"] /= length

            if dual:
                counts = pd.concat( [counts, topmost] )
            else:
                counts = topmost
        
        if cutoff:
            counts = counts.query( f"count >= {cutoff}" )

        self.df.drop( columns = ["__hue__"], inplace = True )

        return counts

    def _plotly_top_gene_sets(self, x, y, ref_col, size = None, subsets = None, n : int = None, x_threshold : float = None, y_threshold : float = None, **kwargs):
        """
        Plot the top enriched gene sets

        Parameters
        ----------
        x : str
            The column to plot on the x-axis.
        y : str
            The column to plot on the y-axis.
        ref_col : str
            The reference column of the dataframe.
        size : str, optional
            The column to use for the size of the points.
        subsets : dict, optional
            The dictionary of subsets to highlight.
        n : int, optional
            The number of gene sets to plot. This is either enterpreted as _per subset_ or total if no subsets are provided.
            If this is provided, then the `x_threshold` and `y_threshold` are ignored.
        x_threshold : float, optional
            The threshold for the x-axis. If provided, only gene sets with x-axis values above this threshold are plotted.
        y_threshold : float, optional
            The threshold for the y-axis. If provided, only gene sets with y-axis values above this threshold are plotted.
        """
        df = self._prep_gene_set_df( x, y, ref_col, size, subsets, n, x_threshold, y_threshold )
        xlabel = kwargs.pop("xlabel", x)
        ylabel = kwargs.pop("ylabel", y)
        fig = px.scatter( df, x = x, y = y, color = "__hue__", size = size, labels = {"x" : xlabel, "y" : ylabel}, **kwargs )
        fig.update_layout( legend = dict( title = "Subset") )
        return fig

    def _matplotlib_top_gene_sets(self, x, y, ref_col, size = None, subsets = None, n : int = None, x_threshold : float = None, y_threshold : float = None, ax = None, **kwargs):
        """
        Plot the top enriched gene sets

        Parameters
        ----------
        x : str
            The column to plot on the x-axis.
        y : str
            The column to plot on the y-axis.
        ref_col : str
            The reference column of the dataframe.
        size : str, optional
            The column to use for the size of the points.
        subsets : dict, optional
            The dictionary of subsets to highlight.
        n : int, optional
            The number of gene sets to plot. This is either enterpreted as _per subset_ or total if no subsets are provided.
            If this is provided, then the `x_threshold` and `y_threshold` are ignored.
        x_threshold : float, optional
            The threshold for the x-axis. If provided, only gene sets with x-axis values above this threshold are plotted.
        y_threshold : float, optional
            The threshold for the y-axis. If provided, only gene sets with y-axis values above this threshold are plotted.
        ax : matplotlib.Axes, optional
            The axes to plot on. If not provided, a new figure and axes are created.
        """
        df = self._prep_gene_set_df( x, y, ref_col, size, subsets, n, x_threshold, y_threshold )
        if not ax:
            fig, ax = plt.subplots( figsize = kwargs.pop("figsize") )

        xlabel = kwargs.pop("xlabel", x)
        ylabel = kwargs.pop("ylabel", "")

        ax.grid( True, axis = "both" )
        sns.scatterplot( data = df, x = x, y = y, hue = "__hue__", size = size, ax = ax, )
        ax.set( xlabel = xlabel, ylabel = ylabel )
        ax.legend( bbox_to_anchor = (1, 1), frameon = False )
        ax.invert_yaxis()
        return fig

    def _prep_gene_set_df( self, x : str, y : str, ref_col : str = None, subsets : dict = None, n : int = None, x_threshold : float = None, y_threshold : float = None):
        """
        Prepares a top-most dataframe to view enriched gene sets.

        Parameters
        ----------
        x : str
            The x-axis column
        y : str
            The y-axis column
        subsets : dict
            The dictionary of subsets to highlight.
        ref_col : str
            The reference column of the dataframe.
        n : int
            The number of gene sets to plot. This is either enterpreted as _per subset_ or total if no subsets are provided.
            If this is provided, then the `x_threshold` and `y_threshold` are ignored.
        x_threshold : float
            The threshold for the x-axis. If provided, only gene sets with x-axis values above this threshold are plotted.
        y_threshold : float
            The threshold for the y-axis. If provided, only gene sets with y-axis values above this threshold are plotted.
        
        Returns
        -------
        df : pd.DataFrame
            The dataframe with the top-most enriched gene sets.
        """
        if subsets:
            if isinstance(subsets, dict):
                self._highlight( ref_col = ref_col, subsets = subsets )
            elif callable(subsets):
                self.df["__hue__"] = subsets( self.df[ref_col] )
            else:
                raise ValueError( "The `subsets` argument must be a dictionary or a callable function." )
            
        if n:
            if "__hue__" in self.df.columns:
                groups = self.df.groupby( "__hue__" )
                df = pd.concat( [group.sort_values( x, ascending = False ).head( n ) for _, group in groups] )
            else:
                df = self.df.sort_values( x, ascending = False ).head( n )
        else:
            df = self.df.query( f"`{x}` >= {x_threshold} and `{y}` >= {y_threshold}" )
        
        df = df.sort_values( x, ascending = True )
        return df

    @staticmethod
    def _count_subsets( df ):
        """
        Count the number of terms in each subset.

        Parameters
        ----------
        df : pd.DataFrame
            The dataframe with a column for the subset of terms.
        
        Returns
        -------
        counts : pd.DataFrame
            The dataframe with the counts of terms in each subset.
        """
        counts = df[ "__hue__" ].value_counts()
        counts = pd.DataFrame( {"count" : counts} ) 
        counts = counts.reset_index()
        counts = counts.rename( columns = {"index" : "subset"} )

        return counts

    def _highlight( self, ref_col : str, subsets : dict ):
        """
        The core function to generate a "__hue__" column within the dataframe.
        """
        ref = self.df[ref_col].astype(str)

        categories = self.df[ref_col].copy()
        categories.iloc[:] = "other"

        for subset, keyterms in subsets.items():

            mask = self._mask_keyterms( ref, keyterms )
            categories.iloc[ mask ] = subset 
        
        self.df.loc[ :, "__hue__" ] = categories

    def _get_kwargs(self, kwargs):
        """
        Get key attributes from kwargs.
        """
        kwargs.pop( "hue", None )
        style = kwargs.pop( "style", self.style )
        x = kwargs.pop( "x", self.x )
        y = kwargs.pop( "y", self.y )

        title = kwargs.pop( "title", None )
        xlabel = kwargs.pop( "xlabel", self.x )
        ylabel = kwargs.pop( "ylabel", self.y ) 

        return x, y, title, xlabel, ylabel, style


    @staticmethod
    def _mask_keyterms( ref : pd.Series, keyterms : list,  ):
        """
        Returns a mask of entries within `ref` matching any of the `keyterms`.
        """
        return ref.str.contains( "|".join( keyterms ), case = False, na = False )



def _matplotlib_scatterplot( df, x, y, hue, style, **kwargs ):
    """
    The matplotlib backend core function for a single scatterplot
    """
    ax = kwargs.pop( "ax", None )
    if ax is None:
        fig, ax = plt.subplots( figsize = kwargs.pop( "figsize", (4, 4) ), dpi = kwargs.pop( "dpi", 300 ) )
    else:
        fig = ax.get_figure()


    title = kwargs.pop( "title", None )
    xlabel = kwargs.pop( "xlabel", x )
    ylabel = kwargs.pop( "ylabel", y )
    facecolor = kwargs.pop( "facecolor", "none" )

    sns.scatterplot( x = x, y = y, hue = hue, style = style, data = df, ax = ax, **kwargs )

    ax.set( title = title,
            xlabel = xlabel,
            ylabel = ylabel,
            facecolor = facecolor )
            
    ax.legend( bbox_to_anchor = (1.01, 1), loc = 2, borderaxespad = 0., frameon = False, facecolor = None )

    return fig 


def _plotly_scatterplot(df, x, y, hue, style, **kwargs):
    """
    The scatterplot function for the plotly backend
    """

    hover_data = kwargs.pop( "hover_data", None )
    if hover_data is None:
        hover_data = [ i for i in ["Term", "Gene_set", "Combined Score"] if i in df.columns ]

    fig = px.scatter( 
                        df, 
                        x = x, y = y, 
                        color = hue,
                        symbol = style,
                        hover_data = hover_data,
                        **kwargs
                    )
    
    return fig


def _plotly_collection_scatterplot(collection, x, y, hue, style, **kwargs):
    """
    The scatterplot function for the plotly backend
    """

    hover_data = kwargs.pop( "hover_data", None )
    if hover_data is None:
        hover_data = [ i for i in ["Term", "Ecotype", "Gene_set", "Combined Score"] if i in list(collection.values())[0].columns ]

    total_df = []
    for ecotype, df in collection:
        df = df.copy()
        df[ "Ecotype" ] = ecotype 

        total_df += [df]

    total_df = pd.concat( total_df )
    total_df = total_df.reset_index( drop = True )

    title = kwargs.pop( "title", None )
    xlabel = kwargs.pop( "xlabel", x )
    ylabel = kwargs.pop( "ylabel", y )

    fig = px.scatter( 
                        total_df, 
                        x = x, y = y, 
                        color = hue,
                        symbol = style,
                        hover_data = hover_data,
                        facet_col = "Ecotype",
                        labels = { x : xlabel, y : ylabel },
                        **kwargs
                    )
    fig.update_layout( title = title )

    return fig


def _matplotlib_collection_scatterplot(collection, x, y, hue, style, **kwargs):
    """
    The scatterplot function for the matplotlib backend.
    """

    nrows, ncols = make_layout_from_list( list(collection.keys()) )
    fig, axs = plt.subplots( nrows, ncols, figsize = kwargs.pop( "figsize", (ncols * 4, nrows * 4) ), dpi = kwargs.pop( "dpi", 300 ) )

    pad = kwargs.pop( "padding", None )
    xlabel = kwargs.pop( "xlabel", x )
    ylabel = kwargs.pop( "ylabel", y )

    for ecotype, ax in zip(collection.keys(), axs.flat):
        sns.scatterplot( x = x, y = y, hue = hue, style = style, data = collection[ecotype], ax = ax, **kwargs )

        ax.set( title = ecotype,
                xlabel = xlabel,
                ylabel = ylabel )

        ax.legend( bbox_to_anchor = (1.01, 1), loc = 2, borderaxespad = 0., frameon = False, facecolor = None )
    
    if pad is not None:
        fig.tight_layout( pad = pad )
    return fig