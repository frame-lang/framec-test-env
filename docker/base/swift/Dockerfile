FROM swift:5.10
RUN mkdir -p /tests /output
ARG RUNNER_HASH
COPY runners/runner.sh /runner.sh
COPY runners/framec_cached.sh /framec_cached.sh
COPY runners/swift_batch.sh /swift_batch.sh
RUN chmod +x /runner.sh /swift_batch.sh /framec_cached.sh
ENTRYPOINT ["/runner.sh"]
CMD ["swift"]
