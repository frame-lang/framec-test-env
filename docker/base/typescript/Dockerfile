FROM node:20-slim
RUN npm install -g tsx typescript @types/node && \
    mkdir -p /tests /output /tmp/out /opt
ARG RUNNER_HASH
COPY runners/runner.sh /runner.sh
COPY runners/framec_cached.sh /framec_cached.sh
COPY runners/typescript_batch.sh /typescript_batch.sh
COPY runners/TestRunner.ts /opt/TestRunner.ts
RUN chmod +x /runner.sh /typescript_batch.sh /framec_cached.sh
ENTRYPOINT ["/runner.sh"]
CMD ["typescript"]
