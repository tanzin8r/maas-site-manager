#!/usr/bin/env make -f

define PACKAGES
libasound2t64 \
libatk-bridge2.0-0 \
libatk1.0-0 \
libatspi2.0-0 \
libcairo-gobject2 \
libcairo2 \
libcups2 \
libdbus-glib-1-2 \
libgbm1 \
libgtk-3-0 \
libnspr4 \
libnss3 \
libpango-1.0-0 \
libpangocairo-1.0-0\
libx11-xcb1 \
libxdamage1 \
libxkbcommon0 \
libxtst6 \
npm \
yarnpkg
endef

FE_TEST_TIMEOUT = 15000
FE_TEST_RETRY = 3

install-node:
	sudo apt update && sudo apt install -y curl xz-utils
	curl -fsSL https://nodejs.org/dist/v22.14.0/node-v22.14.0-linux-x64.tar.xz -o node.tar.xz
	mkdir -p node-22 && tar -xf node.tar.xz -C node-22 --strip-components=1
	rm node.tar.xz
	export PATH=$$(pwd)/node-22/bin:$$PATH && node -v
.PHONY: install-node

install-dependencies:
	sudo -E DEBIAN_FRONTEND=noninteractive \
		apt -y install --no-install-recommends $(PACKAGES)
.PHONY: install-dependencies

ci-dep: install-node install-dependencies
	export PATH=$$(pwd)/node-22/bin:$$PATH && \
	YARN_CACHE_FOLDER=/var/cache/yarn yarnpkg install && \
	PLAYWRIGHT_BROWSERS_PATH=/var/cache/playwright-browsers npx --yes playwright install
.PHONY: ci-dep

ci-build:
	yarnpkg run build
.PHONY: ci-build

ci-lint:
	yarnpkg run lint
.PHONY: ci-lint

ci-test: unit-test e2e-test
.PHONY: ci-test

unit-test:
	VITEST_JUNIT_SUITE_NAME='maas-site-manager frontend tests' \
		yarnpkg run coverage --test-timeout=$(FE_TEST_TIMEOUT) \
		--retry=$(FE_TEST_RETRY) --silent --reporter=junit \
		--reporter=default \
		--outputFile.junit=../junit-frontend.xml
.PHONY: unit-test

e2e-test:
	PLAYWRIGHT_BROWSERS_PATH=/var/cache/playwright-browsers \
	PLAYWRIGHT_JUNIT_OUTPUT_NAME=../junit-e2e.xml \
	npx playwright test --reporter=junit
.PHONY: e2e-test
