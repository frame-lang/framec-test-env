FROM rust:latest
RUN mkdir -p /tests /output /rust_runner && \
    cd /rust_runner && cargo init --name runner && \
    echo 'serde = { version = "1.0", features = ["derive"] }' >> Cargo.toml && \
    echo 'serde_json = "1.0"' >> Cargo.toml && \
    echo 'tokio = { version = "1", features = ["full"] }' >> Cargo.toml && \
    cargo build --release 2>/dev/null || true
ARG RUNNER_HASH
COPY runners/runner.sh /runner.sh
COPY runners/framec_cached.sh /framec_cached.sh
COPY runners/rust_batch.sh /rust_batch.sh
RUN chmod +x /runner.sh /rust_batch.sh /framec_cached.sh
ENTRYPOINT ["/runner.sh"]
CMD ["rust"]
