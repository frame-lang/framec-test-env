FROM node:20-bullseye

LABEL maintainer="Framepiler Teams (PT + DAP)" \
      description="Shared Framepiler adapter semantics test environment"

# Basic tools: Python (for potential framec_tests), Git, curl, Rust toolchain.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      python3 python3-pip ca-certificates git curl \
      build-essential pkg-config \
      rustc cargo && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Repos are expected to be mounted:
#   - /frame_transpiler      -> main PT repo (framec source/binary)
#   - /framepiler_test_env   -> this shared env
#
# Example:
#   docker run --rm -it \
#     -v /Users/you/projects/frame_transpiler:/frame_transpiler \
#     -v /Users/you/projects/framepiler_test_env:/framepiler_test_env \
#     framepiler-test-env \
#     bash -c 'cd /framepiler_test_env/adapter_protocol && \
#       npm install && \
#       FRAMEC_BIN=/frame_transpiler/target/release/framec ./scripts/run_adapter_smoke.sh'

CMD ["/bin/bash"]
