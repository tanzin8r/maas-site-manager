.DEFAULT_GOAL := ci-build

install-dependencies ci-dep ci-build ci-lint ci-test:
	$(MAKE) -C frontend $@
	$(MAKE) -C backend $@
.PHONY: install-dependencies ci-dep ci-build ci-lint ci-test

ci-dep-docker-prepare: ci-dep # run by the build-env-prepare job
	chmod -R a+w /var/cache/playwright-browsers /var/cache/yarn || true
.PHONY: ci-dep-docker-prepare
