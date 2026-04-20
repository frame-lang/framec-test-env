FROM dart:3.4
RUN mkdir -p /tests /output
ARG RUNNER_HASH
COPY runners/runner.sh /runner.sh
COPY runners/framec_cached.sh /framec_cached.sh
COPY runners/dart_batch.sh /dart_batch.sh
RUN chmod +x /runner.sh /dart_batch.sh /framec_cached.sh
ENTRYPOINT ["/runner.sh"]
CMD ["dart"]
