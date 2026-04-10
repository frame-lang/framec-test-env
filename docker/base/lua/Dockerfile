FROM ubuntu:24.04
RUN apt-get update && apt-get install -y --no-install-recommends \
    lua5.4 luarocks build-essential liblua5.4-dev && \
    luarocks install lua-cjson 2>/dev/null || true && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /tests /output
ARG RUNNER_HASH
COPY runners/runner.sh /runner.sh
RUN chmod +x /runner.sh
ENTRYPOINT ["/runner.sh"]
CMD ["lua"]
