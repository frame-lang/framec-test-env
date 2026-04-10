FROM eclipse-temurin:21-jdk
RUN mkdir -p /tests /output /lib && \
    apt-get update && apt-get install -y --no-install-recommends curl && \
    curl -sL "https://repo1.maven.org/maven2/org/json/json/20231013/json-20231013.jar" -o /lib/json.jar && \
    apt-get remove -y curl && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*
ARG RUNNER_HASH
COPY runners/runner.sh /runner.sh
RUN chmod +x /runner.sh
ENTRYPOINT ["/runner.sh"]
CMD ["java"]
