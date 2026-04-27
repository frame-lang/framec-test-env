FROM gcc:14
RUN apt-get update && apt-get install -y --no-install-recommends \
        libcjson-dev ccache && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /tests /output /ccache /usr/local/lib/ccache && \
    ln -sf /usr/bin/ccache /usr/local/lib/ccache/gcc && \
    ln -sf /usr/bin/ccache /usr/local/lib/ccache/cc
# Same ccache wiring as the cpp image — see that Dockerfile for
# the PATH-prefix-with-ccache-dir rationale and the /ccache
# volume note.
ENV PATH="/usr/local/lib/ccache:${PATH}" \
    CCACHE_DIR=/ccache \
    CCACHE_MAXSIZE=500M
ARG RUNNER_HASH
COPY runners/runner.sh /runner.sh
COPY runners/framec_cached.sh /framec_cached.sh
RUN chmod +x /runner.sh /framec_cached.sh
ENTRYPOINT ["/runner.sh"]
CMD ["c"]
