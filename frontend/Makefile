#!/usr/bin/env make -f

.PHONY: install-dependencies ci-dep ci-build ci-lint ci-test unit-test e2e-test

define PACKAGES
git \
curl \
fonts-noto-color-emoji \
libxss1 \
libxcomposite1 \
libxrandr2 \
libxext6 \
libxfixes3 \
libxshmfence1 \
libxinerama1 \
libdrm2 \
libxcb1 \
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
libpangocairo-1.0-0 \
libx11-xcb1 \
libxdamage1 \
libxkbcommon0 \
libxtst6 \
npm \
yarnpkg
endef

ifdef JENKINS_URL
	YARN_PATH := /var/cache/yarn yarnpkg install
    PLAYWRIGHT_PATH := /var/cache/playwright-browsers
else
	YARN_PATH := .cache/yarn yarnpkg install
    PLAYWRIGHT_PATH := .cache/playwright-browsers
endif

FE_TEST_TIMEOUT = 15000
FE_TEST_RETRY = 3

install-dependencies:
	sudo -E DEBIAN_FRONTEND=noninteractive \
		apt -y install --no-install-recommends $(PACKAGES)

ci-dep:
	YARN_CACHE_FOLDER=$(YARN_PATH)
	PLAYWRIGHT_BROWSERS_PATH=$(PLAYWRIGHT_PATH) \
		npx --yes playwright install

ci-build:
	yarnpkg run build

ci-lint:
	yarnpkg run lint

ci-test: unit-test e2e-test

unit-test:
	VITEST_JUNIT_SUITE_NAME='maas-site-manager frontend tests' \
		yarnpkg run coverage --test-timeout=$(FE_TEST_TIMEOUT) \
		--retry=$(FE_TEST_RETRY) --silent --reporter=junit \
		--reporter=default \
		--outputFile.junit=../junit-frontend.xml

e2e-test:
	PLAYWRIGHT_BROWSERS_PATH=$(PLAYWRIGHT_PATH) \
	PLAYWRIGHT_JUNIT_OUTPUT_NAME=../junit-e2e.xml \
	npx playwright test --reporter=junit