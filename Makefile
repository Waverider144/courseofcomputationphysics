LATEXMK ?= latexmk
PYTHON ?= python
REVISED = Course_of_Computational_Physics_Vol1_Revised
VOL0_EN = Course_of_Computational_Physics_Vol0_EN
VOL1_EN = Course_of_Computational_Physics_Vol1_EN
CHAPTERS = $(wildcard vol1_revised/chapters/*.tex)
VOL0_DIR = Vol0_Linear_Algebra_HPC
VOL0_PDF = Course_of_Computational_Physics_Vol0.pdf
VOL0_SOURCES = $(wildcard $(VOL0_DIR)/*.tex $(VOL0_DIR)/chapters/*/*.tex $(VOL0_DIR)/appendices/*.tex $(VOL0_DIR)/references/*.tex)
VOL0_FIGURES = $(wildcard $(VOL0_DIR)/figures/*.pdf $(VOL0_DIR)/results/summary.tex)
VOL0_EN_SOURCES = $(wildcard Vol0_Linear_Algebra_HPC_EN/*.tex Vol0_Linear_Algebra_HPC_EN/chapters/*/*.tex Vol0_Linear_Algebra_HPC_EN/appendices/*.tex Vol0_Linear_Algebra_HPC_EN/references/*.tex)
VOL1_EN_SOURCES = $(wildcard vol1_revised_en/*.tex vol1_revised_en/chapters/*.tex)
VOL0_RECORDS = $(wildcard $(VOL0_DIR)/results/measurements.json $(VOL0_DIR)/results/hardware_*.json)

.PHONY: all revised verify vol0 vol0-examples vol0-verify vol0-hardware english vol0-en vol1-en translations-verify math-verify code-verify check

all: revised vol0 english

revised: $(REVISED).pdf

$(REVISED).pdf: $(REVISED).tex vol1_revised/preamble.tex vol1_revised/references.tex $(CHAPTERS)
	$(LATEXMK) -xelatex -outdir=build -interaction=nonstopmode -halt-on-error $(REVISED).tex
	cp build/$(REVISED).pdf $@

english: vol0-en vol1-en

vol0-en: $(VOL0_EN).pdf

vol1-en: $(VOL1_EN).pdf

Vol0_Linear_Algebra_HPC_EN/appendices/results.tex: verification/render_english_results.py $(VOL0_RECORDS)
	$(PYTHON) verification/render_english_results.py

$(VOL0_EN).pdf: $(VOL0_EN).tex $(VOL0_EN_SOURCES) $(VOL0_FIGURES) Vol0_Linear_Algebra_HPC_EN/appendices/results.tex
	$(LATEXMK) -xelatex -outdir=build/vol0-en -interaction=nonstopmode -halt-on-error $(VOL0_EN).tex
	cp build/vol0-en/$(VOL0_EN).pdf $@

$(VOL1_EN).pdf: $(VOL1_EN).tex $(VOL1_EN_SOURCES)
	$(LATEXMK) -xelatex -outdir=build/vol1-en -interaction=nonstopmode -halt-on-error $(VOL1_EN).tex
	cp build/vol1-en/$(VOL1_EN).pdf $@

translations-verify:
	$(PYTHON) verification/check_english_editions.py

math-verify:
	$(PYTHON) verification/check_math_reference.py

code-verify:
	$(PYTHON) -m unittest discover -s verification -p 'test_*.py'

check: all
	$(MAKE) verify vol0-verify math-verify code-verify translations-verify

verify:
	$(PYTHON) verification/check_revised_volume.py

vol0: $(VOL0_PDF)

$(VOL0_PDF): $(VOL0_SOURCES) $(VOL0_FIGURES)
	$(LATEXMK) -xelatex -outdir=$(VOL0_DIR)/build -interaction=nonstopmode -halt-on-error $(VOL0_DIR)/main.tex
	cp $(VOL0_DIR)/build/main.pdf $@

vol0-examples:
	$(PYTHON) $(VOL0_DIR)/code_examples/run_all.py
	$(PYTHON) $(VOL0_DIR)/code_examples/render_results.py
	$(PYTHON) verification/render_english_results.py

vol0-hardware:
	$(PYTHON) $(VOL0_DIR)/code_examples/run_accelerators.py
	$(PYTHON) $(VOL0_DIR)/code_examples/render_results.py
	$(PYTHON) verification/render_english_results.py

vol0-verify:
	$(PYTHON) verification/check_vol0.py
