# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'eco_helper'
copyright = '2022, Noah Kleinschmidt'
author = 'Noah Kleinschmidt'
release = '0.0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration


MOCK_MODULES = ['numpy', 'scipy', 'matplotlib', 'plotly', 'plotly.subplots', 'plotly.graph_objs', 'seaborn', 'matplotlib.pyplot', 'matplotlib.lines', 'scipy.interpolate', 'scipy.stats', 'streamlit', 'pandas', 'gseapy', 'qpcr' ]
autodoc_mock_imports = MOCK_MODULES


extensions = [
    # 'autoapi.extension',
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
]
napoleon_numpy_docstring = True
# autoapi_dirs = ['../../eco_helper']

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'press'
html_logo = "../eco_helper.svg"
html_static_path = ['_static']
