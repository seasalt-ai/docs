# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = docs
ALLSPHINXOPTS   = -d $(BUILDDIR)/doctrees  $(SPHINXOPTS) $(SOURCEDIR)


# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	echo "docs.seasalt.ai" > $(BUILDDIR)/html/CNAME

.PHONY: livehtml
livehtml:
	sphinx-autobuild -b html $(ALLSPHINXOPTS) $(BUILDDIR)/html --port 4002
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."
	@echo "you can access it from http://localhost:4002"
