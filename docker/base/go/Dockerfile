FROM golang:1.23
# Pre-create a module dir for the multi-bin build path: one
# `go build ./cmd/...` invocation produces N test binaries instead
# of N separate go build calls, amortizing toolchain startup.
RUN mkdir -p /tests /output /go_runner/cmd /go_runner/bin && \
    cd /go_runner && go mod init runner
ARG RUNNER_HASH
COPY runners/runner.sh /runner.sh
COPY runners/framec_cached.sh /framec_cached.sh
COPY runners/go_batch.sh /go_batch.sh
RUN chmod +x /runner.sh /go_batch.sh /framec_cached.sh
ENTRYPOINT ["/runner.sh"]
CMD ["go"]
