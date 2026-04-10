FROM gcc:14
RUN apt-get update && apt-get install -y --no-install-recommends nlohmann-json3-dev && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /tests /output
ARG RUNNER_HASH
COPY runners/runner.sh /runner.sh
RUN chmod +x /runner.sh
ENTRYPOINT ["/runner.sh"]
CMD ["cpp"]
