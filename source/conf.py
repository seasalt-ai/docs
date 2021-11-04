# pytype: skip-file
# flake8: noqa
# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('../../..'))
import sphinx_rtd_theme


# -- Project information -----------------------------------------------------

project = 'Seasalt.ai Documentation'
copyright = '2020-2021, Seasalt.ai'
author = 'Seasalt.ai'

# The full version, including alpha/beta/rc tags
release = '0.0.1'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx_rtd_theme",
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.autosummary',
    'sphinx.ext.todo', # https://www.sphinx-doc.org/en/master/usage/extensions/todo.html
]

todo_include_todos = True

autosummary_generate = False
autoclass_content = "both"  # Add __init__ doc (ie. params) to class summaries
autosummary_imported_members = True
autodoc_inherit_docstrings = True  # If no class summary, inherit base class summary

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['api']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = 'alabaster'
#
# Configuration options:
# https://sphinx-rtd-theme.readthedocs.io/en/latest/configuring.html
html_theme = 'sphinx_rtd_theme'

html_theme_options = {
    'analytics_id': 'UA-10405841-8',  #  Provided by Google in your dashboard
    # 'analytics_anonymize_ip': False,
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    # 'vcs_pageview_mode': '',
    'style_nav_header_background': '#2980B9',
    # Toc options
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_css_files = ['custom.css']

html_logo = 'logo.png'

# https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-html_extra_path
# html_extra_path = ['cart/index.html']
