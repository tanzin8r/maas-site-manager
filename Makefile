define BACKEND_PACKAGES
python3-venv \
python3-dev \
tox \
postgresql
endef

define FRONTEND_PACKAGES
yarnpkg
endef


# Dependencies

install-dependencies: install-backend-dependencies install-frontend-dependencies
.PHONY: install-dependencies

install-backend-dependencies:
	sudo -E DEBIAN_FRONTEND=noninteractive apt -y install $(BACKEND_PACKAGES)
.PHONY: install-backend-dependencies

install-frontend-dependencies:
	sudo -E DEBIAN_FRONTEND=noninteractive apt -y install $(FRONTEND_PACKAGES)
.PHONY: install-frontend-dependencies


# Overall CI targets

ci-dep: ci-backend-dep ci-frontend-dep
.PHONY: ci-dep

ci-build: # will run the frontend build targets
.PHONY: ci-build ci-frontend-build

ci-lint: ci-backend-lint  # ci-frontend-lint  # TODO: linter not set up, uncomment later
.PHONY: ci-lint

ci-test: ci-backend-test  # ci-frontend-tests  # TODO: tests not yet working, uncomment later
.PHONY: ci-test


# Backend CI targets

ci-backend-dep: install-backend-dependencies
.PHONY: ci-backend-dep

ci-backend-build:  # nothing to do since everything is run in tox envs
.PHONY: ci-backend-build

ci-backend-lint:
	cd backend && tox -e lint,check
.PHONY: ci-backend-lint

ci-backend-test:
	cd backend && tox -e test
.PHONY: ci-test


# Frontend CI targets

ci-frontend-dep: install-frontend-dependencies
	cd frontend && yarnpkg install
.PHONY: ci-frontend-dep

ci-frontend-build:  # nothing to do since everything is run in tox envs
	cd frontend && yarnpkg run build
.PHONY: ci-frontend-build

ci-frontend-lint:
	# cd frontend && yarn run lint  # TODO: uncomment once linting is set up
.PHONY: ci-frontend-lint

ci-frontend-test:
	cd frontend && yarnpkg run test --  --silent run
.PHONY: ci-test

