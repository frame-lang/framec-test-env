FROM node:20-slim
RUN npm install -g ts-node typescript @types/node && \
    mkdir -p /tests /output /tmp/out && \
    echo '{"compilerOptions":{"target":"ES2020","module":"CommonJS","esModuleInterop":true,"strict":false,"skipLibCheck":true,"types":["node"]}}' > /tmp/out/tsconfig.json
ARG RUNNER_HASH
COPY runners/runner.sh /runner.sh
RUN chmod +x /runner.sh
ENTRYPOINT ["/runner.sh"]
CMD ["typescript"]
