# -*- coding: utf-8 -*-
# :Project:   metapensiero.sqlalchemy.dbloady -- YAML based data loader
# :Created:   ven  1 gen 2016, 16.19.54, CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017 Lele Gaifax
#

TESTDIRS := $(wildcard tests/*)

all: help

help::
	@printf "Development targets\n"
	@printf "===================\n\n"

help::
	@printf "test\n\tRun basic functional test (needs PostgreSQL)\n"

define make-test-rule
help::
	@printf "$(2)-$(1)\n\trun $(2) under $(1)\n"

.PHONY: $(2)-$(1)
$(2)-$(1):
	@$(MAKE) -C $(1) $(2)
endef

$(foreach testdir,$(TESTDIRS),$(eval $(call make-test-rule,$(testdir),test)))
$(foreach testdir,$(TESTDIRS),$(eval $(call make-test-rule,$(testdir),clean)))
$(foreach testdir,$(TESTDIRS),$(eval $(call make-test-rule,$(testdir),realclean)))

.PHONY: test
test: $(addprefix test-,$(TESTDIRS))

.PHONY: clean
clean: $(addprefix clean-,$(TESTDIRS))

.PHONY: realclean
realclean: $(addprefix realclean-,$(TESTDIRS))

include Makefile.release
