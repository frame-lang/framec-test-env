FROM gcc:14
RUN apt-get update && apt-get install -y --no-install-recommends \
        nlohmann-json3-dev ccache && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /tests /output /ccache /usr/local/lib/ccache && \
    ln -sf /usr/bin/ccache /usr/local/lib/ccache/g++ && \
    ln -sf /usr/bin/ccache /usr/local/lib/ccache/gcc && \
    ln -sf /usr/bin/ccache /usr/local/lib/ccache/c++ && \
    ln -sf /usr/bin/ccache /usr/local/lib/ccache/cc
# ccache shim convention: install symlinks in a dedicated dir
# (/usr/local/lib/ccache) and prepend that to PATH. ccache then
# searches the rest of PATH for the real compiler. CCACHE_DIR
# persists via the `/ccache` volume mount in docker-compose.yml.
ENV PATH="/usr/local/lib/ccache:${PATH}" \
    CCACHE_DIR=/ccache \
    CCACHE_MAXSIZE=500M
ARG RUNNER_HASH
COPY runners/runner.sh /runner.sh
COPY runners/framec_cached.sh /framec_cached.sh
COPY runners/cpp_batch.sh /cpp_batch.sh
RUN chmod +x /runner.sh /cpp_batch.sh /framec_cached.sh
ENTRYPOINT ["/runner.sh"]
CMD ["cpp"]
