# pyksp

package, provides API to compilation, testing and maintaining of KSP (NI KONTAKT) code from Python.

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

## feature exploration:
https://pyksp-blog.readthedocs.io/en/latest/

If this project help you reduce time to develop, you can give me a cup of coffee :)
[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.me/levitanus?ppid=PPC000628&cnac=RU&rsta=en_RU(en_US)&cust=PWXEBUA7XFQ4A&unptid=2deb5e08-b40a-11e8-9905-5cb90192cb40&t=&cal=cf737490701db&calc=cf737490701db&calf=cf737490701db&unp_tpcid=ppme-social-user-profile-created&page=main:email&pgrp=main:email&e=op&mchn=em&s=ci&mail=sys)
