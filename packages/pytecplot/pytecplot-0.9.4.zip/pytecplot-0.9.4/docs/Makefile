# Makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = python3 -c "import sys,sphinx;sys.exit(sphinx.main(sys.argv))"
PAPER         =
BUILDDIR      = .

# Internal variables.
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -d $(BUILDDIR)/.doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) source
# the i18n builder cannot share the environment and doctrees with the others
I18NSPHINXOPTS  = $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) source

.PHONY: help
help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  apicdoc    to make reference API files"
	@echo "  html       to make standalone HTML files"

.PHONY: clean
clean:
	rm -rf $(BUILDDIR)/.doctrees $(BUILDDIR)/html source/api $(BUILDDIR)/.src $(BUILDDIR)/.staging

.PHONY: apidoc
apidoc:
	python3 source/gendoc.py source/toc.yaml source/api
	@echo "API reference documentation (rst files) generated."

.PHONY: html
html:
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(BUILDDIR)/html
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."
