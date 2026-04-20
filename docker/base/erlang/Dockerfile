FROM erlang:27
RUN mkdir -p /tests /output
ARG RUNNER_HASH
COPY runners/runner.sh /runner.sh
COPY runners/framec_cached.sh /framec_cached.sh
COPY runners/erlang_batch.sh /erlang_batch.sh
RUN chmod +x /runner.sh /erlang_batch.sh /framec_cached.sh
ENTRYPOINT ["/runner.sh"]
CMD ["erlang"]
