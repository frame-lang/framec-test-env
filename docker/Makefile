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
# Set FRAMEPILER_SRC to your framepiler checkout:
#   make test FRAMEPILER_SRC=/path/to/framepiler

SHELL := /bin/bash

# --- Configuration ---
FRAMEPILER_SRC ?= $(shell cd ../.. && pwd)/framepiler
DOCKER_DIR     := $(shell pwd)
TEST_ENV_ROOT  := $(shell cd .. && pwd)
RUNNER         := runners/runner.sh
COMPOSE        := docker compose
RUST_IMAGE     := rust:latest

# Detect host architecture for build targets
HOST_ARCH      := $(shell uname -m)

# Languages that run on the host's native architecture
LANGS := python typescript javascript rust c cpp csharp java go php kotlin swift ruby erlang lua dart

# GDScript requires linux/amd64 (Godot has no ARM64 build)
ALL_LANGS := $(LANGS) gdscript

# --- Stamp files ---
STAMP_DIR     := .stamps
RUNNER_HASH   := $(shell shasum -a 256 $(RUNNER) 2>/dev/null | cut -c1-16)
# Track source changes via Cargo.lock (changes whenever source or deps change)
SRC_HASH      := $(shell shasum -a 256 $(FRAMEPILER_SRC)/Cargo.lock 2>/dev/null | cut -c1-16)

$(STAMP_DIR):
	@mkdir -p $(STAMP_DIR)

# --- framec binaries ---
# Built from source inside Docker. Always produces the right Linux binary.

# Native-arch binary (matches Docker's default platform)
$(STAMP_DIR)/framec-native: $(FRAMEPILER_SRC)/Cargo.lock | $(STAMP_DIR)
	@echo "=== Building framec (native arch) ==="
	@docker run --rm \
		-v "$(FRAMEPILER_SRC):/src:ro" \
		-v "$(DOCKER_DIR):/out" \
		$(RUST_IMAGE) \
		bash -c "cp -r /src /build && rm -rf /build/target && cd /build && \
		         cargo build --release -p framec 2>&1 | tail -3 && \
		         cp target/release/framec /out/framec-native"
	@touch $@
	@echo "Built: framec-native ($$(file framec-native | grep -o 'x86-64\|aarch64'))"

# amd64 binary (for GDScript container which requires x86_64)
$(STAMP_DIR)/framec-amd64: $(FRAMEPILER_SRC)/Cargo.lock | $(STAMP_DIR)
	@echo "=== Building framec (amd64 for GDScript) ==="
	@docker run --rm --platform linux/amd64 \
		-v "$(FRAMEPILER_SRC):/src:ro" \
		-v "$(DOCKER_DIR):/out" \
		$(RUST_IMAGE) \
		bash -c "cp -r /src /build && rm -rf /build/target && cd /build && \
		         cargo build --release -p framec 2>&1 | tail -3 && \
		         cp target/release/framec /out/framec-amd64"
	@touch $@
	@echo "Built: framec-amd64"

framec: $(STAMP_DIR)/framec-native
framec-amd64: $(STAMP_DIR)/framec-amd64

# --- Container images ---

define LANG_BUILD_RULE
$(STAMP_DIR)/image-$(1): base/$(1)/Dockerfile $(RUNNER) | $(STAMP_DIR)
	@echo "=== Building $(1) container ==="
	@FRAMEC_BIN=/dev/null $(COMPOSE) build \
		--build-arg RUNNER_HASH=$(RUNNER_HASH) $(1)
	@touch $$@

build-$(1): $(STAMP_DIR)/image-$(1)
endef

$(foreach lang,$(ALL_LANGS),$(eval $(call LANG_BUILD_RULE,$(lang))))

build: $(foreach lang,$(ALL_LANGS),$(STAMP_DIR)/image-$(lang))
	@echo "=== All images built ==="

# --- Run tests ---

define LANG_TEST_RULE
test-$(1): $(STAMP_DIR)/framec-native $(STAMP_DIR)/image-$(1)
	@FRAMEC_BIN=$(DOCKER_DIR)/framec-native $(COMPOSE) run --rm $(1) 2>/dev/null | grep "^# \|^not ok"
endef

$(foreach lang,$(LANGS),$(eval $(call LANG_TEST_RULE,$(lang))))

# GDScript: always uses amd64 binary + amd64 container
test-gdscript: $(STAMP_DIR)/framec-amd64 $(STAMP_DIR)/image-gdscript
	@FRAMEC_BIN=$(DOCKER_DIR)/framec-amd64 $(COMPOSE) run --rm gdscript 2>/dev/null | grep "^# \|^not ok"

test: $(STAMP_DIR)/framec-native build
	@echo "=== Running all tests ($(words $(LANGS)) languages) ==="
	@for lang in $(LANGS); do \
		FRAMEC_BIN=$(DOCKER_DIR)/framec-native $(COMPOSE) run --rm $$lang 2>/dev/null | grep "^# "; \
	done

test-all: test test-gdscript

# --- Compile-only mode ---

define LANG_COMPILE_RULE
compile-$(1): $(STAMP_DIR)/framec-native $(STAMP_DIR)/image-$(1)
	@FRAMEC_BIN=$(DOCKER_DIR)/framec-native COMPILE_ONLY=true $(COMPOSE) run --rm $(1) 2>/dev/null | grep "^# \|^not ok"
endef

$(foreach lang,$(LANGS),$(eval $(call LANG_COMPILE_RULE,$(lang))))

compile: $(STAMP_DIR)/framec-native build
	@echo "=== Compile-only ($(words $(LANGS)) languages) ==="
	@for lang in $(LANGS); do \
		FRAMEC_BIN=$(DOCKER_DIR)/framec-native COMPILE_ONLY=true $(COMPOSE) run --rm $$lang 2>/dev/null | grep "^# "; \
	done

# --- Clean ---

clean:
	@echo "=== Cleaning ==="
	rm -f framec-native framec-amd64
	rm -rf $(STAMP_DIR)
	rm -rf $(TEST_ENV_ROOT)/output/*/tests/*

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
	@test -f framec-amd64 && echo "  framec-amd64:  $$(file framec-amd64 | grep -o 'x86-64\|aarch64\|ELF.*')" || echo "  framec-amd64:  not built"
	@echo ""
	@echo "Images:"
	@for lang in $(ALL_LANGS); do \
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
	@echo "  make framec-amd64       Build framec (x86_64, for GDScript)"
	@echo "  make rebuild            Full clean + rebuild"
	@echo ""
	@echo "Test:"
	@echo "  make test               Run 16 languages (excludes GDScript)"
	@echo "  make test-python        Run single language"
	@echo "  make test-gdscript      GDScript (x86 emulation, ~7 min)"
	@echo "  make test-all           All 17 languages"
	@echo "  make compile            Compile-only mode (all languages)"
	@echo "  make compile-python     Compile-only single language"
	@echo ""
	@echo "Debug:"
	@echo "  make shell-python       Shell into container"
	@echo "  make status             Show build state"
	@echo ""
	@echo "Clean:"
	@echo "  make clean              Remove binaries + stamps + output"
	@echo "  make clean-images       Also remove Docker images"
	@echo ""
	@echo "Config:"
	@echo "  FRAMEPILER_SRC=/path    Framepiler source (default: $(FRAMEPILER_SRC))"

.PHONY: build framec framec-amd64 test test-all compile clean clean-images rebuild status help
.PHONY: $(foreach lang,$(ALL_LANGS),build-$(lang) test-$(lang) compile-$(lang) shell-$(lang))
