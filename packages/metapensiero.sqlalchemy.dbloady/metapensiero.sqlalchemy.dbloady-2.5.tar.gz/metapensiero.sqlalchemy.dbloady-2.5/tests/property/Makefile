# -*- coding: utf-8 -*-
# :Project:   metapensiero.sqlalchemy.dbloady -- Property based attributes test
# :Created:   mer 07 giu 2017 14:15:02 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2017 Lele Gaifax
#

PYTHON3 ?= python3.6

.PHONY: test
test: env testdbloadydb
	env/bin/dbloady -u sqlite:////tmp/testdbloady.sqlite data.yaml
	env/bin/python model.py test

env:
	$(PYTHON3) -m venv env
	env/bin/pip install --upgrade pip
	env/bin/pip install sqlalchemy
	env/bin/pip install -e ../.. .

.PHONY: testdbloadydb
testdbloadydb:
	rm -f /tmp/testdbloady.sqlite
	env/bin/python model.py setup

.PHONY: clean
clean:
	rm -f /tmp/testdbloady.sqlite

.PHONY: realclean
realclean: clean
	rm -rf env __pycache__ testdbloady.egg-info
