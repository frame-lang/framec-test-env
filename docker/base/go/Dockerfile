FROM golang:1.23
RUN mkdir -p /tests /output
ARG RUNNER_HASH
COPY runners/runner.sh /runner.sh
COPY runners/framec_cached.sh /framec_cached.sh
COPY runners/go_batch.sh /go_batch.sh
RUN chmod +x /runner.sh /go_batch.sh /framec_cached.sh
ENTRYPOINT ["/runner.sh"]
CMD ["go"]
