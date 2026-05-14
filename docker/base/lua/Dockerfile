FROM ubuntu:24.04
RUN apt-get update && apt-get install -y --no-install-recommends \
    lua5.4 luarocks build-essential liblua5.4-dev curl ca-certificates && \
    luarocks install --lua-version=5.4 lua-cjson && \
    mkdir -p /usr/local/share/lua/5.4 && \
    curl -fsSL -o /usr/local/share/lua/5.4/serpent.lua \
        https://raw.githubusercontent.com/pkulchenko/serpent/master/src/serpent.lua && \
    apt-get purge -y --auto-remove curl && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /tests /output /opt
ARG RUNNER_HASH
COPY runners/runner.sh /runner.sh
COPY runners/framec_cached.sh /framec_cached.sh
COPY runners/lua_batch.sh /lua_batch.sh
COPY runners/TestRunner.lua /opt/TestRunner.lua
RUN chmod +x /runner.sh /lua_batch.sh /framec_cached.sh
ENTRYPOINT ["/runner.sh"]
CMD ["lua"]
