FROM eclipse-temurin:21-jdk
RUN apt-get update && apt-get install -y --no-install-recommends curl unzip && \
    curl -sL "https://github.com/JetBrains/kotlin/releases/download/v2.1.0/kotlin-compiler-2.1.0.zip" -o /tmp/kotlin.zip && \
    unzip -q /tmp/kotlin.zip -d /opt && \
    ln -s /opt/kotlinc/bin/kotlinc /usr/local/bin/kotlinc && \
    ln -s /opt/kotlinc/bin/kotlin /usr/local/bin/kotlin && \
    rm /tmp/kotlin.zip && \
    mkdir -p /tests /output /lib && \
    curl -sL "https://repo1.maven.org/maven2/org/json/json/20231013/json-20231013.jar" -o /lib/json.jar && \
    apt-get remove -y curl && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*
ARG RUNNER_HASH
COPY runners/runner.sh /runner.sh
RUN chmod +x /runner.sh
ENTRYPOINT ["/runner.sh"]
CMD ["kotlin"]
