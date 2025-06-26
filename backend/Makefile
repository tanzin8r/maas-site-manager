define PACKAGES
python3-venv \
python3-dev \
tox \
postgresql
endef


install-dependencies:
	@if [ "$(shell id -u)" = 0 ]; then \
            export DEBIAN_FRONTEND=noninteractive; \
			apt -y install $(PACKAGES); \
	else \
			sudo -E DEBIAN_FRONTEND=noninteractive \
				apt -y install $(PACKAGES); \
	fi
.PHONY: install-dependencies

ci-dep: install-dependencies
.PHONY: ci-dep

ci-build:  # nothing to do since everything is run in tox envs
.PHONY: ci-build

ci-lint:
	tox run -e lint,check
.PHONY: ci-lint

ci-test:
	tox run -e test -- --junit-xml=../junit-backend.xml --cov-report=xml
.PHONY: ci-test
