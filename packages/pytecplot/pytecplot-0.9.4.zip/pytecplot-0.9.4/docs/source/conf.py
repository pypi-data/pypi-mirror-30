# coding: utf-8
#!/usr/bin/env python3
#
# pytecplot documentation build configuration file, created by
# sphinx-quickstart on Mon Feb 29 09:27:13 2016.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.
import sys
import os
from datetime import datetime
from unittest.mock import patch, Mock

class AutoAttr:
    def __call__(self):
        pass
    def __getattr__(self, attr):
        return self

no_dlopen_patch = patch('ctypes.cdll.LoadLibrary', Mock(return_value=AutoAttr()))
no_dlopen_patch.start()

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
here = os.path.abspath(os.path.realpath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.normpath(os.path.join(here,'..','..')))
sys.path.insert(0, os.path.normpath(os.path.join(here,'..','.staging')))

import tecplot


# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    # The autodoc extension will pull docstrings directly from the python source code.
    'sphinx.ext.autodoc',
    #
    # The napoleon extension will translate google doc style docstrings into Restructured Text style docstrings before
    # sending the docstrings to Sphinx.
    #
    # We thus get the best of both worlds:
    #  Readable docstrings in the code and and nicely formatted sphinx html.
    # See: http://www.sphinx-doc.org/en/stable/ext/napoleon.html#module-sphinx.ext.napoleon
    #
    'sphinx.ext.napoleon',
    #'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    #'sphinx.ext.todo',
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
    #'sphinx.ext.linkcode',
    'sphinx.ext.autosummary',
    'sphinx.ext.coverage',
]

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = False  # We use google style docstrings only!
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = False
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = False

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The encoding of source files.
#source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'PyTecplot'
copyright = u'{}, Tecplot, Inc.'.format(datetime.now().year)
author = u'Tecplot, Inc.'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The version.
version = '.'.join(str(x) for x in tecplot.version_info[:2])
release = tecplot.__version__

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None
highlight_language = 'python'

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
#today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build']

# The reST default role (used for this markup: `text`) to use for all
# documents.
default_role = 'any'

# If true, '()' will be appended to :func: etc. cross-reference text.
add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
#add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
#show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
# sphinx friendly
pygments_style = 'friendly'

# A list of ignored prefixes for module index sorting.
#modindex_common_prefix = []

# If true, keep warnings as "system message" paragraphs in the built documents.
#keep_warnings = False

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False


# -- Options for HTML output ----------------------------------------------


# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
# alabaster pydoc default classic sphinx_rtd_theme

### py3doc Enhanced Theme
html_theme = 'py3doc_enhanced'
html_theme_path = ['_themes']

### ReadTheDocs Theme
#import sphinx_rtd_theme
#html_theme = 'sphinx_rtd_theme'
#html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
#html_title = None

# A shorter title for the navigation bar.  Default is the same as html_title.
html_short_title = '%s-%s' % (project, version)

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = './_static/powered_by_tecplot.png'

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
#html_favicon = None

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
#html_static_path = ['_static']

# Add any extra paths that contain custom files (such as robots.txt or
# .htaccess) here, relative to this directory. These files are copied
# directly to the root of the documentation.
#html_extra_path = []

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
html_last_updated_fmt = '%b %d, %Y'

# Custom sidebar templates, maps document names to template names.
html_sidebars = {'**': ['searchbox.html', 'globaltoc.html', 'sourcelink.html'],}

# Additional templates that should be rendered to pages, maps page names to
# template names.
#html_additional_pages = {'*' : 'copybutton.js'}

# If false, no module index is generated.
#html_domain_indices = True

# If false, no index is generated.
html_use_index = True

# If true, the index is split into individual pages for each letter.
html_split_index = False

# If true, links to the reST sources are added to the pages.
#html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
#html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
#html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
#html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
#html_file_suffix = None

# Language to be used for generating the HTML full-text search index.
# Sphinx supports the following languages:
#   'da', 'de', 'en', 'es', 'fi', 'fr', 'h', 'it', 'ja'
#   'nl', 'no', 'pt', 'ro', 'r', 'sv', 'tr'
#html_search_language = 'en'

# A dictionary with options for the search language support, empty by default.
# Now only 'ja' uses this config value
#html_search_options = {'type': 'default'}

# The name of a javascript file (relative to the configuration directory) that
# implements a search results scorer. If empty, the default will be used.
#html_search_scorer = 'scorer.js'

# Output file base name for HTML help builder.
htmlhelp_basename = 'pytecplotdoc'

# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
# The paper size ('letterpaper' or 'a4paper').
#'papersize': 'letterpaper',

# The font size ('10pt', '11pt' or '12pt').
#'pointsize': '10pt',

# Additional stuff for the LaTeX preamble.
#'preamble': '',

# Latex figure (float) alignment
#'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'pytecplot.tex', 'pytecplot Documentation',
     'Tecplot, Inc.', 'manual'),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
#latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
#latex_use_parts = False

# If true, show page references after internal links.
#latex_show_pagerefs = False

# If true, show URL addresses after external links.
#latex_show_urls = False

# Documents to append as an appendix to all manuals.
#latex_appendices = []

# If false, no module index is generated.
#latex_domain_indices = True


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'pytecplot', 'pytecplot Documentation',
     [author], 1)
]

# If true, show URL addresses after external links.
#man_show_urls = False


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'pytecplot', 'pytecplot Documentation',
     author, 'pytecplot', 'One line description of project.',
     'Miscellaneous'),
]

# Documents to append as an appendix to all manuals.
#texinfo_appendices = []

# If false, no module index is generated.
#texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
#texinfo_show_urls = 'footnote'

# If true, do not generate a @detailmenu in the "Top" node's menu.
#texinfo_no_detailmenu = False


# -- Options for Epub output ----------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright

# The basename for the epub file. It defaults to the project name.
#epub_basename = project

# The HTML theme for the epub output. Since the default themes are not
# optimized for small screen space, using the same theme for HTML and epub
# output is usually not wise. This defaults to 'epub', a theme designed to save
# visual space.
#epub_theme = 'epub'

# The language of the text. It defaults to the language option
# or 'en' if the language is not set.
#epub_language = ''

# The scheme of the identifier. Typical schemes are ISBN or URL.
#epub_scheme = ''

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#epub_identifier = ''

# A unique identification for the text.
#epub_uid = ''

# A tuple containing the cover image and cover page html template filenames.
#epub_cover = ()

# A sequence of (type, uri, title) tuples for the guide element of content.opf.
#epub_guide = ()

# HTML files that should be inserted before the pages created by sphinx.
# The format is a list of tuples containing the path and title.
#epub_pre_files = []

# HTML files that should be inserted after the pages created by sphinx.
# The format is a list of tuples containing the path and title.
#epub_post_files = []

# A list of files that should not be packed into the epub file.
epub_exclude_files = ['search.html']

# The depth of the table of contents in toc.ncx.
#epub_tocdepth = 3

# Allow duplicate toc entries.
#epub_tocdup = True

# Choose between 'default' and 'includehidden'.
#epub_tocscope = 'default'

# Fix unsupported image types using the Pillow.
#epub_fix_images = False

# Scale large images.
#epub_max_image_width = 0

# How to display URL addresses: 'footnote', 'no', or 'inline'.
#epub_show_urls = 'inline'

# If false, no index is generated.
#epub_use_index = True

nitpicky = True  # Warn about all unresolved references

intersphinx_mapping = {'python': ('https://docs.python.org/3.5', None)}

#######################################
# Macros
#######################################
# TODO (10/11/16, davido): Add a preprocessing step which makes
# these substitutions directly in the source code before publishing

rst_prolog = """
.. |Tecplot 360| replace:: `Tecplot 360 <http://www.tecplot.com/products/tecplot-360>`__
.. |Tecplot License| replace:: `Tecplot 360 License <http://www.tecplot.com/my/license-keys>`__
.. |TecPLUS| replace:: `TecPLUS™ <http://www.tecplot.com/products/software-maintenance-services>`__
.. |Tecplot Engine| replace:: Tecplot Engine
.. |PyTecplot| replace:: PyTecplot
.. |Tecplot Macro Scripting Guide| replace:: `Tecplot Macro Scripting Guide <http://download.tecplot.com/360/current/360_scripting_guide.pdf>`__
.. |export_supersample_description| replace:: Controls the amount of antialiasing used in the image.
            Valid values are 1-16. A value of **1** indicates that no antialiasing will
            be used. Antialiasing smooths jagged edges on text,
            lines, and edges of image output formats by the process of supersampling.
            Some graphics cards can cause Tecplot 360 to crash when larger anti-aliasing values are used.
            If this occurs on your machine, try updating your graphics driver or
            using a lower anti-aliasing value. (default: **3**)

.. |export_width_description| replace:: Specify a width in pixels for the generated image.
            A larger width increases the quality of your image. However,
            the greater the width, the longer it will take to export the image,
            and the larger the exported file. (default: **800**)
.. |export_filename_description| replace:: filename with or without extension.

.. |export_convert256_description| replace:: Pass `True` to generate an image with no more than 256 colors
            (reduced from a possible 16 million colors).
            Tecplot 360 selects the best color match.
            The image will have a greatly reduced file size,
            but for plots with many colors, the results may be suboptimal.
            If this option is used with transparency, smooth color gradations,
            or antialiasing may result in poor image quality. (default: `False`)

.. |export_region_description| replace:: If ``region`` is a `frame object <Frame>`, then the contents of the
            frame will be exported.
            If region is `ExportRegion.CurrentFrame`, then the contents of the
            currently active frame will be exported.
            If region is `ExportRegion.AllFrames`, then the smallest rectangle
            containing all frames will be exported.
            If region is `ExportRegion.WorkArea`, then everything shown in the
            workspace will be exported.
            (default: `ExportRegion.CurrentFrame`)

.. |export_general_info| replace:: If exporting is taking an unusually long time,
            or you get an error message saying that the image cannot be
            exported, the most likely cause is that the image width you
            are trying to export is too large. Selecting a smaller image
            width will greatly speed up the export process.
            For an image export size of Length x Width, the file size
            for an uncompressed true color image is approximately
            Length x Width x 3. Memory requirements to export
            such an image can be up to twice this size.
            For 256-color images, the maximum file size is approximately
            Length x Width, but is usually less since all 256-color image
            files are compressed. However, the memory requirements for
            exporting are the same as they are for a true color
            uncompressed image.
"""


#######################################
# sphinx patching

from sphinx.domains import python as sphinx_domains_python
from sphinx.util import nodes

def python_resolve_any_xref(self, env, fromdocname, builder, target,
                            node, contnode):
    modname = node.get('py:module')
    clsname = node.get('py:class')
    results = []

    # always search in "refspecific" mode with the :any: role
    matches = self.find_obj(env, modname, clsname, target, None, 1)
    for name, obj in matches:
        if obj[1] == 'module':
            results.append(('py:mod',
                            self._make_module_refnode(builder, fromdocname,
                                                      name, contnode)))
        else:
            results.append(('py:' + self.role_for_objtype(obj[1]),
                            nodes.make_refnode(builder, fromdocname, obj[0], name,
                                         contnode, name)))

    subdomain_preference = ['py:func', 'py:meth', 'py:class', 'py:module']
    if len(results) > 1:
        for subdomain in subdomain_preference:
            filtered_results = list(filter(lambda x: str(x[0]) == subdomain, results))
            if len(filtered_results):
                return filtered_results

    return results

sphinx_domains_python.PythonDomain.resolve_any_xref = python_resolve_any_xref
