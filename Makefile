# Makefile
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details

PKG_NAME := $(shell basename $(dir $(abspath $(lastword $(MAKEFILE_LIST)))) | sed -r -e "s/-/_/g")
PKG_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
REPO_DIR ?= $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
SOURCE_DIR ?= $(dir $(abspath $(lastword $(MAKEFILE_LIST))))/$(PKG_NAME)
EXTRA_DIR ?= $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
SBIN_DIR := $(EXTRA_DIR)/pypkg
### Custom pylint plugins configuration
PYLINT_PLUGINS_DIR := $(shell if [ -d $(EXTRA_DIR)/pylint_plugins ]; then echo "$(EXTRA_DIR)/pylint_plugins"; fi)
PYLINT_PLUGINS_LIST := $(shell if [ -d $(EXTRA_DIR)/pylint_plugins ]; then cd $(EXTRA_DIR)/pylint_plugins && ls -m *.py | sed 's|.*/||g' | sed 's|, |,|g' | sed 's|\.py||g'; fi)
PYLINT_CLI_APPEND := $(shell if [ -d $(EXTRA_DIR)/pylint_plugins ]; then echo "--load-plugins=$(PYLINT_PLUGINS_LIST)"; fi)
PYLINT_CMD := pylint \
	--rcfile=$(EXTRA_DIR)/.pylintrc \
	$(PYLINT_CLI_APPEND) \
	--output-format=colorized \
	--reports=no \
	--score=no
LINT_FILES := $(shell $(SBIN_DIR)/get-pylint-files.sh $(PKG_NAME) $(REPO_DIR) $(SOURCE_DIR) $(EXTRA_DIR))
###

asort:
	@echo "Sorting Aspell whitelist"
	@$(SBIN_DIR)/sort-whitelist.sh $(PKG_DIR)/data/whitelist.en.pws

bdist: meta
	@echo "Creating binary distribution"
	@cd $(PKG_DIR) && python setup.py bdist

black:
	@echo "Running Black on package files"
	@black $(LINT_FILES)

clean: FORCE
	@echo "Cleaning package"
	@rm -rf $(PKG_DIR)/.tox
	@find $(PKG_DIR) -name '*.pyc' -delete
	@find $(PKG_DIR) -name '__pycache__' -delete
	@find $(PKG_DIR) -name '.coverage*' -delete
	@find $(PKG_DIR) -name '*.tmp' -delete
	@find $(PKG_DIR) -name '*.pkl' -delete
	@find $(PKG_DIR) -name '*.error' -delete
	@rm -rf $(PKG_DIR)/build
	@rm -rf	$(PKG_DIR)/dist
	@rm -rf $(PKG_DIR)/docs/_build
	@rm -rf $(PKG_DIR)/$(PKG_NAME).egg-info
	@rm -rf $(PKG_DIR)/.cache
	@rm -rf $(PKG_DIR)/.eggs

distro: docs clean sdist wheel
	@rm -rf build $(PKG_NAME).egg-info

docs: FORCE
	@$(SBIN_DIR)/build_docs.py $(ARGS)
	@cd $(PKG_DIR)/docs && make linkcheck && make lintshell

default:
	@echo "No default action"

FORCE:

lint: pylint pydocstyle

meta: FORCE
	@echo "Updating package meta-data"
	@cd $(SBIN_DIR) && ./update_copyright_notice.py
	@cd $(SBIN_DIR) && ./gen_req_files.py
	@cd $(SBIN_DIR) && ./gen_pkg_manifest.py

pylint:
	@echo "Running Pylint on package files"
	@PYTHONPATH="$(PYLINT_PLUGINS_DIR):$(PYTHONPATH)" $(PYLINT_CMD) $(LINT_FILES)

pydocstyle:
	@echo "Running Pydocstyle on package files"
	@pydocstyle --config=$(EXTRA_DIR)/.pydocstyle $(LINT_FILES)

sdist: meta
	@echo "Creating source distribution"
	@cd $(PKG_DIR) && python setup.py sdist --formats=zip
	@$(SBIN_DIR)/list-authors.sh

sterile: clean
	@echo "Removing tox directory"
	@rm -rf $(PKG_DIR)/.tox

test: FORCE
	@cd $(SBIN_DIR) && ./gen_req_files.py
	@cd $(SBIN_DIR) && ./gen_pkg_manifest.py
	@$(SBIN_DIR)/rtest.sh $(ARGS)

upload: lint distro
	@twine upload $(PKG_DIR)/dist/*

wheel: lint meta
	@echo "Creating wheel distribution"
	@$(SBIN_DIR)/make-wheels.sh
	@$(SBIN_DIR)/list-authors.sh
