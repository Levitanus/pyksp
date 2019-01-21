# pyksp

package, provides API to compilation, testing and maintaining of KSP (NI KONTAKT) code from Python.

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/af2970c7afb14904a9e4425ebe4dc55f)](https://www.codacy.com/app/Levitanus/pyksp?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Levitanus/pyksp&amp;utm_campaign=Badge_Grade)

## what is pyksp

It provides API for generating code from python source to NI Kontakt language: KSP.
This version of documentation asserts users familiar with KSP and Nills SublimeKSP compiler. This new compiler is made in endevour of continuing the Nills work, so I tried to take the best from "parent", improve it a bit, and give the freedom of architecture to the end-coder.

The key features of pyksp are:

* support of unit tests
* support of gui tests
* no language restrictions and much more bad-syntax architecture safety (still SublimeKSP is parse source and interprets every line, pyksp responds only for the "real KSP" part, the rest You cad do, whatever Python allows)
* intelligent compilation (while SublimeKSP can expand source to 200-300K or MUCH more lines of code, before optimize it, pyksp compiles exactly what it needs)
* pretty amount of functions are well-documented and coder has to look into the KSP reference a little bit more rarely
* gui programming becomes a little bit funnier :)
  
Full list of SublimeKSP vs pyksp (I like SublimeKSP) You can find in the respective section.

## installation

since release version 0.1 pyksp will be available via PyPi, but till now:

* clone repository to the local folder
* move to it in console or terminal
* print ``pip install -e pyksp``

[feature exploration on ReadTheDocs](https://pyksp-blog.readthedocs.io/en/latest/)
