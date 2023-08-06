.. -*- coding: utf-8 -*-

Changes
-------

2.5 (2018-04-09)
~~~~~~~~~~~~~~~~

- Try to fix different behaviour in progressbar2 3.7.0 w.r.t. multiple progress bars


2.4 (2018-04-08)
~~~~~~~~~~~~~~~~

- Now File elements can read text files

- Support dumping hstore values (not tested enough, though)


2.3 (2017-06-07)
~~~~~~~~~~~~~~~~

- Fix handling of property based attributes


2.2 (2017-05-18)
~~~~~~~~~~~~~~~~

- The File elements may now contain their content, without accessing external files


2.1 (2017-05-02)
~~~~~~~~~~~~~~~~

- New ``--quiet`` option to omit the progress bar


2.0 (2017-04-06)
~~~~~~~~~~~~~~~~

- Require `ruamel.yaml`__ instead of PyYAML__

__ https://pypi.python.org/pypi/ruamel.yaml
__ https://pypi.python.org/pypi/PyYAML


1.11 (2017-03-22)
~~~~~~~~~~~~~~~~~

- Spring cleanup, no externally visible changes


1.10 (2016-11-16)
~~~~~~~~~~~~~~~~~

- Reduce load noise by using progressbar2__

__ https://pypi.python.org/pypi/progressbar2


1.9 (2016-11-15)
~~~~~~~~~~~~~~~~

- Ability to execute raw SQL statements to fetch a value from the database


1.8 (2016-11-15)
~~~~~~~~~~~~~~~~

- Better tests

- Handle assignments to non-relationship properties


1.7 (2016-11-05)
~~~~~~~~~~~~~~~~

- Make Python 3 happy by explicitly use binary mode to read external files


1.6 (2016-10-29)
~~~~~~~~~~~~~~~~

- Quick&approximated solution to load `generic associations`__

__ http://docs.sqlalchemy.org/en/latest/_modules/examples/generic_associations/generic_fk.html


1.5 (2016-03-12)
~~~~~~~~~~~~~~~~

- New complementary dump functionality, exposed by a new cli tool, dbdumpy

- Cosmetic, backward compatible, changes to the YAML format, for nicer sorting


1.4 (2016-02-10)
~~~~~~~~~~~~~~~~

- Data files and preload/postload scripts may be specified also as package relative resources


1.3 (2016-01-14)
~~~~~~~~~~~~~~~~

- New --preload and --postload options to execute arbitrary Python scripts before or after the
  load


1.2 (2016-01-09)
~~~~~~~~~~~~~~~~

- Fix source distribution


1.1 (2016-01-09)
~~~~~~~~~~~~~~~~

- Fix data refs when loading from compact representation


1.0 (2016-01-07)
~~~~~~~~~~~~~~~~

- Allow more compact representation when all instances share the same fields

- Extract dbloady from metapensiero.sphinx.patchdb 1.4.2 into a standalone package
