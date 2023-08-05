#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Django Heroku Connect documentation build configuration file, created by
# sphinx-quickstart on Thu Nov 30 13:44:31 2017.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))
import importlib
import inspect
import sys
import os

import django
import sphinx_rtd_theme

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.testapp.settings")
sys.path.insert(0, os.path.abspath('..'))
django.setup()


# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.inheritance_diagram',
    'sphinx.ext.intersphinx',
    'sphinx.ext.intersphinx',
    'sphinx.ext.githubpages',
    'sphinxcontrib.spelling',
    'sphinx.ext.linkcode',
]


def linkcode_resolve(domain, info):
    """Link source code to GitHub."""
    project = 'django-heroku-connect'
    github_user = 'Thermondo'
    head = 'master'

    if domain != 'py' or not info['module']:
        return None
    filename = info['module'].replace('.', '/')
    mod = importlib.import_module(info['module'])
    basename = os.path.splitext(mod.__file__)[0]
    if basename.endswith('__init__'):
        filename += '/__init__'
    item = mod
    lineno = ''

    for piece in info['fullname'].split('.'):
        try:
            item = getattr(item, piece)
        except AttributeError:
            pass
        try:
            lines, first_line = inspect.getsourcelines(item)
            lineno = '#L%d-L%s' % (first_line, first_line + len(lines) - 1)
        except (TypeError, IOError):
            pass
    return ("https://github.com/%s/%s/blob/%s/%s.py%s" %
            (github_user, project, head, filename, lineno))


# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'Django Heroku Connect'
copyright = '2017, Thermondo GmbH'
author = 'Thermondo GmbH'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = ''
# The full version, including alpha/beta/rc tags.
release = ''

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#

html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'DjangoHerokuConnectdoc'


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'DjangoHerokuConnect.tex', 'Django Heroku Connect Documentation',
     'Thermondo GmbH', 'manual'),
]


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'djangoherokuconnect', 'Django Heroku Connect Documentation',
     [author], 1)
]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'DjangoHerokuConnect', 'Django Heroku Connect Documentation',
     author, 'DjangoHerokuConnect', 'One line description of project.',
     'Miscellaneous'),
]


intersphinx_mapping = {
    'python': ('http://docs.python.org/3.6', None),
    'django': ('https://docs.djangoproject.com/en/stable/',
               'https://docs.djangoproject.com/en/stable/_objects/'),
}


spelling_word_list_filename = 'spelling_wordlist.txt'
spelling_show_suggestions = True


inheritance_graph_attrs = dict(rankdir="TB", size='"6.0, 8.0"',
                               fontsize=14, ratio='compress')
