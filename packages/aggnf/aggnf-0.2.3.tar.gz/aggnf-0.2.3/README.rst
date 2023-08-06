===============================
aggnf
===============================

.. image:: https://img.shields.io/travis/jwgalley/aggnf.svg
        :target: https://travis-ci.org/jwgalley/aggnf

.. image:: https://img.shields.io/pypi/v/aggnf.svg
        :target: https://pypi.python.org/pypi/aggnf


aggnf: Aggregate Nth Field. A small console utility to count/group text data.



* Free software: MIT license
* Documentation: (COMING SOON!) https://aggnf.readthedocs.org.

Features
--------

Generates aggregate counts of text data, using a specified field as a key.

Fields can be delimited by any string, the default is consecutive whitespace.

Key field can be any integer, with negative integers counting backwards. The default is the last field.

How-To
--------

The ``--help`` option is descriptive::

    ~$ aggnf --help
    Usage: aggnf [OPTIONS] [IN_DATA]

      Group text data based on a Nth field, and print the aggregate result.

      Works like SQL:
          `select field, count(*) from tbl group by field`

      Or shell:
          `cat file | awk '{print $NF}' | sort | uniq -c`

      Arguments:
          IN_DATA   Input file, if blank, STDIN will be used.

    Options:
      -d, --sep TEXT          Field delimiter. Defaults to whitespace.
      -n, --fieldnum INTEGER  The field to use as the key, default: last field.
      -o, --sort              Sort result.
      -i, --ignore-err        Don't exit if field is specified and out of range.
      --help                  Show this message and exit.



Here we generate an example file of 1000 random numbers, and ask aggnf to group it for us, ordering the result by the most common occurrences::

    ~$ seq 1 1000 | while read -r l; do echo -e "line:${l}\t${RANDOM:0:1}"; done > rand.txt
    ~$ aggnf -o rand.txt
           1: 340
           2: 336
           3: 120
           8: 42
           6: 37
           5: 35
           7: 35
           4: 33
           9: 22


This might look familiar, as it's the same result one might get from something like ``select field,count(*) as count from table group by field order by count desc``, or even by the following bash one-liner::

    ~$ cat rand.txt | awk '{print $NF}' | sort | uniq -c | sort -nr
    340 1
    336 2
    120 3
     42 8
     37 6
     35 7
     35 5
     33 4
     22 9


To-Do
-----

1. Output is mangled when using another delimiter, will fix.
2. Add a ``--sum`` option, which will key on one field, and sum the contents of another.
3. Speed optimizations.

Notes
-----

The usefulness of this program is questionable. It's functionality is already covered by existing console commands that are much faster.

This project is merely a quick example to learn the basics of packages which are unfamiliar to me, namely: cookiecutter, tox, and click.

