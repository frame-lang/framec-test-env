FROM node:20-slim
RUN npm install -g tsx typescript @types/node && \
    mkdir -p /tests /output /tmp/out
ARG RUNNER_HASH
COPY runners/runner.sh /runner.sh
RUN chmod +x /runner.sh
ENTRYPOINT ["/runner.sh"]
CMD ["typescript"]
