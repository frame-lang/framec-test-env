FROM eclipse-temurin:21-jdk
RUN mkdir -p /tests /output /lib && \
    apt-get update && apt-get install -y --no-install-recommends curl && \
    curl -sL "https://repo1.maven.org/maven2/org/json/json/20231013/json-20231013.jar" -o /lib/json.jar && \
    apt-get remove -y curl && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*
ARG RUNNER_HASH
COPY runners/runner.sh /runner.sh
COPY runners/framec_cached.sh /framec_cached.sh
COPY runners/java_batch.sh /java_batch.sh
COPY runners/TestRunner.java /tmp/TestRunner.java
RUN chmod +x /runner.sh /java_batch.sh /framec_cached.sh && \
    mkdir -p /opt/test_runner_build && \
    javac -d /opt/test_runner_build /tmp/TestRunner.java && \
    (cd /opt/test_runner_build && jar cf /opt/test_runner.jar TestRunner*.class) && \
    rm -rf /opt/test_runner_build /tmp/TestRunner.java
ENTRYPOINT ["/runner.sh"]
CMD ["java"]
