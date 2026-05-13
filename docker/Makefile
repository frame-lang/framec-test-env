# Frame Test Environment — Build & Run
#
# Usage:
#   make test                     # Build framec + containers, run all tests
#   make test-python              # Single language
#   make test-all                 # All 17 including GDScript
#   make build                    # Build containers only
#   make framec                   # Build framec binaries only
#   make clean                    # Remove all cached artifacts
#   make rebuild                  # Full clean + rebuild
#   make status                   # Show build state
#   make help                     # This message
#
# The framec binary is always built from source inside Docker.
# FRAMEPILER_SRC must point at your framec checkout. Defaults to
# ../../framec (the sibling-dir layout: <parent>/framec next to
# <parent>/framec-test-env). Override if yours lives elsewhere:
#   make test FRAMEPILER_SRC=/path/to/framec

SHELL := /bin/bash

# --- Configuration ---
# Path to the framec checkout (renamed from "framepiler"). The variable
# keeps its old name for command-line back-compat; the default tracks
# the rename.
FRAMEPILER_SRC ?= $(shell cd ../.. && pwd)/framec
DOCKER_DIR     := $(shell pwd)
TEST_ENV_ROOT  := $(shell cd .. && pwd)
RUNNER         := runners/runner.sh
COMPOSE        := docker compose

# Detect host architecture for build targets
HOST_ARCH      := $(shell uname -m)

# All 17 target languages. GDScript now uses native ARM64 Godot.
LANGS := python typescript javascript rust c cpp csharp java go php kotlin swift ruby erlang lua dart gdscript

# --- Stamp files ---
STAMP_DIR     := .stamps
RUNNER_HASH   := $(shell shasum -a 256 $(RUNNER) 2>/dev/null | cut -c1-16)
# Track source changes: hash Cargo.lock + all .rs files so any code change triggers rebuild
SRC_HASH      := $(shell (shasum -a 256 $(FRAMEPILER_SRC)/Cargo.lock; find $(FRAMEPILER_SRC)/framec/src -name '*.rs' -exec shasum -a 256 {} +) 2>/dev/null | shasum -a 256 | cut -c1-16)
# Stamp file encodes the hash — if source changes, the stamp path changes, forcing rebuild
SRC_STAMP     := $(STAMP_DIR)/framec-src-$(SRC_HASH)

$(STAMP_DIR):
	@mkdir -p $(STAMP_DIR)

# Source-change sentinel: touched whenever the source hash changes
$(SRC_STAMP): | $(STAMP_DIR)
	@rm -f $(STAMP_DIR)/framec-src-*
	@touch $@

# --- framec binaries ---
# Cross-compiled from macOS using cargo-zigbuild (no Docker build step).
# Requires: cargo install cargo-zigbuild, brew install zig,
#           rustup target add aarch64-unknown-linux-gnu x86_64-unknown-linux-gnu

# Native-arch binary (ARM64 Linux for Docker's default platform on Apple Silicon)
# Delete output first to prevent stale binaries surviving cargo's incremental cache.
$(STAMP_DIR)/framec-native: $(SRC_STAMP) | $(STAMP_DIR)
	@echo "=== Cross-compiling framec (aarch64-linux) ==="
	@rm -f "$(DOCKER_DIR)/framec-native"
	@cd "$(FRAMEPILER_SRC)" && \
		CARGO_INCREMENTAL=0 cargo zigbuild --release -p framec --target aarch64-unknown-linux-gnu 2>&1 | tail -3 && \
		cp target/aarch64-unknown-linux-gnu/release/framec "$(DOCKER_DIR)/framec-native"
	@touch $@
	@echo "Built: framec-native ($$(file framec-native | grep -o 'x86-64\|aarch64'))"

framec: $(STAMP_DIR)/framec-native

# --- Container images ---

define LANG_BUILD_RULE
$(STAMP_DIR)/image-$(1): base/$(1)/Dockerfile $(RUNNER) runners/framec_cached.sh | $(STAMP_DIR)
	@echo "=== Building $(1) container ==="
	@FRAMEC_BIN=/dev/null $(COMPOSE) build \
		--build-arg RUNNER_HASH=$(RUNNER_HASH) $(1)
	@touch $$@

build-$(1): $(STAMP_DIR)/image-$(1)
endef

$(foreach lang,$(LANGS),$(eval $(call LANG_BUILD_RULE,$(lang))))

# Kotlin's image bakes in TestRunner.jar + kotlin_batch.sh — rebuild when
# either changes. The kotlin rule from LANG_BUILD_RULE is double-colon
# here so we augment, not override, its prerequisites.
$(STAMP_DIR)/image-kotlin: runners/kotlin_batch.sh runners/TestRunner.kt
$(STAMP_DIR)/image-java: runners/java_batch.sh runners/TestRunner.java
$(STAMP_DIR)/image-csharp: runners/csharp_batch.sh runners/TestRunner.cs runners/TestRunner.csproj
$(STAMP_DIR)/image-typescript: runners/typescript_batch.sh runners/TestRunner.ts
$(STAMP_DIR)/image-rust: runners/rust_batch.sh
$(STAMP_DIR)/image-cpp: runners/cpp_batch.sh
$(STAMP_DIR)/image-swift: runners/swift_batch.sh
$(STAMP_DIR)/image-dart: runners/dart_batch.sh
$(STAMP_DIR)/image-go: runners/go_batch.sh
$(STAMP_DIR)/image-erlang: runners/erlang_batch.sh
$(STAMP_DIR)/image-gdscript: runners/gdscript_batch.sh
$(STAMP_DIR)/image-python: runners/python_batch.sh runners/TestRunner.py
$(STAMP_DIR)/image-javascript: runners/javascript_batch.sh runners/TestRunner.mjs
$(STAMP_DIR)/image-ruby: runners/ruby_batch.sh runners/TestRunner.rb
$(STAMP_DIR)/image-php: runners/php_batch.sh runners/TestRunner.php
$(STAMP_DIR)/image-lua: runners/lua_batch.sh runners/TestRunner.lua

build: $(foreach lang,$(LANGS),$(STAMP_DIR)/image-$(lang))
	@echo "=== All images built ==="

# --- Run tests ---

define LANG_TEST_RULE
test-$(1): $(STAMP_DIR)/framec-native $(STAMP_DIR)/image-$(1)
	@FRAMEC_BIN=$(DOCKER_DIR)/framec-native $(COMPOSE) run --rm $(1) 2>/dev/null | grep "^# \|^not ok"
endef

# Generate test-<lang> for all languages (including GDScript, now native ARM64)
$(foreach lang,$(LANGS),$(eval $(call LANG_TEST_RULE,$(lang))))

# Per-container parallelism cap when running the full matrix.
# Each batch script defaults to nproc internally (correct for solo
# `make test-<lang>` runs that own the whole host). With ~7 heavy
# compilers running concurrently on a 12-core host, the default-nproc
# setting produces ~84 parallel jobs competing for 12 cores — ~7x
# oversubscription that thrashes the scheduler and page cache.
# Pinning each parallel-stage container to MATRIX_JOBS brings total
# concurrency down to ~28 (~2.3x oversubscription) without losing
# meaningful intra-container parallelism. Override on the make line
# if you want a different cap.
MATRIX_JOBS ?= 4

test: $(STAMP_DIR)/framec-native build
	@echo "=== Running all tests in parallel ($(words $(LANGS)) languages) ==="
	@# Daemon preflight — fail fast if Docker is wedged before we
	@# commit to a long matrix run. Docker Desktop on macOS has gone
	@# unresponsive (still answering `compose ps` but not making
	@# progress) for hours at a time; a 5s `docker info` probe
	@# catches that before we start ~5-7 min of work.
	@timeout 5 docker info >/dev/null 2>&1 || { \
		echo "ERROR: Docker daemon unresponsive (timeout 5s on 'docker info')"; \
		exit 2; }
	@# framec_cache size warning — `framec_cached.sh` has LRU eviction
	@# (keeps FRAMEC_CACHE_KEEP=3 most-recent framec hashes per lang),
	@# but if eviction was disabled or hadn't been in place historically
	@# the cache can carry 100+ GB. Warn at 5 GB/lang so the user can
	@# `make clean-cache` before another run packs more in.
	@for d in $(TEST_ENV_ROOT)/output/*/.framec_cache; do \
		[ -d "$$d" ] || continue; \
		kb=$$(du -sk "$$d" 2>/dev/null | cut -f1); \
		mb=$$((kb / 1024)); \
		if [ "$$mb" -gt 5000 ]; then \
			echo "  WARNING: $$d is $${mb} MB — run 'make clean-cache' to reclaim"; \
		fi; \
	done
	@# --force-recreate: collect-results.sh greps `^not ok` lines from
	@# the container's full log history. Persistent containers from
	@# prior runs accumulate logs (one suite invocation per run); a
	@# prior run that failed surfaces its `not ok` lines as if they
	@# were from the current run. Force-recreate clears that history
	@# by replacing the containers, so each matrix run sees only its
	@# own output.
	@FRAMEC_BIN=$(DOCKER_DIR)/framec-native \
	 CPP_COMPILE_JOBS=$(MATRIX_JOBS) \
	 DART_COMPILE_JOBS=$(MATRIX_JOBS) \
	 ERLANG_TEST_JOBS=$(MATRIX_JOBS) \
	 GO_COMPILE_JOBS=$(MATRIX_JOBS) \
	 RUST_EXEC_JOBS=$(MATRIX_JOBS) \
	 SWIFT_COMPILE_JOBS=$(MATRIX_JOBS) \
	 timeout 300 $(COMPOSE) up -d --force-recreate $(LANGS)
	@FRAMEC_BIN=$(DOCKER_DIR)/framec-native \
	 ./collect-results.sh $(LANGS)
	@FRAMEC_BIN=$(DOCKER_DIR)/framec-native $(COMPOSE) down --remove-orphans 2>/dev/null || true

test-all: test

# --- Compile-only mode ---

define LANG_COMPILE_RULE
compile-$(1): $(STAMP_DIR)/framec-native $(STAMP_DIR)/image-$(1)
	@FRAMEC_BIN=$(DOCKER_DIR)/framec-native COMPILE_ONLY=true $(COMPOSE) run --rm $(1) 2>/dev/null | grep "^# \|^not ok"
endef

$(foreach lang,$(LANGS),$(eval $(call LANG_COMPILE_RULE,$(lang))))

compile: $(STAMP_DIR)/framec-native build
	@echo "=== Compile-only in parallel ($(words $(LANGS)) languages) ==="
	@FRAMEC_BIN=$(DOCKER_DIR)/framec-native \
	 COMPILE_ONLY=true $(COMPOSE) up -d $(LANGS)
	@FRAMEC_BIN=$(DOCKER_DIR)/framec-native \
	 ./collect-results.sh $(LANGS)
	@FRAMEC_BIN=$(DOCKER_DIR)/framec-native $(COMPOSE) down --remove-orphans 2>/dev/null || true

# --- Clean ---

clean:
	@echo "=== Cleaning ==="
	rm -f framec-native
	rm -rf $(STAMP_DIR)
	rm -rf $(TEST_ENV_ROOT)/output/*/tests/*

clean-cache:
	@# Remove the framec transpile caches. Safe — they only memoise
	@# `framec compile` output keyed by (framec-binary-sha, source-sha).
	@# Next matrix run re-populates the current framec-hash entry on
	@# first transpile (~30 s overhead for the whole run). See
	@# docs/docker.md "framec transpile cache" for why this exists.
	@echo "=== Cleaning framec transpile caches ==="
	@for d in $(TEST_ENV_ROOT)/output/*/.framec_cache; do \
		[ -d "$$d" ] || continue; \
		kb=$$(du -sk "$$d" 2>/dev/null | cut -f1); \
		mb=$$((kb / 1024)); \
		echo "  rm  $$d  ($${mb} MB)"; \
		rm -rf "$$d"; \
	done

clean-images: clean
	@echo "=== Removing Docker images ==="
	@FRAMEC_BIN=/dev/null $(COMPOSE) down --rmi all 2>/dev/null || true

rebuild: clean-images build

# --- Debug ---

shell-%: $(STAMP_DIR)/framec-native $(STAMP_DIR)/image-%
	FRAMEC_BIN=$(DOCKER_DIR)/framec-native $(COMPOSE) run --rm --entrypoint bash $*

# --- Info ---

status:
	@echo "Framepiler source: $(FRAMEPILER_SRC)"
	@echo "Runner hash:       $(RUNNER_HASH)"
	@echo "Source hash:        $(SRC_HASH)"
	@echo "Host arch:          $(HOST_ARCH)"
	@echo ""
	@echo "Binaries:"
	@test -f framec-native && echo "  framec-native: $$(file framec-native | grep -o 'x86-64\|aarch64\|ELF.*')" || echo "  framec-native: not built"
	@echo ""
	@echo "Images:"
	@for lang in $(LANGS); do \
		if [ -f $(STAMP_DIR)/image-$$lang ]; then \
			echo "  $$lang: built"; \
		else \
			echo "  $$lang: not built"; \
		fi \
	done

help:
	@echo "Frame Test Environment"
	@echo ""
	@echo "  framec is always built from source inside Docker."
	@echo "  Works on Linux, macOS (ARM64 + x86), and Windows."
	@echo ""
	@echo "Build:"
	@echo "  make build              Build all container images"
	@echo "  make build-python       Build single language image"
	@echo "  make framec             Build framec (native arch)"
	@echo "  make framec             Build framec (native ARM64 Linux)"
	@echo "  make rebuild            Full clean + rebuild"
	@echo ""
	@echo "Test:"
	@echo "  make test               Run all 17 languages in parallel"
	@echo "  make test-python        Run single language"
	@echo "  make compile            Compile-only mode (all languages)"
	@echo "  make compile-python     Compile-only single language"
	@echo ""
	@echo "Debug:"
	@echo "  make shell-python       Shell into container"
	@echo "  make status             Show build state"
	@echo ""
	@echo "Clean:"
	@echo "  make clean              Remove binaries + stamps + output"
	@echo "  make clean-cache        Remove framec transpile caches (output/*/.framec_cache)"
	@echo "  make clean-images       Also remove Docker images"
	@echo ""
	@echo "Config:"
	@echo "  FRAMEPILER_SRC=/path    Framepiler source (default: $(FRAMEPILER_SRC))"

.PHONY: build framec test test-all compile clean clean-cache clean-images rebuild status help
.PHONY: $(foreach lang,$(LANGS),build-$(lang) test-$(lang) compile-$(lang) shell-$(lang))
