FROM rust:1.83-slim

# Install framec binary
COPY framec /usr/local/bin/framec
RUN chmod +x /usr/local/bin/framec

# Create working directories and cargo project
RUN mkdir -p /tests /tmp/out /rust_runner

# Create a minimal Cargo project for running tests
WORKDIR /rust_runner
RUN cargo init --name runner && \
    echo 'serde = { version = "1.0", features = ["derive"] }' >> Cargo.toml && \
    echo 'serde_json = "1.0"' >> Cargo.toml

# Pre-compile dependencies
RUN cargo build --release 2>/dev/null || true

# Copy entry script
COPY run_tests.sh /run_tests.sh
RUN chmod +x /run_tests.sh

WORKDIR /tests

ENTRYPOINT ["/run_tests.sh"]
