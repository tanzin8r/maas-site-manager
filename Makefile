.DEFAULT_GOAL := ci-build

# return changed paths at first level of the tree
TOP_LEVEL_CHANGES := $(shell git diff-tree --no-commit-id --name-only -r HEAD | cut -d/ -f1| sort | uniq)

install-dependencies ci-dep ci-build ci-lint ci-test:
ifneq (,$(findstring backend,$(TOP_LEVEL_CHANGES)))
	$(MAKE) -C backend $@
endif
ifneq (,$(findstring frontend,$(TOP_LEVEL_CHANGES)))
	$(MAKE) -C frontend $@
endif
.PHONY: install-dependencies ci-dep ci-build ci-lint ci-test

# run by the build-env-prepare job
ci-dep-docker-prepare:
	$(MAKE) -C backend ci-dep
	$(MAKE) -C frontend ci-dep
	chmod -R a+w /var/cache/playwright-browsers /var/cache/yarn || true
.PHONY: ci-dep-docker-prepare


SNAPCRAFT := SNAPCRAFT_BUILD_INFO=1 snapcraft -v
SNAP_FILE := maas-site-manager.snap

snap:
	$(SNAPCRAFT) -o $(SNAP_FILE)
.PHONY: snap

snap-clean:
	$(SNAPCRAFT) clean
	rm -f $(SNAP_FILE)
.PHONY: snap-clean
