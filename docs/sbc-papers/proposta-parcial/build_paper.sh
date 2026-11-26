#!/bin/bash
set -e

echo "=== Compilando Documento SBC (LaTeX + BibTeX) ==="
pdflatex -interaction=nonstopmode proposta.tex > /dev/null
bibtex proposta > /dev/null
pdflatex -interaction=nonstopmode proposta.tex > /dev/null
pdflatex -interaction=nonstopmode proposta.tex > /dev/null

echo "=== Compilação Concluída com Sucesso ==="
TOTAL_PAGES=$(pdfinfo proposta.pdf | grep Pages | awk '{print $2}')
echo "PDF Gerado: proposta.pdf"
echo "Total Atual de Páginas: $TOTAL_PAGES páginas (Meta Parcial: Seções 1 e 2 estruturadas)"
