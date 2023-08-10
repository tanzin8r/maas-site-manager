define PACKAGES
python3-venv \
python3-dev \
tox \
postgresql
endef


install-dependencies:
	sudo -E DEBIAN_FRONTEND=noninteractive \
		apt -y install $(PACKAGES)
.PHONY: install-dependencies

ci-dep: install-dependencies
.PHONY: ci-dep

ci-build:  # nothing to do since everything is run in tox envs
.PHONY: ci-build

ci-lint:
	tox run -e lint,check
.PHONY: ci-lint

ci-test:
	tox run -e test -- --junit-xml=../junit-backend.xml
.PHONY: ci-test

