# Makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
PAPER         =
BUILDDIR      = _build

INSTALLDIR = /home/newville/public_html/asteval/


# Internal variables.
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -d $(BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .

.PHONY: html pdf all help clean dirhtml latex


all: html pdf
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) _build/html
	cd $(BUILDDIR)/latex && make all-pdf
	cp -pr $(BUILDDIR)/latex/asteval.pdf $(BUILDDIR)/html/asteval.pdf
	@echo
	-cd $(BUILDDIR) && ln -s html asteval_doc && zip -pur asteval_doc.zip asteval_doc/* && mv asteval_doc.zip html && rm -f asteval_doc
	@echo "Build finished. The HTML pages are in _build/html."

html:
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(BUILDDIR)/html
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

pdf: latex
	cd $(BUILDDIR)/latex && make all-pdf
	cp -pr $(BUILDDIR)/latex/asteval.pdf ./asteval.pdf

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  html      to make standalone HTML files"
	@echo "  pdf       pdf from latex version"
	@echo "  all       html, pdf, and doc.zip"
	@echo "  clean     to remove all output"

latex:
	$(SPHINXBUILD) -b latex $(ALLSPHINXOPTS) _build/latex
	@echo
	@echo "Build finished; the LaTeX files are in _build/latex."
	@echo "Run \`make all-pdf' or \`make all-ps' in that directory to" \
	      "run these through (pdf)latex."

latexpdf:
	$(SPHINXBUILD) -b latex $(ALLSPHINXOPTS) _build/latex
	@echo "Running LaTeX files through pdflatex..."
	make -C _build/latex all-pdf
	@echo "pdflatex finished; the PDF files are in _build/latex."

clean:
	-rm -rf _build/*
