define PACKAGES
python3-venv \
python3-dev \
tox \
postgresql
endef

install-dependencies:
	sudo apt -y install $(PACKAGES)
.PHONY: install-dependencies


# CI targets

ci-dep: install-dependencies
.PHONY: ci-dep

ci-build: # nothing to do since everything is run in tox envs
.PHONY: ci-build

ci-lint:
	tox -e lint,check
.PHONY: ci-lint

ci-test:
	tox -e test
.PHONY: ci-test
