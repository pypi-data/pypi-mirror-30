# -*- coding: utf-8 -*-
# :Project:   metapensiero.sqlalchemy.dbloady -- File functional test
# :Created:   dom 08 apr 2018 13:57:32 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018 Lele Gaifax
#

PYTHON3 ?= python3.6

.PHONY: test
test: env
	env/bin/python test.py

env:
	$(PYTHON3) -m venv env
	env/bin/pip install --upgrade pip
	env/bin/pip install sqlalchemy
	env/bin/pip install -e ../.. .

.PHONY: clean
clean:

.PHONY: realclean
realclean: clean
	rm -rf env __pycache__ testdbloady.egg-info
