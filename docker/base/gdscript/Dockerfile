FROM ubuntu:24.04

# Install Godot 4.6.2 headless (ARM64 native)
RUN apt-get update && apt-get install -y --no-install-recommends wget unzip ca-certificates && \
    GODOT_VERSION=4.6.2 && \
    ARCH=$(dpkg --print-architecture) && \
    if [ "$ARCH" = "arm64" ]; then \
        GODOT_ARCH="linux.arm64"; \
    else \
        GODOT_ARCH="linux.x86_64"; \
    fi && \
    wget -q "https://github.com/godotengine/godot/releases/download/${GODOT_VERSION}-stable/Godot_v${GODOT_VERSION}-stable_${GODOT_ARCH}.zip" -O /tmp/godot.zip && \
    unzip -q /tmp/godot.zip -d /tmp && \
    mv /tmp/Godot_v${GODOT_VERSION}-stable_${GODOT_ARCH} /usr/local/bin/godot && \
    chmod +x /usr/local/bin/godot && \
    rm -rf /tmp/godot.zip /var/lib/apt/lists/* && \
    mkdir -p /tests /output

ARG RUNNER_HASH
COPY runners/runner.sh /runner.sh
COPY runners/framec_cached.sh /framec_cached.sh
COPY runners/gdscript_batch.sh /gdscript_batch.sh
RUN chmod +x /runner.sh /gdscript_batch.sh /framec_cached.sh
ENTRYPOINT ["/runner.sh"]
CMD ["gdscript"]
