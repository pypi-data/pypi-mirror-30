# -*- coding: utf-8 -*-
# :Project:   metapensiero.sqlalchemy.dbloady -- JSON functional test
# :Created:   mar 08 nov 2016 09:48:18 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017 Lele Gaifax
#

PYTHON3 ?= python3.6

.PHONY: test
test: env testdbloadydb
	env/bin/dbloady -u postgresql://localhost/testdbloady data.yaml
	env/bin/python model.py test

env:
	$(PYTHON3) -m venv env
	env/bin/pip install --upgrade pip
	env/bin/pip install sqlalchemy psycopg2
	env/bin/pip install -e ../.. .

.PHONY: testdbloadydb
testdbloadydb:
	dropdb --if-exists testdbloady
	createdb testdbloady
	env/bin/python model.py setup

.PHONY: clean
clean:
	dropdb --if-exists testdbloady

.PHONY: realclean
realclean: clean
	rm -rf env __pycache__ testdbloady.egg-info
