PMACParser
================

|Build Status|  |Coverage Status|  |Code Health|

PMACParser is a library that parses PMAC programs. 
It includes an emulator for forward kinematic programs,
which parses the program and then, using an input dictionary of
variables, runs the program, returning a dictionary of populated
variables based on the operations of the kinematic program.

Documentation
-------------

To use:

from pmacparser.pmac_parser import PMACParser

code_lines = ["Q1=(P(4800+1)*P1+P(4900+1))", "Q5=(P(4800+2)*P2+P(4900+2))"]

input_vars = {"P1": 51, "P2": 345.3, "P4801": 45.4, "P4802": 162.4, "P4901": 4, "P4902": 5}

parser = PMACParser(code_lines)

output_vars = parser.parse(input_vars)

.. |Build Status| image:: https://api.travis-ci.org/dls-controls/pmacparser.svg
    :target: https://travis-ci.org/dls-controls/pmacparser
.. |Coverage Status| image:: https://coveralls.io/repos/github/dls-controls/pmacparser/badge.svg?branch=master
    :target: https://coveralls.io/github/dls-controls/pmacparser?branch=master
.. |Code Health| image:: https://landscape.io/github/dls-controls/pmacparser/master/landscape.svg?style=flat
    :target: https://landscape.io/github/dls-controls/pmacparser/master

