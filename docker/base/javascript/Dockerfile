FROM node:20-slim
RUN mkdir -p /tests /output /opt
ARG RUNNER_HASH
COPY runners/runner.sh /runner.sh
COPY runners/framec_cached.sh /framec_cached.sh
COPY runners/javascript_batch.sh /javascript_batch.sh
COPY runners/TestRunner.mjs /opt/TestRunner.mjs
RUN chmod +x /runner.sh /javascript_batch.sh /framec_cached.sh
ENTRYPOINT ["/runner.sh"]
CMD ["javascript"]
